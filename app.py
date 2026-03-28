"""
ParisCred Intelligence - Sistema SaaS Completo
Aplicação Full-Stack com Autenticação, Painel ADM e Gerenciamento
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import requests
import json
from datetime import datetime
import secrets
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "CONSIGNADO123")
EVOLUTION_HEADERS = {
    "Content-Type": "application/json",
    "apikey": EVOLUTION_API_KEY
}

try:
    from database import Database, UsuariosDB, CampanhasDB, HistoricoDB
    logger.info("[OK] Banco de dados integrado")
    USANDO_BANCO = True
except Exception as e:
    logger.error(f"[ERRO] Banco de dados NAO importado: {e}")
    USANDO_BANCO = False

USUARIOS = {
    'admin@pariscred.com': {
        'senha': 'Admin@2025',
        'nome': 'Administrador ParisCred',
        'role': 'admin',
        'criado_em': '2025-01-01',
        'ativo': True
    },
    'vendedor1@pariscred.com': {
        'senha': 'Vendedor@123',
        'nome': 'João Vendedor',
        'role': 'vendedor',
        'criado_em': '2025-01-15',
        'ativo': True
    }
}

# Campanhas criadas
CAMPANHAS = {
    'camp001': {
        'id': 'camp001',
        'nome': 'Campanha Inicial',
        'descricao': 'Primeira campanha de teste',
        'status': 'rascunho',
        'criador': 'admin@pariscred.com',
        'beneficiarios': [
            {'numero': '5548991105801', 'nome': 'Kleiton'},
            {'numero': '5548996057792', 'nome': 'Kleber Mohr'}
        ],
        'mensagem': 'Olá! Você tem uma ótima notícia!',
        'botoes': [
            {'id': '1', 'text': '💸 Ver meu Troco (Port)'},
            {'id': '2', 'text': '💰 Dinheiro Novo'}
        ],
        'instancias': ['Paris_01', 'Chip01', 'Chip02'],
        'criado_em': '2025-03-17',
        'disparado_em': None,
        'total_enviados': 0
    }
}

# Histórico de disparos
HISTORICO = []

# WhatsApp Instâncias (conectadas)
WHATSAPP_INSTANCIAS = {
    'Paris_01': {
        'nome': 'Paris_01',
        'numero': '+5548991105801',
        'status': 'desconectado',
        'conectado_em': None,
        'respondendo': False
    },
    'Chip01': {
        'nome': 'Chip01',
        'numero': '+5548996057792',
        'status': 'desconectado',
        'conectado_em': None,
        'respondendo': False
    },
    'Chip02': {
        'nome': 'Chip02',
        'numero': None,
        'status': 'desconectado',
        'conectado_em': None,
        'respondendo': False
    }
}

# Leads qualificados (chegam de agente virtual)
LEADS = {
    'lead001': {
        'id': 'lead001',
        'numero': '5548991234567',
        'nome': 'Cliente Premium',
        'mensagem': 'Olá! Gostaria de saber mais sobre o Troco.',
        'timestamp': '2025-03-17T10:30:00',
        'status': 'pendente',  # pendente, atendido, resolvido
        'atendido_por': None,
        'campanha': 'camp001',
        'qualificacao': 'alta'
    },
    'lead002': {
        'id': 'lead002',
        'numero': '5548991654321',
        'nome': 'Prospect Novo',
        'mensagem': 'Tenho interesse no Dinheiro Novo',
        'timestamp': '2025-03-17T11:45:00',
        'status': 'pendente',
        'atendido_por': None,
        'campanha': 'camp001',
        'qualificacao': 'media'
    },
    'lead003': {
        'id': 'lead003',
        'numero': '5548999876543',
        'nome': 'Cliente Recorrente',
        'mensagem': 'Qual o prazo para aprovação?',
        'timestamp': '2025-03-17T12:15:00',
        'status': 'atendido',
        'atendido_por': 'vendedor1@pariscred.com',
        'campanha': 'camp001',
        'qualificacao': 'alta'
    }
}

# Conversa com leads (histórico de mensagens)
CONVERSAS_LEADS = {
    'lead001': [],
    'lead002': [],
    'lead003': [
        {
            'direção': 'entrada',
            'mensagem': 'Qual o prazo para aprovação?',
            'timestamp': '2025-03-17T12:15:00'
        },
        {
            'direção': 'saída',
            'mensagem': 'Olá! O prazo é de 2 a 3 dias úteis. Posso ajudá-lo?',
            'timestamp': '2025-03-17T12:16:00',
            'vendedor': 'vendedor1@pariscred.com'
        }
    ]
}

# ============================================================
# HELPER FUNCTIONS - EVOLUTION API
# ============================================================

def evolution_criar_instancia(nome_instancia):
    """Criar nova instância WhatsApp na Evolution API"""
    try:
        url = f"{EVOLUTION_API_URL}/instance/create"
        payload = {"instanceName": nome_instancia}
        
        response = requests.post(url, json=payload, headers=EVOLUTION_HEADERS, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Erro ao criar instância Evolution: {e}")
        return None

def evolution_listar_instancias():
    """Listar todas as instâncias da Evolution API"""
    try:
        url = f"{EVOLUTION_API_URL}/instance/fetchInstances"
        response = requests.get(url, headers=EVOLUTION_HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            instancias = data.get('value', [])
            
            # Garantir que instancias é uma lista
            if not isinstance(instancias, list):
                instancias = [instancias] if instancias else []
            
            # Converter para formato padrão
            resultado = []
            for inst in instancias:
                # Verificar se é um dict e não uma lista
                if isinstance(inst, dict):
                    resultado.append({
                        'instance': {
                            'instanceName': inst.get('name', 'N/A'),
                            'instanceStatus': 'open' if inst.get('connectionStatus') == 'open' else 'close'
                        },
                        'contact': {
                            'id': inst.get('number') or 'não conectado'
                        }
                    })
            return resultado
        return []
    except Exception as e:
        print(f"❌ Erro ao listar instâncias Evolution: {e}")
        return []

def evolution_obter_qrcode(nome_instancia):
    """Obter QR Code da instância"""
    try:
        # Endpoint correto da Evolution API para obter QR Code
        url = f"{EVOLUTION_API_URL}/instance/qrcode/{nome_instancia}"
        response = requests.get(url, headers=EVOLUTION_HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Retorna o QR Code em base64 ou URL
            return data.get('qrcode') or data.get('base64') or data.get('imageUrl')
        return None
    except Exception as e:
        print(f"❌ Erro ao obter QR Code: {e}")
        return None

def evolution_conectar_instancia(nome_instancia):
    """Conectar instância para obter QR Code"""
    try:
        # Endpoint para conectar e gerar QR Code
        url = f"{EVOLUTION_API_URL}/instance/connect"
        payload = {"instanceName": nome_instancia}
        
        response = requests.post(url, json=payload, headers=EVOLUTION_HEADERS, timeout=10)
        
        if response.status_code in [200, 201]:
            return response.json()
        
        # Se falhar, tenta apenas obter QR Code
        qr = evolution_obter_qrcode(nome_instancia)
        return {'qrcode': qr} if qr else None
    except Exception as e:
        print(f"❌ Erro ao conectar instância: {e}")
        return None

def evolution_desconectar_instancia(nome_instancia):
    """Desconectar instância"""
    try:
        url = f"{EVOLUTION_API_URL}/instance/logout"
        payload = {"instanceName": nome_instancia}
        
        response = requests.post(url, json=payload, headers=EVOLUTION_HEADERS, timeout=10)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ Erro ao desconectar instância: {e}")
        return False

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
        
        usuario = USUARIOS.get(session['usuario'])
        if not usuario or usuario['role'] != 'admin':
            return jsonify({'erro': 'Acesso negado'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def requer_admin_api(f):
    """Decorator para proteger APIs de administrador (retorna JSON)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return jsonify({'erro': 'Não autenticado'}), 401
        
        usuario = USUARIOS.get(session['usuario'])
        if not usuario or usuario['role'] != 'admin':
            return jsonify({'erro': 'Acesso negado'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def obter_usuario_atual():
    """Retorna dados do usuário logado"""
    if 'usuario' not in session:
        return None
    
    email = session['usuario']
    
    if USANDO_BANCO:
        try:
            usuario = UsuariosDB.obter(email)
            if usuario:
                return {
                    'email': usuario['email'],
                    'nome': usuario['nome'],
                    'role': usuario['role'],
                    'criado_em': usuario['criado_em'],
                    'ativo': usuario['ativo']
                }
        except Exception as e:
            logger.error(f"[USUARIO] Erro ao buscar do banco: {e}")
    
    return USUARIOS.get(email)

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
        email = request.form.get('email', '').lower()
        senha = request.form.get('senha', '')
        
        if USANDO_BANCO:
            try:
                if UsuariosDB.verificar_senha(email, senha):
                    usuario = UsuariosDB.obter(email)
                    if usuario and usuario.get('ativo'):
                        session['usuario'] = email
                        logger.info(f"[LOGIN] Usuario {email} logado com sucesso (BD)")
                        return redirect(url_for('dashboard'))
            except Exception as e:
                logger.error(f"[LOGIN] Erro ao verificar usuario no banco: {e}")
        
        usuario = USUARIOS.get(email)
        if usuario and usuario['senha'] == senha and usuario['ativo']:
            session['usuario'] = email
            logger.info(f"[LOGIN] Usuario {email} logado (modo demonstração)")
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', erro='Email ou senha incorretos')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Faz logout do usuário"""
    session.clear()
    return redirect(url_for('login'))

# ============================================================
# ROTAS PROTEGIDAS - DASHBOARD
# ============================================================

@app.route('/dashboard')
@requer_login
def dashboard():
    """Dashboard principal do usuário"""
    usuario = obter_usuario_atual()
    return render_template('dashboard.html', usuario=usuario)

@app.route('/api/usuario')
@requer_login
def api_usuario():
    """Retorna dados do usuário logado"""
    usuario = obter_usuario_atual()
    return jsonify({
        'email': session['usuario'],
        'nome': usuario['nome'],
        'role': usuario['role'],
        'criado_em': usuario['criado_em']
    })

@app.route('/api/stats')
@requer_login
def api_stats():
    """Retorna estatísticas do usuário/sistema"""
    usuario = obter_usuario_atual()
    
    if USANDO_BANCO:
        try:
            if usuario['role'] == 'admin':
                usuarios = UsuariosDB.listar_todos()
                campanhas = CampanhasDB.listar_todas()
                return jsonify({
                    'total_usuarios': len(usuarios),
                    'total_campanhas': len(campanhas),
                    'total_disparos': 0,
                    'usuarios_ativos': sum(1 for u in usuarios if u.get('ativo', True)),
                    'campanhas_ativas': sum(1 for c in campanhas if c.get('status') == 'ativo')
                })
            else:
                campanhas = CampanhasDB.listar_por_criador(session['usuario'])
                return jsonify({
                    'total_campanhas': len(campanhas),
                    'total_disparos': sum(c.get('total_enviados', 0) for c in campanhas),
                    'campanhas_ativas': sum(1 for c in campanhas if c.get('status') == 'ativo')
                })
        except Exception as e:
            logger.error(f"[STATS] Erro ao buscar stats: {e}")
    
    if usuario['role'] == 'admin':
        return jsonify({
            'total_usuarios': len(USUARIOS),
            'total_campanhas': len(CAMPANHAS),
            'total_disparos': len(HISTORICO),
            'usuarios_ativos': sum(1 for u in USUARIOS.values() if u['ativo']),
            'campanhas_ativas': sum(1 for c in CAMPANHAS.values() if c['status'] == 'ativo')
        })
    else:
        campanhas_users = [c for c in CAMPANHAS.values() if c['criador'] == session['usuario']]
        return jsonify({
            'total_campanhas': len(campanhas_users),
            'total_disparos': sum(c['total_enviados'] for c in campanhas_users),
            'campanhas_ativas': sum(1 for c in campanhas_users if c['status'] == 'ativo')
        })

# ============================================================
# ROTAS DE CAMPANHAS
# ============================================================

@app.route('/campanhas')
@requer_login
def campanhas():
    """Página de gerenciamento de campanhas"""
    usuario = obter_usuario_atual()
    return render_template('campanhas.html', usuario=usuario)

@app.route('/api/campanhas', methods=['GET', 'POST'])
@requer_login
def api_campanhas():
    """API para CRUD de campanhas"""
    usuario = obter_usuario_atual()
    
    if request.method == 'GET':
        lista = []
        
        if USANDO_BANCO:
            try:
                if usuario['role'] == 'admin':
                    campanhas = CampanhasDB.listar_todas()
                else:
                    campanhas = CampanhasDB.listar_por_criador(session['usuario'])
                
                for c in campanhas:
                    lista.append({
                        'id': c['id'],
                        'nome': c['nome'],
                        'descricao': c['descricao'],
                        'status': c['status'],
                        'criador': c['criador'],
                        'beneficiarios': c.get('beneficiarios_json', []),
                        'mensagem': c['mensagem'],
                        'botoes': c.get('botoes_json', []),
                        'instancias': c.get('instancias_json', []),
                        'criado_em': c['criado_em'],
                        'disparado_em': c.get('disparado_em'),
                        'total_enviados': c.get('total_enviados', 0)
                    })
            except Exception as e:
                logger.error(f"[CAMPANHAS] Erro ao buscar do banco: {e}")
        
        if not lista:
            if usuario['role'] == 'admin':
                lista = list(CAMPANHAS.values())
            else:
                lista = [c for c in CAMPANHAS.values() if c['criador'] == session['usuario']]
        
        return jsonify(lista)
    
    elif request.method == 'POST':
        data = request.json
        
        if USANDO_BANCO:
            try:
                camp_id = CampanhasDB.criar(
                    nome=data.get('nome', 'Nova Campanha'),
                    descricao=data.get('descricao', ''),
                    criador=session['usuario'],
                    mensagem=data.get('mensagem', ''),
                    beneficiarios=data.get('beneficiarios', []),
                    botoes=data.get('botoes', []),
                    instancias=data.get('instancias', ['Paris_01'])
                )
                
                campanha = CampanhasDB.obter(camp_id)
                logger.info(f"[CAMPANHA] Criada via BD: {camp_id}")
                
                return jsonify({
                    'sucesso': True,
                    'mensagem': f'Campanha "{data.get("nome")}" criada com sucesso!',
                    'campanha': {
                        'id': camp_id,
                        'nome': data.get('nome'),
                        'status': 'rascunho',
                        'criador': session['usuario']
                    }
                }), 201
            except Exception as e:
                logger.error(f"[CAMPANHA] Erro ao criar no banco: {e}")
        
        camp_id = f"camp{len(CAMPANHAS) + 1:03d}"
        
        nova_campanha = {
            'id': camp_id,
            'nome': data.get('nome', 'Nova Campanha'),
            'descricao': data.get('descricao', ''),
            'status': 'rascunho',
            'criador': session['usuario'],
            'beneficiarios': data.get('beneficiarios', []),
            'mensagem': data.get('mensagem', ''),
            'botoes': data.get('botoes', []),
            'instancias': data.get('instancias', ['Paris_01']),
            'criado_em': datetime.now().isoformat(),
            'disparado_em': None,
            'total_enviados': 0
        }
        
        CAMPANHAS[camp_id] = nova_campanha
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Campanha "{nova_campanha["nome"]}" criada com sucesso!',
            'campanha': nova_campanha
        }), 201

@app.route('/api/campanhas/<camp_id>', methods=['GET', 'PUT', 'DELETE'])
@requer_login
def api_campanha_detalhes(camp_id):
    """API para detalhes de 1 campanha"""
    usuario = obter_usuario_atual()
    
    campanha = CAMPANHAS.get(camp_id)
    if not campanha:
        return jsonify({'erro': 'Campanha não encontrada'}), 404
    
    # Verificar permissão
    if usuario['role'] != 'admin' and campanha['criador'] != session['usuario']:
        return jsonify({'erro': 'Acesso negado'}), 403
    
    if request.method == 'GET':
        return jsonify(campanha)
    
    elif request.method == 'PUT':
        # Atualizar campanha
        data = request.json
        campanha.update({
            'nome': data.get('nome', campanha['nome']),
            'descricao': data.get('descricao', campanha['descricao']),
            'beneficiarios': data.get('beneficiarios', campanha['beneficiarios']),
            'mensagem': data.get('mensagem', campanha['mensagem']),
            'botoes': data.get('botoes', campanha['botoes']),
            'instancias': data.get('instancias', campanha['instancias'])
        })
        
        return jsonify({'sucesso': True, 'campanha': campanha})
    
    elif request.method == 'DELETE':
        # Deletar campanha
        if campanha['status'] != 'rascunho':
            return jsonify({'erro': 'Só é possível deletar campanhas em rascunho'}), 400
        
        del CAMPANHAS[camp_id]
        return jsonify({'sucesso': True, 'mensagem': 'Campanha deletada'})

# ============================================================
# ROTAS DE DISPARO
# ============================================================

@app.route('/api/campanhas/<camp_id>/disparar', methods=['POST'])
@requer_login
def disparar_campanha(camp_id):
    """Dispara uma campanha"""
    usuario = obter_usuario_atual()
    
    campanha = CAMPANHAS.get(camp_id)
    if not campanha:
        return jsonify({'erro': 'Campanha não encontrada'}), 404
    
    # Verificar permissão
    if usuario['role'] != 'admin' and campanha['criador'] != session['usuario']:
        return jsonify({'erro': 'Acesso negado'}), 403
    
    if not campanha['beneficiarios']:
        return jsonify({'erro': 'Nenhum beneficiário configurado'}), 400
    
    # Simular disparo (em produção, conectaria com Evolution API)
    resultados = []
    
    try:
        for idx, beneficiario in enumerate(campanha['beneficiarios']):
            # Aqui entra a lógica real de envio via Evolution API
            resultados.append({
                'beneficiario': beneficiario['nome'],
                'numero': beneficiario['numero'],
                'status': 'enviado',
                'timestamp': datetime.now().isoformat()
            })
        
        # Atualizar campanha
        campanha['status'] = 'disparado'
        campanha['disparado_em'] = datetime.now().isoformat()
        campanha['total_enviados'] = len(resultados)
        
        # Registrar no histórico
        HISTORICO.append({
            'campanha_id': camp_id,
            'usuario': session['usuario'],
            'timestamp': datetime.now().isoformat(),
            'total_beneficiarios': len(resultados),
            'resultados': resultados
        })
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'{len(resultados)} mensagens disparadas com sucesso!',
            'resultados': resultados
        })
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ============================================================
# ROTAS ADMINISTRATIVAS
# ============================================================

@app.route('/admin')
@requer_admin
def admin():
    """Dashboard administrativo"""
    usuario = obter_usuario_atual()
    return render_template('admin.html', usuario=usuario)

@app.route('/api/admin/usuarios', methods=['GET', 'POST'])
@requer_admin
def api_admin_usuarios():
    """Gerenciar usuários (apenas ADM)"""
    
    if request.method == 'GET':
        usuarios = []
        
        if USANDO_BANCO:
            try:
                for u in UsuariosDB.listar_todos():
                    usuarios.append({
                        'email': u['email'],
                        'nome': u['nome'],
                        'role': u['role'],
                        'ativo': u['ativo'],
                        'criado_em': u['criado_em']
                    })
            except Exception as e:
                logger.error(f"[ADMIN USUARIOS] Erro ao buscar usuarios: {e}")
        
        if not usuarios:
            for email, dados in USUARIOS.items():
                usuarios.append({
                    'email': email,
                    'nome': dados['nome'],
                    'role': dados['role'],
                    'ativo': dados['ativo'],
                    'criado_em': dados['criado_em']
                })
        
        return jsonify(usuarios)
    
    elif request.method == 'POST':
        data = request.json
        email = data.get('email', '').lower()
        
        if USANDO_BANCO:
            try:
                sucesso = UsuariosDB.criar(
                    email=email,
                    nome=data.get('nome', 'Novo Usuário'),
                    senha=data.get('senha', 'Temp@123'),
                    role=data.get('role', 'vendedor')
                )
                if sucesso:
                    logger.info(f"[ADMIN] Usuario criado: {email}")
                    return jsonify({
                        'sucesso': True,
                        'mensagem': f'Usuário {data.get("nome")} criado com sucesso!',
                        'usuario': {'email': email, 'nome': data.get('nome'), 'role': data.get('role', 'vendedor')}
                    }), 201
                return jsonify({'erro': 'Erro ao criar usuário'}), 500
            except Exception as e:
                logger.error(f"[ADMIN] Erro ao criar usuario: {e}")
                return jsonify({'erro': str(e)}), 500
        
        if email in USUARIOS:
            return jsonify({'erro': 'Email já cadastrado'}), 400
        
        USUARIOS[email] = {
            'senha': data.get('senha', 'Temp@123'),
            'nome': data.get('nome', 'Novo Usuário'),
            'role': data.get('role', 'vendedor'),
            'criado_em': datetime.now().isoformat(),
            'ativo': True
        }
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Usuário {data.get("nome")} criado com sucesso!',
            'usuario': {
                'email': email,
                'nome': USUARIOS[email]['nome'],
                'role': USUARIOS[email]['role']
            }
        }), 201

@app.route('/api/admin/usuarios/<email>', methods=['PUT', 'DELETE'])
@requer_admin
def api_admin_usuario_detalhes(email):
    """Gerenciar usuário específico (apenas ADM)"""
    
    usuario = USUARIOS.get(email)
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    if request.method == 'PUT':
        data = request.json
        usuario.update({
            'nome': data.get('nome', usuario['nome']),
            'role': data.get('role', usuario['role']),
            'ativo': data.get('ativo', usuario['ativo'])
        })
        
        return jsonify({'sucesso': True, 'usuario': {
            'email': email,
            'nome': usuario['nome'],
            'role': usuario['role'],
            'ativo': usuario['ativo']
        }})
    
    elif request.method == 'DELETE':
        # Não deleta, apenas desativa
        usuario['ativo'] = False
        return jsonify({'sucesso': True, 'mensagem': 'Usuário desativado'})

@app.route('/api/admin/historico')
@requer_admin
def api_admin_historico():
    """Ver histórico de disparos (apenas ADM)"""
    return jsonify(HISTORICO)

# ============================================================
# ROTAS DE GERENCIAMENTO WHATSAPP (ADMIN)
# ============================================================

@app.route('/admin/whatsapp')
@requer_login
def admin_whatsapp():
    """Painel de gerenciamento de WhatsApp para admin"""
    usuario = obter_usuario_atual()
    
    # Verificar se é admin
    if usuario['role'] != 'admin':
        return redirect(url_for('dashboard'))
    
    return render_template('whatsapp_admin_real.html', 
                         usuario=usuario)

@app.route('/api/whatsapp/instancias')
@requer_admin_api
def api_whatsapp_instancias():
    """Listar todas as instâncias WhatsApp da Evolution API"""
    instancias_evolution = evolution_listar_instancias()
    
    # Se conseguiu da Evolution, retorna
    if instancias_evolution:
        return jsonify(instancias_evolution)
    
    # Fallback: retorna nossas instâncias simuladas
    instancias_list = []
    for nome, dados in WHATSAPP_INSTANCIAS.items():
        instancias_list.append({
            'instance': {
                'instanceName': nome,
                'instanceStatus': dados['status']
            },
            'contact': {
                'id': dados['numero'] or 'não conectado'
            }
        })
    return jsonify(instancias_list)

@app.route('/api/whatsapp/conectar', methods=['POST'])
@requer_admin_api
def api_whatsapp_conectar():
    """Conectar novo número WhatsApp"""
    data = request.json or {}
    instancia_nome = data.get('instancia_nome')
    numero = data.get('numero')
    
    if not instancia_nome or instancia_nome not in WHATSAPP_INSTANCIAS:
        return jsonify({'erro': 'Instância não encontrada'}), 400
    
    if not numero:
        return jsonify({'erro': 'Número é obrigatório'}), 400
    
    # Atualizar instância
    WHATSAPP_INSTANCIAS[instancia_nome]['numero'] = numero
    WHATSAPP_INSTANCIAS[instancia_nome]['status'] = 'conectando'
    
    return jsonify({
        'sucesso': True,
        'mensagem': f'Conectando {instancia_nome}...',
        'instancia': instancia_nome
    })

@app.route('/api/whatsapp/conectar-numero', methods=['POST'])
@requer_admin_api
def api_whatsapp_conectar_numero():
    """Conectar via número WhatsApp direto"""
    data = request.json or {}
    instancia_nome = data.get('instancia_nome')
    numero = data.get('numero')
    
    if not instancia_nome or instancia_nome not in WHATSAPP_INSTANCIAS:
        return jsonify({'erro': 'Instância não encontrada'}), 400
    
    if not numero:
        return jsonify({'erro': 'Número é obrigatório'}), 400
    
    # Limpar número (remover caracteres especiais)
    numero_limpo = ''.join(c for c in numero if c.isdigit())
    
    if len(numero_limpo) < 10:
        return jsonify({'erro': 'Número WhatsApp inválido'}), 400
    
    # Gerar código de confirmação único
    import random
    codigo_confirmacao = str(random.randint(100000, 999999))
    
    # Armazenar informação de conexão pendente
    if not hasattr(api, 'conexoes_pendentes'):
        api.conexoes_pendentes = {}
    
    api.conexoes_pendentes[numero_limpo] = {
        'instancia': instancia_nome,
        'codigo': codigo_confirmacao,
        'timestamp': datetime.now().isoformat(),
        'confirmado': False
    }
    
    # Atualizar status da instância
    WHATSAPP_INSTANCIAS[instancia_nome]['numero'] = numero_limpo
    WHATSAPP_INSTANCIAS[instancia_nome]['status'] = 'aguardando_confirmacao'
    
    # Simular envio de notificação/mensagem (em produção, enviaria via Evolution API)
    print(f"📱 [SIMULADO] Notificação enviada para WhatsApp: {numero_limpo}")
    print(f"   Código de confirmação: {codigo_confirmacao}")
    
    return jsonify({
        'sucesso': True,
        'mensagem': f'✓ Notificação enviada para {numero_limpo}. Aguardando confirmação no telefone...',
        'numero': numero_limpo,
        'instancia': instancia_nome,
        'aguardando_confirmacao': True,
        'codigo_confirmacao': codigo_confirmacao
    })

@app.route('/api/whatsapp/gerar-codigo', methods=['POST'])
@requer_admin_api
def api_whatsapp_gerar_codigo():
    """Gerar código de autenticação para conectar WhatsApp"""
    data = request.json or {}
    instancia_nome = data.get('instancia_nome')
    
    if not instancia_nome or instancia_nome not in WHATSAPP_INSTANCIAS:
        return jsonify({'erro': 'Instância não encontrada'}), 400
    
    # Gerar código de 6 dígitos
    import random
    codigo = str(random.randint(100000, 999999))
    
    # Armazenar o código associado à instância (com timestamp)
    if not hasattr(api, 'codigos_gerados'):
        api.codigos_gerados = {}
    
    api.codigos_gerados[codigo] = {
        'instancia': instancia_nome,
        'timestamp': datetime.now().isoformat(),
        'validado': False
    }
    
    # Atualizar status da instância
    WHATSAPP_INSTANCIAS[instancia_nome]['status'] = 'aguardando_codigo'
    
    return jsonify({
        'sucesso': True,
        'codigo': codigo,
        'instancia': instancia_nome,
        'mensagem': f'Código {codigo} gerado para {instancia_nome}. Cole no WhatsApp em "Não consegue escanear?"'
    })

@app.route('/api/whatsapp/validar-codigo/<codigo>', methods=['POST'])
@requer_admin_api
def api_whatsapp_validar_codigo(codigo):
    """Validar código de autenticação (chamado pelo WhatsApp)"""
    if not hasattr(api, 'codigos_gerados') or codigo not in api.codigos_gerados:
        return jsonify({'erro': 'Código não encontrado ou expirado'}), 404
    
    info_codigo = api.codigos_gerados[codigo]
    instancia_nome = info_codigo['instancia']
    
    # Validar se código é recente (menos de 2 minutos)
    tempo_gerado = datetime.fromisoformat(info_codigo['timestamp'])
    idade_codigo = (datetime.now() - tempo_gerado).total_seconds()
    
    if idade_codigo > 120:  # 2 minutos
        return jsonify({'erro': 'Código expirado'}), 400
    
    # Marcar instância como conectada
    WHATSAPP_INSTANCIAS[instancia_nome]['status'] = 'conectado'
    WHATSAPP_INSTANCIAS[instancia_nome]['conectado_em'] = datetime.now().isoformat()
    WHATSAPP_INSTANCIAS[instancia_nome]['respondendo'] = True
    info_codigo['validado'] = True
    
    return jsonify({
        'sucesso': True,
        'mensagem': f'✓ {instancia_nome} conectado com sucesso!',
        'instancia': instancia_nome
    })

@app.route('/api/whatsapp/desconectar', methods=['POST'])
@requer_admin_api
def api_whatsapp_desconectar():
    """Desconectar número WhatsApp"""
    data = request.json or {}
    instancia_nome = data.get('instancia_nome')
    
    if not instancia_nome or instancia_nome not in WHATSAPP_INSTANCIAS:
        return jsonify({'erro': 'Instância não encontrada'}), 400
    
    WHATSAPP_INSTANCIAS[instancia_nome]['status'] = 'desconectado'
    WHATSAPP_INSTANCIAS[instancia_nome]['numero'] = None
    WHATSAPP_INSTANCIAS[instancia_nome]['conectado_em'] = None
    
    return jsonify({
        'sucesso': True,
        'mensagem': f'{instancia_nome} desconectado'
    })

@app.route('/api/whatsapp/conectar-qrcode', methods=['POST'])
@requer_admin_api
def api_whatsapp_conectar_qrcode():
    """Conectar instância via QR Code REAL da Evolution API"""
    data = request.json or {}
    instancia_nome = data.get('instancia_nome')
    
    if not instancia_nome:
        return jsonify({'erro': 'instancia_nome é obrigatório'}), 400
    
    # Chamar Evolution API para conectar
    resultado = evolution_conectar_instancia(instancia_nome)
    
    if not resultado:
        return jsonify({
            'erro': 'Falha ao conectar com Evolution API. Verifique se está rodando.',
            'url': EVOLUTION_API_URL
        }), 500
    
    # Atualizar status local
    WHATSAPP_INSTANCIAS[instancia_nome]['status'] = 'conectando_qrcode'
    
    return jsonify({
        'sucesso': True,
        'mensagem': f'✓ Iniciando conexão para {instancia_nome}. Escaneie o QR Code no seu WhatsApp!',
        'instancia': instancia_nome,
        'status': 'conectando'
    })

@app.route('/api/whatsapp/verificar-status/<instancia_nome>')
@requer_admin_api
def api_whatsapp_verificar_status(instancia_nome):
    """Verificar status de conexão em tempo real"""
    instancias = evolution_listar_instancias()
    
    for inst in instancias:
        if inst.get('instance', {}).get('instanceName') == instancia_nome:
            status = inst.get('instance', {}).get('instanceStatus')
            
            if status == 'open':
                # Conectou!
                WHATSAPP_INSTANCIAS[instancia_nome]['status'] = 'conectado'
                WHATSAPP_INSTANCIAS[instancia_nome]['conectado_em'] = datetime.now().isoformat()
                WHATSAPP_INSTANCIAS[instancia_nome]['respondendo'] = True
                
                return jsonify({
                    'conectado': True,
                    'status': 'conectado',
                    'instancia': instancia_nome,
                    'mensagem': f'✓ {instancia_nome} conectado com sucesso!'
                })
            else:
                return jsonify({
                    'conectado': False,
                    'status': status,
                    'instancia': instancia_nome,
                    'mensagem': 'Aguardando escanear QR Code...'
                })
    
    return jsonify({'erro': 'Instância não encontrada'}), 404

@app.route('/api/whatsapp/qrcode/<instancia_nome>')
@requer_admin_api
def api_whatsapp_qrcode(instancia_nome):
    """Obter QR Code REAL da Evolution API"""
    # Primeiro, conectar a instância na Evolution para gerar QR Code
    resultado_conexao = evolution_conectar_instancia(instancia_nome)
    
    if not resultado_conexao:
        return jsonify({'erro': 'Falha ao conectar com Evolution API'}), 500
    
    # Aguardar um pouco para o QR code ser gerado
    import time
    time.sleep(1)
    
    # Obter o QR Code gerado
    qrcode_data = evolution_obter_qrcode(instancia_nome)
    
    if not qrcode_data:
        return jsonify({'erro': 'QR Code não disponível. Tente novamente em alguns segundos.'}), 400
    
    # Atualizar status da instância
    WHATSAPP_INSTANCIAS[instancia_nome]['status'] = 'aguardando_qrcode'
    
    return jsonify({
        'sucesso': True,
        'instancia': instancia_nome,
        'qrcode': qrcode_data,
        'instrucoes': 'Abra WhatsApp no seu telefone > Configurações > Aparelhos Vinculados > Vincular um aparelho e escaneie o código acima',
        'timestamp': datetime.now().isoformat()
    })

# ============================================================
# ROTAS DE ATENDIMENTO (VENDEDOR)
# ============================================================

@app.route('/vendedor/atendimento')
@requer_login
def vendedor_atendimento():
    """Tela de atendimento para vendedores"""
    usuario = obter_usuario_atual()
    
    # Filtrar leads pendentes
    leads_pendentes = [v for k, v in LEADS.items() if v['status'] == 'pendente']
    leads_atendidos = [v for k, v in LEADS.items() if v['atendido_por'] == session.get('usuario')]
    
    # Se for vendedor, ver apenas seus leads
    if usuario['role'] == 'vendedor':
        pass  # Pode ver seus próprios leads
    
    return render_template('atendimento_vendedor.html',
                         leads_pendentes=leads_pendentes,
                         leads_atendidos=leads_atendidos,
                         usuario=usuario,
                         conversas=CONVERSAS_LEADS)

@app.route('/api/leads/pendentes')
@requer_login
def api_leads_pendentes():
    """Listar leads não atendidos (apenas pendentes)"""
    leads = [v for k, v in LEADS.items() if v['status'] == 'pendente']
    return jsonify(leads)

@app.route('/api/leads/<lead_id>/atender', methods=['POST'])
@requer_login
def api_leads_atender(lead_id):
    """Marcar lead como atendido"""
    if lead_id not in LEADS:
        return jsonify({'erro': 'Lead não encontrado'}), 404
    
    LEADS[lead_id]['status'] = 'atendido'
    LEADS[lead_id]['atendido_por'] = session.get('usuario')
    
    return jsonify({
        'sucesso': True,
        'mensagem': 'Lead atendido'
    })

@app.route('/api/leads/<lead_id>/responder', methods=['POST'])
@requer_login
def api_leads_responder(lead_id):
    """Enviar mensagem de resposta ao lead"""
    data = request.json or {}
    mensagem = data.get('mensagem')
    
    if lead_id not in LEADS:
        return jsonify({'erro': 'Lead não encontrado'}), 404
    
    if not mensagem:
        return jsonify({'erro': 'Mensagem é obrigatória'}), 400
    
    # Adicionar mensagem ao histórico da conversa
    if lead_id not in CONVERSAS_LEADS:
        CONVERSAS_LEADS[lead_id] = []
    
    CONVERSAS_LEADS[lead_id].append({
        'direção': 'saída',
        'mensagem': mensagem,
        'timestamp': datetime.now().isoformat(),
        'vendedor': session.get('usuario')
    })
    
    return jsonify({
        'sucesso': True,
        'mensagem': 'Resposta enviada ao lead'
    })

@app.route('/api/leads/<lead_id>/conversa')
@requer_login
def api_leads_conversa(lead_id):
    """Obter histórico de conversa com lead"""
    if lead_id not in LEADS:
        return jsonify({'erro': 'Lead não encontrado'}), 404
    
    conversa = CONVERSAS_LEADS.get(lead_id, [])
    lead = LEADS[lead_id]
    
    return jsonify({
        'lead': lead,
        'conversa': conversa
    })

@app.route('/api/whatsapp/confirmar-numero/<numero>', methods=['POST'])
@requer_admin_api
def api_whatsapp_confirmar_numero(numero):
    """Confirmar conexão por número (chamado via webhook/callback)"""
    numero_limpo = ''.join(c for c in numero if c.isdigit())
    
    if not hasattr(api, 'conexoes_pendentes') or numero_limpo not in api.conexoes_pendentes:
        return jsonify({'erro': 'Conexão não encontrada'}), 404
    
    info_conexao = api.conexoes_pendentes[numero_limpo]
    instancia_nome = info_conexao['instancia']
    
    # Marcar como conectada
    WHATSAPP_INSTANCIAS[instancia_nome]['status'] = 'conectado'
    WHATSAPP_INSTANCIAS[instancia_nome]['conectado_em'] = datetime.now().isoformat()
    WHATSAPP_INSTANCIAS[instancia_nome]['respondendo'] = True
    info_conexao['confirmado'] = True
    
    return jsonify({
        'sucesso': True,
        'mensagem': f'✓ {instancia_nome} conectado com sucesso!',
        'instancia': instancia_nome
    })

@app.route('/api/whatsapp/status-conexao/<numero>')
@requer_admin_api
def api_whatsapp_status_conexao(numero):
    """Verificar status da conexão aguardando confirmação"""
    numero_limpo = ''.join(c for c in numero if c.isdigit())
    
    if not hasattr(api, 'conexoes_pendentes') or numero_limpo not in api.conexoes_pendentes:
        return jsonify({'status': 'nao_encontrada'}), 404
    
    info_conexao = api.conexoes_pendentes[numero_limpo]
    
    return jsonify({
        'numero': numero_limpo,
        'instancia': info_conexao['instancia'],
        'confirmado': info_conexao['confirmado'],
        'timestamp': info_conexao['timestamp']
    })

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'banco_integrado': USANDO_BANCO,
        'usuarios': len(USUARIOS),
        'campanhas': len(CAMPANHAS)
    })

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'erro': 'Não encontrado'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'erro': 'Erro interno do servidor'}), 500

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print(" PARISCRED INTELLIGENCE - SaaS COMPLETO")
    print("="*70)
    
    modo = "BANCO DE DADOS" if USANDO_BANCO else "MODO DEMONSTRACAO"
    print(f"\n [INFO] Modo: {modo}")
    print(f" [SUCCESS] Servidor iniciando na porta 5000...")
    print(f" [SUCCESS] Acessar em: http://localhost:5000")
    print(f"\n [INFO] Contas de Teste:")
    print(f"   ADM: admin@pariscred.com / Admin@2025")
    print(f"   Vendedor: vendedor1@pariscred.com / Vendedor@123")
    print(f"\n" + "="*70 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
