"""
Skill: WhatsApp Atendimento
Integração Evolution API, automação, chatbots
"""

import sqlite3
import requests
import json
from datetime import datetime
from typing import Optional, Dict, List
from database import Database


class WhatsAppDB:
    """Gerencia instâncias e mensagens WhatsApp"""
    
    @staticmethod
    def criar_tabelas():
        """Cria tabelas de WhatsApp"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Instâncias WhatsApp
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS whatsapp_instancias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_instancia TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    status TEXT DEFAULT 'desconectado',
                    qrcode LONGBLOB,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_conexao TIMESTAMP,
                    ultima_atividade TIMESTAMP,
                    ativo BOOLEAN DEFAULT 1
                )
            """)
            
            # Mensagens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensagens_whatsapp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_origem TEXT,
                    numero_destino TEXT NOT NULL,
                    texto TEXT,
                    tipo TEXT DEFAULT 'texto',
                    direcao TEXT,
                    status TEXT DEFAULT 'pendente',
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    instancia TEXT,
                    message_id TEXT UNIQUE,
                    ativo BOOLEAN DEFAULT 1
                )
            """)
            
            # Webhooks log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webhooks_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evento TEXT,
                    payload JSON,
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    @staticmethod
    def criar_instancia(nome_instancia: str) -> Dict:
        """Cria nova instância WhatsApp"""
        
        # Salvar no banco
        db = Database()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO whatsapp_instancias (nome_instancia, status)
                    VALUES (?, 'qrcode')
                """, (nome_instancia,))
                
                instancia_id = cursor.lastrowid
                conn.commit()
            
            return {
                "sucesso": True,
                "instancia_id": instancia_id,
                "nome_instancia": nome_instancia,
                "status": "qrcode",
                "mensagem": "Instância criada. Escaneie o QR Code para conectar."
            }
        
        except sqlite3.IntegrityError:
            return {"erro": "Instância com este nome já existe"}
    
    @staticmethod
    def listar_instancias() -> List[Dict]:
        """Lista todas as instâncias"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome_instancia, phone, status, data_conexao, ultima_atividade
                FROM whatsapp_instancias WHERE ativo = 1
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def atualizar_status_instancia(nome_instancia: str, novo_status: str) -> Dict:
        """Atualiza status da instância"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE whatsapp_instancias 
                SET status = ?, data_conexao = datetime('now'), ultima_atividade = datetime('now')
                WHERE nome_instancia = ? AND ativo = 1
            """, (novo_status, nome_instancia))
            
            conn.commit()
        
        return {"sucesso": True, "novo_status": novo_status}
    
    @staticmethod
    def enviar_mensagem(numero_destino: str, texto: str, nome_instancia: str = None) -> Dict:
        """Envia mensagem WhatsApp"""
        
        # Log da mensagem
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mensagens_whatsapp 
                (numero_destino, texto, tipo, direcao, status, instancia)
                VALUES (?, ?, 'texto', 'enviada', 'envio', ?)
            """, (numero_destino, texto, nome_instancia))
            
            mensagem_id = cursor.lastrowid
            conn.commit()
        
        return {
            "sucesso": True,
            "mensagem_id": mensagem_id,
            "numero_destino": numero_destino,
            "status": "enviado",
            "data": datetime.now().isoformat()
        }
    
    @staticmethod
    def processar_webhook(dados: Dict) -> Dict:
        """Processa webhook do Evolution API"""
        
        # Log webhook
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO webhooks_log (evento, payload)
                VALUES (?, ?)
            """, (dados.get("event"), json.dumps(dados)))
            
            conn.commit()
        
        tipo_evento = dados.get("event")
        
        if tipo_evento == "messages.upsert":
            return WhatsAppDB._processar_mensagem_entrada(dados)
        
        elif tipo_evento == "connection.update":
            return WhatsAppDB._processar_conexao(dados)
        
        else:
            return {"processado": False, "evento": tipo_evento}
    
    @staticmethod
    def _processar_mensagem_entrada(dados: Dict) -> Dict:
        """Processa mensagem recebida"""
        
        from skill_crm import ClientesDB
        
        numero_remetente = dados.get("sender")
        mensagem_texto = dados.get("message", {}).get("text", "")
        instancia = dados.get("instance")
        
        # Registrar mensagem
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mensagens_whatsapp 
                (numero_origem, texto, tipo, direcao, status, instancia)
                VALUES (?, ?, 'texto', 'recebida', 'sucesso', ?)
            """, (numero_remetente, mensagem_texto, instancia))
            
            conn.commit()
        
        # Buscar/Criar cliente
        cliente = ClientesDB.buscar_por_phone(numero_remetente)
        
        if not cliente:
            ClientesDB.criar_cliente(
                nome="Cliente WhatsApp",
                phone=numero_remetente
            )
            cliente = ClientesDB.buscar_por_phone(numero_remetente)
        
        # Registrar interação
        if cliente:
            ClientesDB.registrar_interacao(
                cliente['id'],
                'whatsapp',
                mensagem_texto,
                'recebida'
            )
        
        # Classificar e responder
        resposta = WhatsAppDB._classificar_e_responder(mensagem_texto, cliente)
        
        return {
            "processado": True,
            "cliente_id": cliente['id'] if cliente else None,
            "resposta": resposta
        }
    
    @staticmethod
    def _processar_conexao(dados: Dict) -> Dict:
        """Processa evento de conexão"""
        instancia = dados.get("instance")
        novo_status = "conectado" if dados.get("connection", {}).get("isOnline") else "desconectado"
        
        WhatsAppDB.atualizar_status_instancia(instancia, novo_status)
        
        return {"processado": True, "instancia": instancia, "novo_status": novo_status}
    
    @staticmethod
    def _classificar_e_responder(mensagem: str, cliente: Dict = None) -> str:
        """Classifica intenção e gera resposta"""
        
        mensagem_lower = mensagem.lower()
        
        # Palavras-chave
        if any(word in mensagem_lower for word in ["emprestimo", "loan", "credito", "credit"]):
            return """
Ótimo! Vamos ajudá-lo com um empréstimo consignado.

Qual é o valor que você precisa emprestar?
(Valores entre R$ 500 e R$ 50.000)
            """
        
        elif any(word in mensagem_lower for word in ["simulacao", "simular", "quanto", "parcela"]):
            return """
Simulação de Empréstimo:

Para simular, me diga:
1. Valor desejado (ex: 5000)
2. Número de parcelas (ex: 60)

Vou calcular tudo pra você!
            """
        
        elif any(word in mensagem_lower for word in ["minha", "conta", "saldo", "extrato"]):
            if cliente:
                return f"""
Dados da sua conta, {cliente.get('nome', 'Cliente')}:
- Status: {cliente.get('status', 'ativo')}
- Margem Disponível: R$ {cliente.get('margem_consignavel', 0)}
- Última atualização: {cliente.get('data_criacao')}

Precisa de algo mais?
                """
            else:
                return "Para acessar sua conta, precisamos do seu cadastro."
        
        elif any(word in mensagem_lower for word in ["oi", "olá", "opa", "e ai"]):
            return """
Olá! Bem-vindo ao ParisCred! 👋

Como posso ajudá-lo hoje?
- Empréstimo consignado
- Simulação
- Dados da conta
- Suporte
            """
        
        else:
            return """
Desculpe, não entendi. 😅

Posso ajudar com:
- Empréstimo consignado
- Simulação
- Dados da conta
- Suporte técnico

O que você quer fazer?
            """


# Inicializar tabelas
WhatsAppDB.criar_tabelas()
