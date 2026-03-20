---
name: whatsapp-atendimento
description: "Use when: building WhatsApp flows, chatbots, automations, message templates, customer support workflows, number maturation, Evolution API integration. Handles all WhatsApp-related features."
---

# 💬 WhatsApp Atendimento Skill

**Use this skill for**: WhatsApp flows, chatbots, message automation, number maturation, Evolution API, customer support.

## 🔧 Evolution API Setup

```python
# Configuration
EVOLUTION_API_URL = "http://localhost:8080"
EVOLUTION_API_KEY = "CONSIGNADO123"

# Headers
EVOLUTION_HEADERS = {
    "Content-Type": "application/json",
    "apikey": EVOLUTION_API_KEY
}
```

## 📱 Estrutura de Intâncias WhatsApp

```python
# instances table
- id: INTEGER PRIMARY KEY
- nome_instancia: TEXT UNIQUE
- phone: TEXT
- status: TEXT (conectado, qrcode, falha)
- qrcode: LONGBLOB
- data_criacao: TIMESTAMP
- data_conexao: TIMESTAMP
- ultima_atividade: TIMESTAMP
```

## 🚀 Criar Instância WhatsApp

```python
async def criar_instancia(nome_instancia):
    """
    Cria nova instância WhatsApp na Evolution API
    """
    payload = {
        "instanceName": nome_instancia,
        "integration": "WHATSAPP-BUSINESS"
    }
    
    response = requests.post(
        f"{EVOLUTION_API_URL}/instance/create",
        json=payload,
        headers=EVOLUTION_HEADERS
    )
    
    if response.status_code == 201:
        data = response.json()
        
        # Salvar no banco
        db.execute("""
            INSERT INTO instances (nome_instancia, status, data_criacao)
            VALUES (?, 'qrcode', datetime('now'))
        """, (nome_instancia,))
        
        return {
            "sucesso": True,
            "hash": data.get("instance", {}).get("instanceId"),
            "nome_instancia": nome_instancia
        }
    
    return {"erro": "Falha ao criar instância"}
```

## 🔐 QR Code Connection

```python
def obter_qrcode(nome_instancia):
    """
    Obtém QR Code para conectar WhatsApp
    """
    response = requests.get(
        f"{EVOLUTION_API_URL}/instance/fetchInstances",
        params={"instanceName": nome_instancia},
        headers=EVOLUTION_HEADERS
    )
    
    instances = response.json().get("instances", [])
    
    for inst in instances:
        if inst.get("instance", {}).get("instanceName") == nome_instancia:
            return {
                "hash": inst.get("instance", {}).get("instanceId"),
                "qr_code": inst.get("qrcode", {}).get("base64"),
                "status": inst.get("instance", {}).get("status")
            }
    
    return {"erro": "Instância não encontrada"}
```

## 📨 Enviar Mensagem

```python
def enviar_mensagem_whatsapp(numero_destino, texto_mensagem, nome_instancia):
    """
    Envia mensagem via WhatsApp
    
    Entrada:
    - numero_destino: "5511987654321"
    - texto_mensagem: "Olá! Como está?"
    - nome_instancia: "instance1"
    
    Saída: ID da mensagem ou erro
    """
    payload = {
        "number": numero_destino,
        "text": texto_mensagem
    }
    
    response = requests.post(
        f"{EVOLUTION_API_URL}/message/sendText/{nome_instancia}",
        json=payload,
        headers=EVOLUTION_HEADERS
    )
    
    if response.status_code == 200:
        message_id = response.json().get("key", {}).get("id")
        
        # Log no banco
        db.execute("""
            INSERT INTO mensagens_whatsapp (numero_destino, texto, tipo, status, data, instancia)
            VALUES (?, ?, 'enviada', 'sucesso', datetime('now'), ?)
        """, (numero_destino, texto_mensagem, nome_instancia))
        
        return {"sucesso": True, "message_id": message_id}
    
    return {"erro": "Falha ao enviar mensagem"}
```

## 🤖 Chatbot Flow

```python
def processar_mensagem_entrada(dados_webhook):
    """
    Processa mensagens recebidas do WhatsApp
    """
    numero_remetente = dados_webhook.get("sender")
    mensagem = dados_webhook.get("message", {}).get("text")
    nome_instancia = dados_webhook.get("instance")
    
    # 1. Buscar/Criar cliente
    cliente_id = obter_ou_criar_cliente(numero_remetente)
    
    # 2. Registrar interação
    db.execute("""
        INSERT INTO interactions (customer_id, tipo, descricao, data)
        VALUES (?, 'whatsapp', ?, datetime('now'))
    """, (cliente_id, mensagem))
    
    # 3. Classificar intenção
    intencao = classificar_intencao(mensagem)  # loan, support, info, etc
    
    # 4. Responder baseado em intenção
    resposta = gerar_resposta(intencao, cliente_id)
    
    # 5. Enviar resposta
    enviar_mensagem_whatsapp(numero_remetente, resposta, nome_instancia)
    
    return {"processado": True}
```

## 📋 Templates de Resposta

```python
TEMPLATES = {
    "saudacao": "Olá {nome}! Bem-vindo ao ParisCred. Como posso ajudá-lo?",
    
    "emprestimo": """
Ótimo! Vou ajudá-lo com um empréstimo consignado.

Qual é o valor que você precisa emprestar?
(Por favor, digite um valor entre R$ 500 e R$ {margem_max})
    """,
    
    "simulacao": """
Simulação de Empréstimo
💰 Valor: R$ {valor}
📅 Parcelas: {parcelas}x
💹 Taxa: {taxa}% a.a.
📊 Valor da Parcela: R$ {valor_parcela}

Deseja prosseguir?
""",
    
    "suporte": "Nossa equipe irá contatá-lo em breve. Ticket: #{ticket_id}",
    
    "encerramento": "Obrigado por usar ParisCred! Até logo!"
}
```

## 🔄 Webhook Handler

```python
@app.route('/webhook/evolution', methods=['POST'])
def webhook_evolution():
    """
    Recebe eventos do Evolution API
    """
    dados = request.json
    tipo_evento = dados.get("event")
    
    if tipo_evento == "messages.upsert":
        processar_mensagem_entrada(dados)
    
    elif tipo_evento == "connection.update":
        atualizar_status_instancia(dados)
    
    elif tipo_evento == "messages.reaction":
        processar_reacao(dados)
    
    return {"sucesso": True}, 200
```

## 📊 Database - Mensagens

```python
# mensagens_whatsapp table
- id: INTEGER PRIMARY KEY
- numero_origem: TEXT
- numero_destino: TEXT
- texto: LONGTEXT
- tipo: TEXT (enviada, recebida)
- status: TEXT (sucesso, pendente, falha)
- data: TIMESTAMP
- instancia: TEXT
- message_id: TEXT UNIQUE

# webhooks_log table
- id: INTEGER PRIMARY KEY
- evento: TEXT
- payload: JSON
- data: TIMESTAMP
```

## 🌱 Maturador de Números

```python
def maturar_numero(numero_whatsapp):
    """
    Inicia processo de maturação do número
    - Conecta o número
    - Envia mensagens iniciais
    - Aguarda respostas
    - Valida se está "pronto" para campanhas
    """
    status = {
        "numero": numero_whatsapp,
        "conectado": False,
        "mensagens_enviadas": 0,
        "mensagens_recebidas": 0,
        "score_saude": 0,
        "pronto_para_campanhas": False
    }
    
    # Passo 1: Conectar
    if conectar_numero_evolution(numero_whatsapp):
        status["conectado"] = True
    
    # Passo 2: Enviar mensagens de teste
    for i in range(5):
        enviar_mensagem_whatsapp(numero_whatsapp, f"Teste {i+1}", numero_whatsapp)
        status["mensagens_enviadas"] += 1
    
    # Passo 3: Esperar respostas (72h)
    # ... lógica de aguardo
    
    # Passo 4: Calcular score
    status["score_saude"] = calcular_saude_numero(numero_whatsapp)
    
    if status["score_saude"] > 80:
        status["pronto_para_campanhas"] = True
    
    return status
```

## ✅ Checklist Implementação

- [ ] Conexão Evolution API configurada
- [ ] Criar/conectar instâncias WhatsApp
- [ ] Enviar mensagens funcionando
- [ ] Receber mensagens (webhook)
- [ ] Chatbot inteligente
- [ ] Maturador de números
- [ ] Análise de conversas
- [ ] Templates de resposta
- [ ] Integração com CRM
