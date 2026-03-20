"""
ParisCred Intelligence - Sistema SaaS com SQLite
Aplicação Full-Stack com Autenticação, Painel ADM e Gerenciamento (Banco de Dados)
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
from datetime import datetime
import secrets
import os

# Importar funções do database
from database import (
    Database,
    UsuariosDB,
    CampanhasDB,
    HistoricoDB
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

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# Inicializar banco de dados na primeira execução
db = Database("app.db")

# Registrar rotas de skills (se disponíveis)
if SKILLS_ENABLED:
    try:
        from skills_routes import registrar_rotas_skills
        registrar_rotas_skills(app)
    except ImportError:
        pass  # Skills routes não disponíveis ainda

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
        
        # Verificar credenciais
        if UsuariosDB.verificar_senha(email, senha):
            usuario = UsuariosDB.obter(email)
            if usuario and usuario['ativo']:
                session['usuario'] = email
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
        # Estatísticas ADM
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
        # Estatísticas do vendedor
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
        # Criar nova campanha
        data = request.json
        
        campanha_id = CampanhasDB.criar(
            nome=data.get('nome', 'Nova Campanha'),
            descricao=data.get('descricao', ''),
            criador=session['usuario'],
            mensagem=data.get('mensagem', ''),
            beneficiarios=data.get('beneficiarios', []),
            botoes=data.get('botoes', []),
            instancias=data.get('instancias', ['Paris_01'])
        )
        
        if campanha_id:
            nova_campanha = CampanhasDB.obter(campanha_id)
            return jsonify({
                'sucesso': True,
                'mensagem': f'Campanha "{nova_campanha["nome"]}" criada com sucesso!',
                'campanha': campanha_para_json(nova_campanha)
            }), 201
        else:
            return jsonify({'erro': 'Erro ao criar campanha'}), 500


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
        return jsonify({'erro': 'Acesso negado'}), 403
    
    if request.method == 'GET':
        return jsonify(campanha_para_json(campanha))
    
    elif request.method == 'PUT':
        # Atualizar campanha
        data = request.json
        
        atualizar_dados = {
            'nome': data.get('nome'),
            'descricao': data.get('descricao'),
            'beneficiarios_json': data.get('beneficiarios'),
            'mensagem': data.get('mensagem'),
            'botoes_json': data.get('botoes'),
            'instancias_json': data.get('instancias')
        }
        
        # Remover valores None
        atualizar_dados = {k: v for k, v in atualizar_dados.items() if v is not None}
        
        if CampanhasDB.atualizar(camp_id, **atualizar_dados):
            campanha_atualizada = CampanhasDB.obter(camp_id)
            return jsonify({
                'sucesso': True,
                'campanha': campanha_para_json(campanha_atualizada)
            })
        else:
            return jsonify({'erro': 'Erro ao atualizar campanha'}), 500
    
    elif request.method == 'DELETE':
        # Deletar campanha
        if campanha['status'] != 'rascunho':
            return jsonify({'erro': 'Só é possível deletar campanhas em rascunho'}), 400
        
        if CampanhasDB.deletar(camp_id):
            return jsonify({'sucesso': True, 'mensagem': 'Campanha deletada'})
        else:
            return jsonify({'erro': 'Erro ao deletar campanha'}), 500


# ============================================================
# ROTAS DE DISPARO
# ============================================================

@app.route('/api/campanhas/<int:camp_id>/disparar', methods=['POST'])
@requer_login
def disparar_campanha(camp_id):
    """Dispara uma campanha"""
    usuario = obter_usuario_atual()
    
    campanha = CampanhasDB.obter(camp_id)
    if not campanha:
        return jsonify({'erro': 'Campanha não encontrada'}), 404
    
    # Verificar permissão
    if usuario['role'] != 'admin' and campanha['criador'] != session['usuario']:
        return jsonify({'erro': 'Acesso negado'}), 403
    
    if not campanha['beneficiarios_json']:
        return jsonify({'erro': 'Nenhum beneficiário configurado'}), 400
    
    # Simular disparo (em produção, conectaria com Evolution API)
    resultados = []
    
    try:
        for idx, beneficiario in enumerate(campanha['beneficiarios_json']):
            # Aqui entra a lógica real de envio via Evolution API
            resultados.append({
                'beneficiario': beneficiario.get('nome', 'N/A'),
                'numero': beneficiario.get('numero', 'N/A'),
                'status': 'enviado',
                'timestamp': datetime.now().isoformat()
            })
        
        # Atualizar campanha (com transação)
        CampanhasDB.atualizar(
            camp_id,
            status='disparado',
            disparado_em=datetime.now().isoformat(),
            total_enviados=len(resultados)
        )
        
        # Registrar no histórico
        HistoricoDB.registrar(
            campanha_id=camp_id,
            usuario=session['usuario'],
            total_beneficiarios=len(resultados),
            resultados={'enviados': resultados}
        )
        
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
    return render_template('admin.html', usuario=usuario_para_json(usuario))


@app.route('/api/admin/usuarios', methods=['GET', 'POST'])
@requer_admin
def api_admin_usuarios():
    """Gerenciar usuários (apenas ADM)"""
    
    if request.method == 'GET':
        # Listar usuários
        usuarios = UsuariosDB.listar_todos()
        return jsonify([usuario_para_json(u) for u in usuarios])
    
    elif request.method == 'POST':
        # Criar novo usuário
        data = request.json
        
        email = data.get('email', '').lower()
        
        # Verificar se já existe
        if UsuariosDB.obter(email):
            return jsonify({'erro': 'Email já cadastrado'}), 400
        
        # Criar novo usuário
        if UsuariosDB.criar(
            email=email,
            nome=data.get('nome', 'Novo Usuário'),
            senha=data.get('senha', 'Temp@123'),
            role=data.get('role', 'vendedor')
        ):
            usuario_criado = UsuariosDB.obter(email)
            return jsonify({
                'sucesso': True,
                'mensagem': f'Usuário {data.get("nome")} criado com sucesso!',
                'usuario': usuario_para_json(usuario_criado)
            }), 201
        else:
            return jsonify({'erro': 'Erro ao criar usuário'}), 500


@app.route('/api/admin/usuarios/<email>', methods=['PUT', 'DELETE'])
@requer_admin
def api_admin_usuario_detalhes(email):
    """Gerenciar usuário específico (apenas ADM)"""
    
    usuario = UsuariosDB.obter(email)
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    if request.method == 'PUT':
        data = request.json
        
        if UsuariosDB.atualizar(
            email,
            nome=data.get('nome'),
            role=data.get('role')
        ):
            usuario_atualizado = UsuariosDB.obter(email)
            return jsonify({
                'sucesso': True,
                'usuario': usuario_para_json(usuario_atualizado)
            })
        else:
            return jsonify({'erro': 'Erro ao atualizar usuário'}), 500
    
    elif request.method == 'DELETE':
        # Soft delete - apenas desativa
        if UsuariosDB.deletar(email):
            return jsonify({'sucesso': True, 'mensagem': 'Usuário desativado'})
        else:
            return jsonify({'erro': 'Erro ao desativar usuário'}), 500


@app.route('/api/admin/historico')
@requer_admin
def api_admin_historico():
    """Ver histórico de disparos (apenas ADM)"""
    from database import Database
    
    db = Database()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.id, h.campanha_id, h.usuario, h.timestamp, 
                   h.total_beneficiarios, h.resultados_json
            FROM historico h
            WHERE h.ativo = 1
            ORDER BY h.timestamp DESC
        """)
        
        import json
        historicos = []
        for row in cursor.fetchall():
            historicos.append({
                'id': row[0],
                'campanha_id': row[1],
                'usuario': row[2],
                'timestamp': row[3],
                'total_beneficiarios': row[4],
                'resultados': json.loads(row[5] or '{}')
            })
        
        return jsonify(historicos)


@app.route('/api/health')
def health():
    """Health check"""
    usuarios = UsuariosDB.listar_todos()
    campanhas = CampanhasDB.listar_todas()
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'usuarios': len(usuarios),
        'campanhas': len(campanhas),
        'database': 'SQLite'
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
    print(" 🚀 PARISCRED INTELLIGENCE - SaaS COMPLETO (SQLite)")
    print("="*70)
    print(f"\n ✓ Servidor iniciando na porta 5000...")
    print(f" ✓ Acessar em: http://localhost:5000")
    print(f" ✓ Banco de dados: app.db (SQLite)")
    print(f"\n 📱 Contas de Teste (após migração):")
    print(f"   ADM: admin@pariscred.com / Admin@2025")
    print(f"   Vendedor: vendedor1@pariscred.com / Vendedor@123")
    print(f"\n" + "="*70 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
