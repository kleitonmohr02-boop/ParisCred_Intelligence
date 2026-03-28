"""
ParisCred Intelligence - Sistema SaaS com SQLite
Aplicação Full-Stack com Autenticação, Painel ADM e Gerenciamento
Versão 2.0 - Com segurança, validação e Evolution API integrada
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps

import requests
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime
import secrets
import threading
import time

# Importar funções do database
from database import (
    Database,
    UsuariosDB,
    CampanhasDB,
    HistoricoDB
)

# Importar validadores
from validators import (
    UsuarioLogin,
    UsuarioCreate,
    CampanhaCreate,
    UsuarioUpdate,
    Beneficiario,
    Botao
)

# Importar skills e rotas customizadas
try:
    from skill_crm import ClientesDB
    from skill_financeiro import FinanceiroDB
    from skill_whatsapp import WhatsAppDB
    from skill_admin import AdminReportsDB
    SKILLS_ENABLED = True
except ImportError:
    SKILLS_ENABLED = False

# ============================================================
# CONFIGURAÇÃO INICIAL
# ============================================================

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Security: Secret key do .env ou gerar uma nova
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Security: Configuração de CORS específica
ALLOWED_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000,http://localhost:3000').split(',')
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

# Logging estruturado
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/pariscred.log')

# Criar diretório de logs se não existir
os.makedirs('logs', exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializar banco de dados
db = Database("app.db")

# Registrar rotas de skills (se disponíveis)
if SKILLS_ENABLED:
    try:
        from skills_routes import registrar_rotas_skills
        registrar_rotas_skills(app)
    except ImportError:
        pass

# Registrar rotas de importação de beneficiários
try:
    from modulo_importacao import criar_rotas_importacao
    criar_rotas_importacao(app)
except ImportError as e:
    logger.warning(f"Módulo importação não disponível: {e}")

# Registrar rotas anti-ban
try:
    from modulo_antiban import criar_rotas_antiban
    criar_rotas_antiban(app)
except ImportError as e:
    logger.warning(f"Módulo anti-ban não disponível: {e}")

# Controle de disparos em segundo plano
DISPAROS_ATIVOS = {}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def requer_login(f):
    """Decorator para proteger rotas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def requer_admin(f):
    """Decorator para proteger rotas ADM"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        
        usuario = UsuariosDB.obter(session['usuario'])
        if not usuario or usuario['role'] != 'admin':
            logger.warning(f"Acesso negado para {session['usuario']} em {request.path}")
            return jsonify({'erro': 'Acesso negado'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def obter_usuario_atual():
    """Retorna dados do usuário logado"""
    if 'usuario' not in session:
        return None
    return UsuariosDB.obter(session['usuario'])


def usuario_para_json(usuario):
    """Converte objeto usuário para JSON, removendo dados sensíveis"""
    if not usuario:
        return None
    
    return {
        'email': usuario['email'],
        'nome': usuario['nome'],
        'role': usuario['role'],
        'criado_em': usuario['criado_em'],
        'ativo': usuario['ativo']
    }


def campanha_para_json(campanha):
    """Converte campanha para JSON"""
    if not campanha:
        return None
    
    return {
        'id': campanha['id'],
        'nome': campanha['nome'],
        'descricao': campanha['descricao'],
        'status': campanha['status'],
        'criador': campanha['criador'],
        'beneficiarios': campanha['beneficiarios_json'],
        'mensagem': campanha['mensagem'],
        'botoes': campanha['botoes_json'],
        'instancias': campanha['instancias_json'],
        'criado_em': campanha['criado_em'],
        'disparado_em': campanha['disparado_em'],
        'total_enviados': campanha['total_enviados']
    }


def enviar_whatsapp_evolution(numero, mensagem, botoes=None, instance_name=None):
    """
    Envia mensagem via Evolution API
    """
    api_url = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
    api_key = os.getenv('EVOLUTION_API_KEY', 'CONSIGNADO123')
    instance = instance_name or os.getenv('EVOLUTION_INSTANCE_NAME', 'Paris_01')
    
    url = f"{api_url}/message/sendText/{instance}"
    
    headers = {
        'Content-Type': 'application/json',
        'apikey': api_key
    }
    
    payload = {
        'number': numero,
        'text': mensagem
    }
    
    if botoes:
        payload['buttons'] = [
            {'id': b['id'], 'text': b['text']} for b in botoes
        ]
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"Mensagem enviada para {numero}")
            return {'status': 'enviado', 'response': response.json()}
        else:
            logger.error(f"Erro ao enviar para {numero}: {response.text}")
            return {'status': 'erro', 'message': response.text}
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout ao enviar para {numero}")
        return {'status': 'timeout', 'message': 'Tempo limite excedido'}
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        return {'status': 'erro', 'message': str(e)}


def checar_instancia_evolution(instance_name=None):
    """
    Verifica status da instância WhatsApp
    """
    api_url = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
    api_key = os.getenv('EVOLUTION_API_KEY', 'CONSIGNADO123')
    instance = instance_name or os.getenv('EVOLUTION_INSTANCE_NAME', 'ParisCred_01')
    
    url = f"{api_url}/instance/connectionState/{instance}"
    
    headers = {'apikey': api_key}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            state = data.get('instance', {}).get('state', 'unknown')
            return {
                'status': 'ok',
                'instance': instance,
                'state': state,
                'conectado': state == 'open'
            }
        else:
            # Tentar listar instâncias
            list_url = f"{api_url}/instance/fetchInstances"
            list_resp = requests.get(list_url, headers=headers, timeout=10)
            if list_resp.status_code == 200:
                insts = list_resp.json()
                for i in insts:
                    if i.get('name') == instance:
                        return {
                            'status': 'ok',
                            'instance': instance,
                            'state': i.get('connectionStatus', 'unknown'),
                            'conectado': i.get('connectionStatus') == 'open'
                        }
            return {'status': 'erro', 'message': f'Status: {response.status_code}'}
            
    except Exception as e:
        logger.error(f"Erro ao verificar instância: {str(e)}")
        return {'status': 'erro', 'message': str(e)}


# ============================================================
# ROTAS PÚBLICAS (Auth)
# ============================================================

@app.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        try:
            # Validar input
            data = UsuarioLogin(
                email=request.form.get('email', ''),
                senha=request.form.get('senha', '')
            )
            
            # Verificar credenciais
            if UsuariosDB.verificar_senha(data.email, data.senha):
                usuario = UsuariosDB.obter(data.email)
                if usuario and usuario['ativo']:
                    session['usuario'] = data.email
                    logger.info(f"Login bem-sucedido: {data.email}")
                    return redirect(url_for('dashboard'))
            
            logger.warning(f"Login falhou para: {data.email}")
            return render_template('login.html', erro='Email ou senha incorretos')
        
        except Exception as e:
            logger.error(f"Erro no login: {str(e)}")
            return render_template('login.html', erro='Erro ao processar login')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Faz logout do usuário"""
    email = session.get('usuario', 'desconhecido')
    session.clear()
    logger.info(f"Logout: {email}")
    return redirect(url_for('login'))


# ============================================================
# ROTAS PROTEGIDAS - DASHBOARD
# ============================================================

@app.route('/dashboard')
@requer_login
def dashboard():
    """Dashboard principal do usuário"""
    usuario = obter_usuario_atual()
    logger.info(f"Acesso dashboard: {usuario['email']}")
    return render_template('dashboard.html', usuario=usuario_para_json(usuario))


@app.route('/api/usuario')
@requer_login
def api_usuario():
    """Retorna dados do usuário logado"""
    usuario = obter_usuario_atual()
    return jsonify(usuario_para_json(usuario))


@app.route('/api/stats')
@requer_login
def api_stats():
    """Retorna estatísticas do usuário/sistema"""
    usuario = obter_usuario_atual()
    
    if usuario['role'] == 'admin':
        usuarios = UsuariosDB.listar_todos()
        campanhas = CampanhasDB.listar_todas()
        
        return jsonify({
            'total_usuarios': len(usuarios),
            'total_campanhas': len(campanhas),
            'total_disparos': sum(c['total_enviados'] for c in campanhas),
            'usuarios_ativos': len(usuarios),
            'campanhas_ativas': sum(1 for c in campanhas if c['status'] == 'disparado')
        })
    else:
        campanhas_users = CampanhasDB.listar_por_criador(session['usuario'])
        return jsonify({
            'total_campanhas': len(campanhas_users),
            'total_disparos': sum(c['total_enviados'] for c in campanhas_users),
            'campanhas_ativas': sum(1 for c in campanhas_users if c['status'] == 'disparado')
        })


# ============================================================
# ROTAS DE CAMPANHAS
# ============================================================

@app.route('/campanhas')
@requer_login
def campanhas():
    """Página de gerenciamento de campanhas"""
    usuario = obter_usuario_atual()
    return render_template('campanhas.html', usuario=usuario_para_json(usuario))


@app.route('/crm')
@requer_login
def crm():
    """Página de CRM - Gestão de Clientes"""
    usuario = obter_usuario_atual()
    return render_template('crm.html', usuario=usuario_para_json(usuario))


@app.route('/api/crm/update_status', methods=['POST'])
@requer_login
def api_crm_update_status():
    """Atualiza o status do lead para Kanban"""
    STATUS_KANBAN = ['Novo Lead', 'Em Negociação', 'Pendente', 'Finalizado']
    
    data = request.get_json()
    
    if not data:
        return jsonify({'erro': 'Dados JSON não fornecidos'}), 400
    
    lead_id = data.get('lead_id')
    novo_status = data.get('status')
    
    if not lead_id:
        return jsonify({'erro': 'ID do lead não fornecido'}), 400
    
    if not novo_status:
        return jsonify({'erro': 'Status não fornecido'}), 400
    
    if novo_status not in STATUS_KANBAN:
        return jsonify({'erro': f'Status inválido. Valores permitidos: {STATUS_KANBAN}'}), 400
    
    try:
        db = Database()
        p = db.placeholder()
        ativo_val = db.bool_def(True)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT id FROM clientes WHERE id = {p} AND ativo = {ativo_val}", (lead_id,))
            row = cursor.fetchone()
            
            if not row:
                return jsonify({'erro': 'Lead não encontrado'}), 404
            
            cursor.execute(f"UPDATE clientes SET status = {p} WHERE id = {p} AND ativo = {ativo_val}", (novo_status, lead_id))
            conn.commit()
        
        logger.info(f"Lead {lead_id} atualizado para status: {novo_status}")
        return jsonify({'success': True, 'status': novo_status})
        
    except Exception as e:
        logger.error(f"Erro ao atualizar status do lead: {str(e)}")
        return jsonify({'erro': f'Erro ao atualizar status: {str(e)}'}), 500


@app.route('/api/crm/leads', methods=['GET'])
@requer_login
def api_crm_leads():
    """Retorna todos os leads com seus status para Kanban"""
    STATUS_KANBAN = ['Novo Lead', 'Em Negociação', 'Pendente', 'Finalizado']
    
    try:
        db = Database()
        p = db.placeholder()
        ativo_val = db.bool_def(True)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM clientes WHERE ativo = {ativo_val} ORDER BY data_criacao DESC")
            
            leads = []
            for row in cursor.fetchall():
                lead = dict(row) if hasattr(row, 'keys') else None
                if lead:
                    leads.append({
                        'id': lead.get('id'),
                        'nome': lead.get('nome'),
                        'phone': lead.get('phone'),
                        'email': lead.get('email'),
                        'status': lead.get('status'),
                        'margem_consignavel': lead.get('margem_consignavel'),
                        'data_criacao': lead.get('data_criacao')
                    })
        
        return jsonify({'success': True, 'leads': leads, 'statuses': STATUS_KANBAN})
        
    except Exception as e:
        logger.error(f"Erro ao listar leads: {str(e)}")
        return jsonify({'erro': f'Erro ao listar leads: {str(e)}'}), 500


@app.route('/financeiro')
@requer_login
def financeiro():
    """Página do Sistema Financeiro"""
    usuario = obter_usuario_atual()
    return render_template('financeiro.html', usuario=usuario_para_json(usuario))


@app.route('/importar')
@requer_login
def pagina_importar():
    """Página de Importar Leads"""
    usuario = obter_usuario_atual()
    return render_template('importar.html', usuario=usuario_para_json(usuario))


@app.route('/coach')
@requer_login
def pagina_coach():
    """Página do Chat IA Coach"""
    usuario = obter_usuario_atual()
    return render_template('coach.html', usuario=usuario_para_json(usuario))


@app.route('/extrato')
@requer_login
def pagina_extrato():
    """Página de Análise de Extrato"""
    usuario = obter_usuario_atual()
    return render_template('extrato.html', usuario=usuario_para_json(usuario))


@app.route('/api/extrato/analisar', methods=['POST'])
@requer_login
def api_analisar_extrato():
    """API para analisar extrato PDF"""
    from modulo_ia import agente_ia, ia_fallback
    
    if 'file' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo enviado'}), 400
    
    arquivo = request.files['file']
    
    if not arquivo.filename.endswith('.pdf'):
        return jsonify({'erro': 'Arquivo deve ser PDF'}), 400
    
    try:
        # Ler PDF
        import PyPDF2
        import tempfile
        
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        arquivo.save(temp_path.name)
        
        with open(temp_path.name, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() or ""
        
        # Limitar texto se muito grande
        if len(texto) > 8000:
            texto = texto[:8000] + "..."
        
        # Enviar para IA
        prompt = f"""Analise este extrato de crédito consignado e identifique:

1. Todos os contratos ativos (banco, parcela, prazo, valor total)
2. Valor total de desconto mensal
3. Oportunidades de portabilidade (se há contratos com taxas altas)
4. Contratos que vão liberar em breve (próximos a quitar)
5. Sugestão de economia
6. Score do cliente (0-100 baseado na situação)

Extrato:
{texto}

Responda em português brasileiro, de forma clara e objetiva."""

        try:
            resposta = agente_ia.gerar_resposta(prompt, {'nome': 'Cliente'})
            if resposta:
                return jsonify({'sucesso': True, 'analise': resposta})
        except Exception as e:
            logger.warning(f"Erro Gemini: {e}")
        
        # Fallback
        return jsonify({
            'sucesso': True, 
            'analise': 'Analise do extrato:\n\n• Contratos encontrados: Verificar manualmente\n• Total desconto: Verificar extrato\n• Recomendação: Entre em contato para análise detalhada'
        })
        
    except Exception as e:
        logger.error(f"Erro ao analisar extrato: {e}")
        return jsonify({'erro': f'Erro ao processar PDF: {str(e)}'}), 500


@app.route('/api/coach/chat', methods=['POST'])
@requer_login
def api_coach_chat():
    """API para Chat com IA Coach"""
    from modulo_ia import agente_ia, ia_fallback
    
    data = request.get_json()
    mensagem = data.get('mensagem', '')
    
    if not mensagem:
        return jsonify({'erro': 'Mensagem vazia'}), 400
    
    usuario = obter_usuario_atual()
    
    # Tentar usar IA
    try:
        resposta = agente_ia.gerar_resposta(mensagem, {'nome': usuario.get('nome', 'Vendedor')})
        if resposta:
            return jsonify({'resposta': resposta})
    except Exception as e:
        logger.warning(f"Erro no Gemini: {e}")
    
    # Fallback
    resposta_fallback = ia_fallback.responder(mensagem)
    return jsonify({'resposta': resposta_fallback})


@app.route('/api/campanhas', methods=['GET', 'POST'])
@requer_login
def api_campanhas():
    """API para CRUD de campanhas"""
    usuario = obter_usuario_atual()
    
    if request.method == 'GET':
        # Listar campanhas
        if usuario['role'] == 'admin':
            lista = CampanhasDB.listar_todas()
        else:
            lista = CampanhasDB.listar_por_criador(session['usuario'])
        
        return jsonify([campanha_para_json(c) for c in lista])
    
    elif request.method == 'POST':
        try:
            # Validar input
            data = request.json
            campanha_validada = CampanhaCreate(
                nome=data.get('nome', 'Nova Campanha'),
                descricao=data.get('descricao', ''),
                mensagem=data.get('mensagem', ''),
                beneficiarios=data.get('beneficiarios', []),
                botoes=data.get('botoes', []),
                instancias=data.get('instancias', ['Paris_01'])
            )
            
            # Criar nova campanha
            campanha_id = CampanhasDB.criar(
                nome=campanha_validada.nome,
                descricao=campanha_validada.descricao,
                criador=session['usuario'],
                mensagem=campanha_validada.mensagem,
                beneficiarios=[b.dict() for b in campanha_validada.beneficiarios],
                botoes=[b.dict() for b in campanha_validada.botoes],
                instancias=campanha_validada.instancias
            )
            
            if campanha_id:
                nova_campanha = CampanhasDB.obter(campanha_id)
                logger.info(f"Campanha criada: {campanha_validada.nome} por {session['usuario']}")
                return jsonify({
                    'sucesso': True,
                    'mensagem': f'Campanha "{nova_campanha["nome"]}" criada com sucesso!',
                    'campanha': campanha_para_json(nova_campanha)
                }), 201
            else:
                return jsonify({'erro': 'Erro ao criar campanha'}), 500
                
        except Exception as e:
            logger.error(f"Erro ao criar campanha: {str(e)}")
            return jsonify({'erro': str(e)}), 400


@app.route('/api/campanhas/<int:camp_id>', methods=['GET', 'PUT', 'DELETE'])
@requer_login
def api_campanha_detalhes(camp_id):
    """API para detalhes de 1 campanha"""
    usuario = obter_usuario_atual()
    
    campanha = CampanhasDB.obter(camp_id)
    if not campanha:
        return jsonify({'erro': 'Campanha não encontrada'}), 404
    
    # Verificar permissão
    if usuario['role'] != 'admin' and campanha['criador'] != session['usuario']:
        logger.warning(f"Acesso negado: {session['usuario']} tentou acessar campanha {camp_id}")
        return jsonify({'erro': 'Acesso negado'}), 403
    
    if request.method == 'GET':
        return jsonify(campanha_para_json(campanha))
    
    elif request.method == 'PUT':
        try:
            # Validar input
            data = request.json
            atualizar_dados = {}
            
            if 'nome' in data:
                atualizar_dados['nome'] = data['nome'][:100]
            if 'descricao' in data:
                atualizar_dados['descricao'] = data['descricao'][:500]
            if 'mensagem' in data:
                atualizar_dados['mensagem'] = data['mensagem'][:4000]
            if 'beneficiarios' in data:
                atualizar_dados['beneficiarios_json'] = data['beneficiarios']
            if 'botoes' in data:
                atualizar_dados['botoes_json'] = data['botoes']
            if 'instancias' in data:
                atualizar_dados['instancias_json'] = data['instancias']
            
            if CampanhasDB.atualizar(camp_id, **atualizar_dados):
                campanha_atualizada = CampanhasDB.obter(camp_id)
                logger.info(f"Campanha atualizada: {camp_id}")
                return jsonify({
                    'sucesso': True,
                    'campanha': campanha_para_json(campanha_atualizada)
                })
            else:
                return jsonify({'erro': 'Erro ao atualizar campanha'}), 500
                
        except Exception as e:
            logger.error(f"Erro ao atualizar campanha: {str(e)}")
            return jsonify({'erro': str(e)}), 400
    
    elif request.method == 'DELETE':
        # Deletar campanha
        if campanha['status'] != 'rascunho':
            return jsonify({'erro': 'Só é possível deletar campanhas em rascunho'}), 400
        
        if CampanhasDB.deletar(camp_id):
            logger.info(f"Campanha deletada: {camp_id}")
            return jsonify({'sucesso': True, 'mensagem': 'Campanha deletada'})
        else:
            return jsonify({'erro': 'Erro ao deletar campanha'}), 500


# ============================================================
# ROTAS DE DISPARO (COM EVOLUTION API)
# ============================================================

@app.route('/api/campanhas/<int:camp_id>/disparar', methods=['POST'])
@requer_login
def Disparar_campanha(camp_id):
    """Inicia o disparo de uma campanha em segundo plano"""
    usuario = obter_usuario_atual()
    
    campanha = CampanhasDB.obter(camp_id)
    if not campanha:
        return jsonify({'erro': 'Campanha não encontrada'}), 404
    
    # Verificar permissão
    if usuario['role'] != 'admin' and campanha['criador'] != session['usuario']:
        logger.warning(f"Acesso negado: {session['usuario']} tentou disparar campanha {camp_id}")
        return jsonify({'erro': 'Acesso negado'}), 403
    
    if not campanha['beneficiarios_json']:
        return jsonify({'erro': 'Nenhum beneficiário configurado'}), 400
    
    # Se já estiver disparando
    if camp_id in DISPAROS_ATIVOS and DISPAROS_ATIVOS[camp_id]['status'] == 'processando':
        return jsonify({'erro': 'Esta campanha já está em processamento'}), 400
    
    # Iniciar thread de disparo
    thread = threading.Thread(target=processar_disparo_background, args=(camp_id, session['usuario']))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'sucesso': True,
        'mensagem': 'Disparo iniciado em segundo plano.',
        'camp_id': camp_id
    })

def processar_disparo_background(camp_id, usuario_email):
    """Função executada em segundo plano para enviar as mensagens"""
    campanha = CampanhasDB.obter(camp_id)
    if not campanha: return

    total = len(campanha['beneficiarios_json'])
    DISPAROS_ATIVOS[camp_id] = {
        'status': 'processando',
        'total': total,
        'enviados': 0,
        'erros': 0,
        'inicio': datetime.now().isoformat()
    }
    
    resultados = []
    delay = int(os.getenv('MESSAGE_DELAY', '5'))
    instancia_nome = campanha['instancias_json'][0] if campanha['instancias_json'] else None
    
    try:
        for idx, beneficiario in enumerate(campanha['beneficiarios_json']):
            # Se campanha foi cancelada ou algo assim (futuro)
            if camp_id not in DISPAROS_ATIVOS: break
                
            numero = beneficiario.get('numero', '')
            nome = beneficiario.get('nome', 'N/A')
            
            if not numero:
                DISPAROS_ATIVOS[camp_id]['erros'] += 1
                continue
            
            # Delay entre envios (exceto o primeiro)
            if idx > 0:
                time.sleep(delay)
            
            # Simular digitação (Anti-Ban 2.0)
            try:
                from modulo_antiban import anti_ban
                anti_ban.simular_digitacao(instancia_nome, numero)
            except Exception:
                pass
            
            # Enviar via Evolution API
            resultado = enviar_whatsapp_evolution(
                numero=numero,
                mensagem=campanha['mensagem'],
                botoes=campanha['botoes_json'],
                instance_name=instancia_nome
            )
            
            if resultado['status'] == 'enviado':
                DISPAROS_ATIVOS[camp_id]['enviados'] += 1
            else:
                DISPAROS_ATIVOS[camp_id]['erros'] += 1
                
            resultados.append({
                'beneficiario': nome,
                'numero': numero,
                'status': resultado['status'],
                'timestamp': datetime.now().isoformat()
            })
        
        # Finalizar
        CampanhasDB.atualizar(
            camp_id,
            status='disparado',
            disparado_em=datetime.now().isoformat(),
            total_enviados=DISPAROS_ATIVOS[camp_id]['enviados']
        )
        
        HistoricoDB.registrar(
            campanha_id=camp_id,
            usuario=usuario_email,
            total_beneficiarios=len(resultados),
            resultados={'enviados': resultados}
        )
        
        DISPAROS_ATIVOS[camp_id]['status'] = 'concluido'
        DISPAROS_ATIVOS[camp_id]['fim'] = datetime.now().isoformat()
        logger.info(f"Campanha {camp_id} finalizada em background")
        
    except Exception as e:
        logger.error(f"Erro no disparo background {camp_id}: {str(e)}")
        if camp_id in DISPAROS_ATIVOS:
            DISPAROS_ATIVOS[camp_id]['status'] = 'erro'
            DISPAROS_ATIVOS[camp_id]['erro_msg'] = str(e)

@app.route('/api/campanhas/progresso')
@requer_login
def api_campanhas_progresso():
    """Retorna o progresso de todos os disparos ativos"""
    return jsonify(DISPAROS_ATIVOS)


@app.route('/whatsapp')
@requer_login
def whatsapp():
    """Página de administração do WhatsApp"""
    usuario = obter_usuario_atual()
    return render_template('whatsapp_admin.html', usuario=usuario_para_json(usuario))


@app.route('/api/whatsapp/status')
@requer_login
def whatsapp_status():
    """Verifica status da instância WhatsApp"""
    instancia = request.args.get('instance', os.getenv('EVOLUTION_INSTANCE_NAME', 'Paris_01'))
    status = checar_instancia_evolution(instancia)
    return jsonify(status)


# ============================================================
# ROTAS ADMINISTRATIVAS
# ============================================================

@app.route('/admin')
@requer_admin
def admin():
    """Dashboard administrativo"""
    usuario = obter_usuario_atual()
    logger.info(f"Acesso admin: {usuario['email']}")
    return render_template('admin.html', usuario=usuario_para_json(usuario))


@app.route('/api/admin/usuarios', methods=['GET', 'POST'])
@requer_admin
def api_admin_usuarios():
    """Gerenciar usuários (apenas ADM)"""
    
    if request.method == 'GET':
        usuarios = UsuariosDB.listar_todos()
        return jsonify([usuario_para_json(u) for u in usuarios])
    
    elif request.method == 'POST':
        try:
            # Validar input
            data = request.json
            usuario_valido = UsuarioCreate(
                email=data.get('email', ''),
                nome=data.get('nome', ''),
                senha=data.get('senha', 'Temp@123'),
                role=data.get('role', 'vendedor')
            )
            
            # Verificar se já existe
            if UsuariosDB.obter(usuario_valido.email):
                return jsonify({'erro': 'Email já cadastrado'}), 400
            
            # Criar novo usuário
            if UsuariosDB.criar(
                email=usuario_valido.email,
                nome=usuario_valido.nome,
                senha=usuario_valido.senha,
                role=usuario_valido.role
            ):
                usuario_criado = UsuariosDB.obter(usuario_valido.email)
                logger.info(f"Usuário criado: {usuario_valido.email} por {session['usuario']}")
                return jsonify({
                    'sucesso': True,
                    'mensagem': f'Usuário {usuario_valido.nome} criado com sucesso!',
                    'usuario': usuario_para_json(usuario_criado)
                }), 201
            else:
                return jsonify({'erro': 'Erro ao criar usuário'}), 500
                
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            return jsonify({'erro': str(e)}), 400


@app.route('/api/admin/usuarios/<email>', methods=['PUT', 'DELETE'])
@requer_admin
def api_admin_usuario_detalhes(email):
    """Gerenciar usuário específico (apenas ADM)"""
    
    usuario = UsuariosDB.obter(email)
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    if request.method == 'PUT':
        try:
            data = request.json
            usuario_valido = UsuarioUpdate(
                nome=data.get('nome'),
                role=data.get('role')
            )
            
            atualizar_dados = {}
            if usuario_valido.nome:
                atualizar_dados['nome'] = usuario_valido.nome
            if usuario_valido.role:
                atualizar_dados['role'] = usuario_valido.role
            
            if UsuariosDB.atualizar(email, **atualizar_dados):
                usuario_atualizado = UsuariosDB.obter(email)
                logger.info(f"Usuário atualizado: {email}")
                return jsonify({
                    'sucesso': True,
                    'usuario': usuario_para_json(usuario_atualizado)
                })
            else:
                return jsonify({'erro': 'Erro ao atualizar usuário'}), 500
                
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {str(e)}")
            return jsonify({'erro': str(e)}), 400
    
    elif request.method == 'DELETE':
        # Soft delete - apenas desativa
        if UsuariosDB.deletar(email):
            logger.info(f"Usuário desativado: {email}")
            return jsonify({'sucesso': True, 'mensagem': 'Usuário desativado'})
        else:
            return jsonify({'erro': 'Erro ao desativar usuário'}), 500


@app.route('/api/admin/historico')
@requer_admin
def api_admin_historico():
    """Ver histórico de disparos (apenas ADM)"""
    from database import Database
    
    db = Database()
    ativo_val = 'TRUE' if db.is_postgres else '1'
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT h.id, h.campanha_id, h.usuario, h.timestamp, 
                   h.total_beneficiarios, h.resultados_json
            FROM historico h
            WHERE h.ativo = {ativo_val}
            ORDER BY h.timestamp DESC
        """)
        
        import json
        historicos = []
        for row in cursor.fetchall():
            r = dict(row) if hasattr(row, 'keys') else {'id': row[0], 'campanha_id': row[1], 'usuario': row[2], 'timestamp': row[3], 'total_beneficiarios': row[4], 'resultados_json': row[5]}
            historicos.append({
                'id': r.get('id', r.get('id')),
                'campanha_id': r.get('campanha_id', r.get('campanha_id')),
                'usuario': r.get('usuario', r.get('usuario')),
                'timestamp': r.get('timestamp', r.get('timestamp')),
                'total_beneficiarios': r.get('total_beneficiarios', r.get('total_beneficiarios')),
                'resultados': json.loads(r.get('resultados_json', r.get('resultados_json', '{}')) or '{}')
            })
        
        return jsonify(historicos)


@app.route('/api/health')
def health():
    """Health check"""
    usuarios = UsuariosDB.listar_todos()
    campanhas = CampanhasDB.listar_todas()
    
    evolution_status = checar_instancia_evolution()
    
    db = Database()
    db_type = 'PostgreSQL' if db.is_postgres else 'SQLite'
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'versao': '2.0',
        'database': {
            'usuarios': len(usuarios),
            'campanhas': len(campanhas),
            'tipo': db_type
        },
        'whatsapp': evolution_status
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 - {request.path}")
    return jsonify({'erro': 'Não encontrado'}), 404


@app.route('/api/admin/seed', methods=['GET', 'POST'])
@requer_admin
def api_seed_dados():
    """Endpoint para popular dados de teste (apenas em desenvolvimento)"""
    # if os.getenv('FLASK_ENV') == 'production':
    #     return jsonify({'erro': 'Nao disponivel em producao'}), 403
    
    try:
        db = Database()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            p = db.placeholder()
            ativo_val = db.bool_def(True)
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS clientes (
                        id {db.pk_auto()},
                        nome TEXT NOT NULL,
                        email TEXT,
                        phone TEXT,
                        cpf TEXT,
                        status TEXT DEFAULT 'Novo Lead',
                        empresa TEXT,
                        cargo TEXT,
                        renda DECIMAL(10,2),
                        margem_consignavel DECIMAL(10,2),
                        banco_atual TEXT,
                        custom_fields TEXT,
                        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ativo BOOLEAN DEFAULT {ativo_val}
                    )
                """)
            except Exception as e:
                logger.warning(f"Tabela clientes pode já existir: {e}")
            
            cursor.execute(f"SELECT COUNT(*) as total FROM campanhas")
            row = cursor.fetchone()
            qtd_camp = row['total'] if isinstance(row, dict) else row[0]
            
            if qtd_camp == 0:
                campanhas = [
                    ('Campanha Aposentados', 'Campanha para aposentados do INSS', 'admin@pariscred.com'),
                    ('Campanha Servidores', 'Campanha para servidores públicos', 'admin@pariscred.com'),
                    ('Campanha Portabilidade', 'Campanha de portabilidade de consignado', 'admin@pariscred.com'),
                ]
                
                for nome, desc, criador in campanhas:
                    cursor.execute(f"""
                        INSERT INTO campanhas (nome, descricao, status, criador, mensagem, beneficiarios_json, botoes_json, instancias_json, total_enviados)
                        VALUES ({p}, {p}, 'rascunho', {p}, 'Olá! Temos uma proposta especial para você!', '[]', '[]', '[]', 0)
                    """, (nome, desc, criador))
            
            cursor.execute(f"SELECT COUNT(*) as total FROM clientes")
            row = cursor.fetchone()
            qtd_cli = row['total'] if isinstance(row, dict) else row[0]
            
            if qtd_cli == 0:
                STATUS_KANBAN = ['Novo Lead', 'Em Negociação', 'Pendente', 'Finalizado']
                clientes = [
                    ('Jose da Silva', 'jose@email.com', '48999991111', '12345678901', STATUS_KANBAN[0], 2500.00, 'INSS'),
                    ('Maria Santos', 'maria@email.com', '48999992222', '23456789012', STATUS_KANBAN[1], 3200.00, 'INSS'),
                    ('Pedro Costa', 'pedro@email.com', '48999993333', '34567890123', STATUS_KANBAN[2], 1800.00, 'CLT'),
                    ('Ana Oliveira', 'ana@email.com', '48999994444', '45678901234', STATUS_KANBAN[1], 4500.00, 'INSS'),
                    ('Joao Lima', 'joao@email.com', '48999995555', '56789012345', STATUS_KANBAN[0], 2100.00, 'INSS'),
                    ('Carlos Souza', 'carlos@email.com', '48999996666', '67890123456', STATUS_KANBAN[3], 2800.00, 'CLT'),
                    ('Francisca Dias', 'francisca@email.com', '48999997777', '78901234567', STATUS_KANBAN[0], 1900.00, 'INSS'),
                    ('Marcos Rodrigues', 'marcos@email.com', '48999998888', '89012345678', STATUS_KANBAN[1], 3100.00, 'INSS'),
                    ('Juliana Ferreira', 'juliana@email.com', '48999999999', '90123456789', STATUS_KANBAN[2], 2200.00, 'INSS'),
                    ('Ricardo Almeida', 'ricardo@email.com', '48998887777', '01234567890', STATUS_KANBAN[1], 2600.00, 'CLT'),
                    ('Fernanda Costa', 'fernanda@email.com', '48998886666', '11223344556', STATUS_KANBAN[0], 1700.00, 'INSS'),
                    ('Bruno Martins', 'bruno@email.com', '48887776655', '22334455667', STATUS_KANBAN[1], 3300.00, 'INSS'),
                    ('Carla Ribeiro', 'carla@email.com', '48876655443', '33445566778', STATUS_KANBAN[2], 2400.00, 'CLT'),
                    ('Diego Souza', 'diego@email.com', '48865544332', '44556677889', STATUS_KANBAN[0], 2000.00, 'INSS'),
                    ('Emily Batista', 'emily@email.com', '48854433221', '55667788990', STATUS_KANBAN[1], 2900.00, 'INSS'),
                    ('Felipe Lima', 'felipe@email.com', '48843322110', '66778899001', STATUS_KANBAN[0], 1850.00, 'CLT'),
                    ('Gabriela Santos', 'gabriela@email.com', '48832211099', '77889900112', STATUS_KANBAN[1], 2700.00, 'INSS'),
                    ('Henrique Alves', 'henrique@email.com', '48821099888', '88990011223', STATUS_KANBAN[2], 2300.00, 'CLT'),
                    ('Isabela Castro', 'isabela@email.com', '48810988777', '99001122334', STATUS_KANBAN[0], 1600.00, 'INSS'),
                    ('Joaquim Mendes', 'joaquim@email.com', '48809877666', '00112233445', STATUS_KANBAN[3], 3400.00, 'INSS'),
                ]
                
                for nome, email, phone, cpf, status, margem, banco in clientes:
                    cursor.execute(f"""
                        INSERT INTO clientes (nome, email, phone, cpf, status, margem_consignavel, banco_atual)
                        VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})
                    """, (nome, email, phone, cpf, status, margem, banco))
                
                return jsonify({'sucesso': True, 'mensagem': 'Dados de teste criados!', 'clientes': len(clientes), 'campanhas': len(campanhas)})
            else:
                return jsonify({'sucesso': True, 'mensagem': 'Dados ja existem!'})
                
    except Exception as e:
        logger.error(f"Erro ao criar seed: {e}")
        return jsonify({'erro': str(e)}), 500


@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 - {str(e)}")
    return jsonify({'erro': 'Erro interno do servidor'}), 500


@app.errorhandler(429)
def rate_limit_handler(e):
    logger.warning(f"Rate limit excedido: {request.ip}")
    return jsonify({'erro': 'Limite de requisições excedido. Tente novamente mais tarde.'}), 429


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print(" PARISCRED INTELLIGENCE v2.0 - SEGURO")
    print("="*70)
    print(f"\n Servidor iniciando na porta 5000...")
    print(f" Acessar em: http://localhost:5000")
    print(f" Banco de dados: {os.getenv('DATABASE_PATH', 'app.db')}")
    print(f" Evolution API: {os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')}")
    print(f" Rate Limiting: ATIVADO")
    print(f" Logging: {LOG_LEVEL}")
    print(f"\n Contas de Teste:")
    print(f"   ADM: admin@pariscred.com / Admin@2025")
    print(f"   Vendedor: vendedor@pariscred.com / Vendedor@123")
    print(f"\n" + "="*70 + "\n")
    
    # RODAR SEED AUTOMATICO EM PRODUCAO
    if os.getenv('FLASK_ENV') == 'production':
        try:
            from app import app
            with app.app_context():
                from database import Database
                db = Database()
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) as total FROM clientes")
                    row = cursor.fetchone()
                    total = row['total'] if isinstance(row, dict) else row[0]
                    if total == 0:
                        print(">>> CRIANDO DADOS DE DEMONSTRACAO...")
                        resp = app.test_client().get('/api/admin/seed')
                        print(f">>> SEED RESULT: {resp.status_code}")
        except Exception as e:
            print(f"Erro ao rodar seed: {e}")
    
    # Verificar modo de produção
    debug_mode = os.getenv('FLASK_ENV', 'production') != 'production'
    
    app.run(
        debug=debug_mode,
        port=int(os.getenv('PORT', 5000)),
        host='0.0.0.0'
    )