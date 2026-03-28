"""
Extensão de rotas para Copilot Skills
CRM, Financeiro, WhatsApp, Admin
VERSÃO CORRIGIDA - Sem decoradores @app.route para evitar duplicação
"""

from flask import Flask, jsonify, request
from functools import wraps

# Importar skills
from skill_crm import ClientesDB
from skill_financeiro import FinanceiroDB
from skill_whatsapp import WhatsAppDB
from skill_admin import AdminReportsDB

# MCP modules - comentario temporario ate implementar
# from mcp_evolution import evolution_mcp
# from mcp_database import db_mcp

# Decorator de proteção
def protected(f):
    """Verifica autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from database import UsuariosDB
        from flask import session, redirect, url_for
        
        if 'usuario' not in session:
            return jsonify({'erro': 'Não autenticado'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


def admin_only(f):
    """Apenas admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from database import UsuariosDB
        from flask import session
        
        if 'usuario' not in session:
            return jsonify({'erro': 'Não autenticado'}), 401
        
        usuario = UsuariosDB.obter(session['usuario'])
        if not usuario or usuario['role'] != 'admin':
            return jsonify({'erro': 'Acesso negado (apenas admin)'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


# ================================================================
# DEFINIÇÃO DE FUNÇÕES DE ROTA (SEM DECORADORES)
# ================================================================

# CRM - Gestão de Clientes

def api_crm_clientes():
    """Listar/criar clientes"""
    if request.method == 'GET':
        status = request.args.get('status')
        limite = int(request.args.get('limite', 50))
        
        clientes = ClientesDB.listar_clientes(status=status, limite=limite)
        
        return jsonify({
            "sucesso": True,
            "total": len(clientes),
            "clientes": clientes
        })
    
    elif request.method == 'POST':
        data = request.json
        
        resultado = ClientesDB.criar_cliente(
            nome=data.get('nome'),
            phone=data.get('phone'),
            cpf=data.get('cpf'),
            empresa=data.get('empresa'),
            cargo=data.get('cargo'),
            renda=data.get('renda'),
            email=data.get('email')
        )
        
        if 'erro' in resultado:
            return jsonify(resultado), 400
        
        return jsonify(resultado), 201


def api_crm_cliente_detalhes(cliente_id):
    """Detalhes de um cliente"""
    cliente = ClientesDB.obter_cliente(cliente_id)
    
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    
    historico = ClientesDB.obter_historico(cliente_id)
    
    return jsonify({
        "sucesso": True,
        "cliente": cliente,
        "historico": historico,
        "total_interacoes": len(historico)
    })


def api_crm_registrar_interacao(cliente_id):
    """Registra interação com cliente"""
    data = request.json
    
    resultado = ClientesDB.registrar_interacao(
        cliente_id=cliente_id,
        tipo=data.get('tipo'),
        descricao=data.get('descricao'),
        resultado=data.get('resultado')
    )
    
    return jsonify(resultado), 201


def api_crm_atualizar_status(cliente_id):
    """Atualiza status do cliente"""
    data = request.json
    
    resultado = ClientesDB.atualizar_status(
        cliente_id=cliente_id,
        novo_status=data.get('novo_status')
    )
    
    return jsonify(resultado)


def api_crm_relatorio_status():
    """Relatório de clientes por status"""
    relatorio = ClientesDB.relatorio_por_status()
    
    return jsonify({
        "sucesso": True,
        "relatorio": relatorio
    })


def api_crm_buscar_phone():
    """Busca cliente por telefone"""
    phone = request.args.get('phone')
    
    if not phone:
        return jsonify({"erro": "Telefone obrigatório"}), 400
    
    cliente = ClientesDB.buscar_por_phone(phone)
    
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    
    return jsonify(cliente)


# FINANCEIRO - Cálculos e Simulações

def api_financeiro_consignado():
    """Calcula margem de consignado"""
    data = request.json
    
    resultado = FinanceiroDB.calcular_consignado(
        renda_liquida=data.get('renda'),
        percentual=data.get('percentual', 30)
    )
    
    return jsonify(resultado)


def api_financeiro_simular():
    """Simula empréstimo"""
    data = request.json
    
    resultado = FinanceiroDB.simular_emprestimo(
        valor=data.get('valor'),
        taxa_anual=data.get('taxa'),
        parcelas=data.get('parcelas')
    )
    
    return jsonify(resultado)


def api_financeiro_analisar_risco(cliente_id):
    """Analisa risco do cliente"""
    risco = FinanceiroDB.analisar_risco(cliente_id)
    
    return jsonify(risco)


def api_financeiro_criar_emprestimo():
    """Cria novo empréstimo"""
    data = request.json
    
    resultado = FinanceiroDB.criar_emprestimo(
        cliente_id=data.get('cliente_id'),
        valor=data.get('valor'),
        taxa_anual=data.get('taxa'),
        parcelas=data.get('parcelas')
    )
    
    if 'erro' in resultado:
        return jsonify(resultado), 400
    
    return jsonify(resultado), 201


def api_financeiro_kpis():
    """KPIs financeiros gerais"""
    kpis = FinanceiroDB.obter_kpis()
    
    return jsonify({
        "sucesso": True,
        "kpis": kpis
    })


# WHATSAPP - Integração WhatsApp

def api_whatsapp_instancias():
    """Listar/criar instâncias WhatsApp"""
    if request.method == 'GET':
        instancias = WhatsAppDB.listar_instancias()
        return jsonify({
            "sucesso": True,
            "total": len(instancias),
            "instancias": instancias
        })
    
    elif request.method == 'POST':
        data = request.json
        
        resultado = WhatsAppDB.criar_instancia(
            nome_instancia=data.get('nome_instancia')
        )
        
        if 'erro' in resultado:
            return jsonify(resultado), 400
        
        return jsonify(resultado), 201


def api_whatsapp_enviar():
    """Envia mensagem WhatsApp"""
    data = request.json
    
    resultado = WhatsAppDB.enviar_mensagem(
        numero_destino=data.get('numero'),
        texto=data.get('texto'),
        nome_instancia=data.get('instancia')
    )
    
    return jsonify(resultado), 201


def webhook_whatsapp():
    """Webhook para receber eventos do WhatsApp"""
    dados = request.json
    
    resultado = WhatsAppDB.processar_webhook(dados)
    
    return jsonify(resultado), 200


def api_whatsapp_status(nome):
    """Obtém status de uma instância"""
    resultado = WhatsAppDB.atualizar_status_instancia(nome, nome)
    
    return jsonify(resultado)


# ADMIN - Relatórios e KPIs

def api_admin_kpis():
    """KPIs gerais do sistema"""
    dias = request.args.get('dias', 30, type=int)
    
    kpis = AdminReportsDB.kpis_gerais(dias=dias)
    
    return jsonify({
        "sucesso": True,
        "kpis": kpis
    })


def api_admin_relatorio_clientes():
    """Relatório de clientes por status"""
    relatorio = AdminReportsDB.relatorio_clientes_por_status()
    
    return jsonify(relatorio)


def api_admin_relatorio_lucro():
    """Análise de lucratividade"""
    analise = AdminReportsDB.analise_lucratividade()
    
    return jsonify({
        "sucesso": True,
        "analise": analise
    })


def api_admin_top_clientes():
    """Top clientes por renda"""
    limite = request.args.get('limite', 10, type=int)
    
    top = AdminReportsDB.ranking_maiores_clientes(limite=limite)
    
    return jsonify({
        "sucesso": True,
        "top_clientes": top
    })


def api_admin_ultimas():
    """Últimas transações"""
    limite = request.args.get('limite', 20, type=int)
    
    transacoes = AdminReportsDB.ultimas_transacoes(limite=limite)
    
    return jsonify({
        "sucesso": True,
        "transacoes": transacoes
    })


def api_admin_alertas():
    """Alertas do sistema"""
    alertas = AdminReportsDB.alertas_sistema()
    
    return jsonify({
        "sucesso": True,
        "alertas": alertas,
        "total": len(alertas)
    })


def api_admin_relatorio_completo():
    """Relatório completo em JSON"""
    relatorio = AdminReportsDB.exportar_relatorio_completo()
    
    return jsonify(relatorio)


def api_admin_relatorio_periodo():
    """Relatório de um período específico"""
    data = request.json
    
    relatorio = AdminReportsDB.relatorio_por_periodo(
        data_inicio=data.get('data_inicio'),
        data_fim=data.get('data_fim')
    )
    
    return jsonify(relatorio)


# MCP - Acesso Direto ao BD e Evolution

def api_mcp_query():
    """Executar query no banco (apenas SELECT)"""
    data = request.json
    
    resultado = db_mcp.execute_query(
        query=data.get('query'),
        params=data.get('params')
    )
    
    return jsonify(resultado)


def api_mcp_evolution_instancias():
    """Listar instâncias da Evolution API"""
    resultado = evolution_mcp.list_instances()
    
    return jsonify(resultado)


def api_mcp_evolution_qrcode(nome):
    """Obter QR Code para conectar"""
    resultado = evolution_mcp.get_qrcode(nome)
    
    return jsonify(resultado)


def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "app": "ParisCred Intelligence",
        "version": "1.0.0",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })


# ================================================================
# REGISTRATION FUNCTION - Usando app.add_url_rule()
# ================================================================

def registrar_rotas_skills(app: Flask):
    """Registra todas as rotas de skills usando app.add_url_rule()"""
    
    # CRM Routes
    app.add_url_rule('/api/crm/clientes', 
                     view_func=protected(api_crm_clientes), 
                     methods=['GET', 'POST'])
    
    app.add_url_rule('/api/crm/clientes/<int:cliente_id>', 
                     view_func=protected(api_crm_cliente_detalhes))
    
    app.add_url_rule('/api/crm/clientes/<int:cliente_id>/interacao', 
                     view_func=protected(api_crm_registrar_interacao), 
                     methods=['POST'])
    
    app.add_url_rule('/api/crm/clientes/<int:cliente_id>/status', 
                     view_func=protected(api_crm_atualizar_status), 
                     methods=['PUT'])
    
    app.add_url_rule('/api/crm/relatorio/por-status', 
                     view_func=protected(api_crm_relatorio_status))
    
    app.add_url_rule('/api/crm/clientes/buscar/phone', 
                     view_func=protected(api_crm_buscar_phone))
    
    # Financeiro Routes
    app.add_url_rule('/api/financeiro/consignado', 
                     view_func=protected(api_financeiro_consignado), 
                     methods=['POST'])
    
    app.add_url_rule('/api/financeiro/simular', 
                     view_func=protected(api_financeiro_simular), 
                     methods=['POST'])
    
    app.add_url_rule('/api/financeiro/risco/<int:cliente_id>', 
                     view_func=protected(api_financeiro_analisar_risco))
    
    app.add_url_rule('/api/financeiro/emprestimos', 
                     view_func=protected(api_financeiro_criar_emprestimo), 
                     methods=['POST'])
    
    app.add_url_rule('/api/financeiro/kpis', 
                     view_func=protected(api_financeiro_kpis))
    
    # WhatsApp Routes
    app.add_url_rule('/api/whatsapp/instancias', 
                     view_func=admin_only(api_whatsapp_instancias), 
                     methods=['GET', 'POST'])
    
    app.add_url_rule('/api/whatsapp/mensagem', 
                     view_func=protected(api_whatsapp_enviar), 
                     methods=['POST'])
    
    app.add_url_rule('/webhook/whatsapp', 
                     view_func=webhook_whatsapp, 
                     methods=['POST'])
    
    app.add_url_rule('/api/whatsapp/instancia/<nome>/status', 
                     view_func=admin_only(api_whatsapp_status))
    
    # Admin Routes
    app.add_url_rule('/api/admin/kpis', 
                     view_func=admin_only(api_admin_kpis))
    
    app.add_url_rule('/api/admin/relatorio/clientes', 
                     view_func=admin_only(api_admin_relatorio_clientes))
    
    app.add_url_rule('/api/admin/relatorio/lucratividade', 
                     view_func=admin_only(api_admin_relatorio_lucro))
    
    app.add_url_rule('/api/admin/top-clientes', 
                     view_func=admin_only(api_admin_top_clientes))
    
    app.add_url_rule('/api/admin/ultimas-transacoes', 
                     view_func=admin_only(api_admin_ultimas))
    
    app.add_url_rule('/api/admin/alertas', 
                     view_func=admin_only(api_admin_alertas))
    
    app.add_url_rule('/api/admin/relatorio/completo', 
                     view_func=admin_only(api_admin_relatorio_completo))
    
    app.add_url_rule('/api/admin/relatorio/periodo', 
                     view_func=admin_only(api_admin_relatorio_periodo), 
                     methods=['POST'])
    
    # MCP Routes
    app.add_url_rule('/api/mcp/db/query', 
                     view_func=admin_only(api_mcp_query), 
                     methods=['POST'])
    
    app.add_url_rule('/api/mcp/evolution/instancias', 
                     view_func=admin_only(api_mcp_evolution_instancias))
    
    app.add_url_rule('/api/mcp/evolution/qrcode/<nome>', 
                     view_func=admin_only(api_mcp_evolution_qrcode))
