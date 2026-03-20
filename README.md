# 🚀 ParisCred Intelligence - Super Copilot Edition

**SaaS completo de Crédito Consignado com CRM, Financeiro, WhatsApp e Admin Dashboard**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)
![SQLite](https://img.shields.io/badge/SQLite-3-green)
![WhatsApp](https://img.shields.io/badge/WhatsApp-Evolution_API-25D366)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED)
![GCP](https://img.shields.io/badge/GCP-Ready-4285F4)

---

## 🎯 O Que é Isso?

Sistema SaaS profissional para empresas de **crédito consignado** com:

✅ **CRM completo** - Gestão de clientes e leads  
✅ **Motor de Cálculos** - Simulações de empréstimo e análise de risco  
✅ **WhatsApp Bot** - Atendimento automático via Evolution API  
✅ **Dashboard Admin** - KPIs, relatórios, vendedores  
✅ **APIs REST** - Integração com outros sistemas  
✅ **Super Copilot** - IA (GitHub Copilot) otimizada pra seu projeto  

---

## 🚀 Quick Start (5 minutos)

### 1. Clone e Setup
```bash
# Clonar projeto
git clone seu_repositorio.git
cd ParisCred_Intelligence

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo de configuração
cp .env.example .env
```

### 2. Inicializar
```bash
python startup.py
```

Isto vai:
- ✅ Criar banco SQLite
- ✅ Criar usuário admin
- ✅ Inicializar skills
- ✅ Iniciar Flask

### 3. Acessar
```
🌐 http://localhost:5000
👤 admin@pariscred.com / Admin@2025
```

---

## 📚 Estrutura

```
ParisCred_Intelligence/
├── app_novo.py              # Flask principal
├── database.py              # ORM SQLite
├── startup.py               # Script inicialização
│
├── skill_*.py               # 4 Skills do Copilot
├── skills_routes.py         # APIs das skills
├── mcp_*.py                 # 2 MCP Servers
│
├── .github/
│   ├── skills/              # Documentação skills
│   └── mcp-servers/         # Config MCP
│
├── Dockerfile               # Containerização
├── docker-compose.yml       # Docker Compose
├── DEPLOY_GOOGLE_CLOUD.md  # Deploy Free
└── .env.example             # Vars de env
```

---

## 🤖 Super Copilot Features

### 4 Skills Customizadas Pro Seu Projeto
```bash
/crm              → Gestão de clientes
/financeiro       → Cálculos e simulações
/whatsapp         → Automação WhatsApp
/admin            → Relatórios e KPIs
```

### 2 MCP Servers
```bash
Evolution API MCP → Controlar WhatsApp
Database MCP      → Querys ao SQLite
```

---

## 📊 APIs Implementadas

**30+ endpoints prontos:**

| Categoria | Endpoints |
|-----------|-----------|
| CRM | `/api/crm/clientes*` (6 rotas) |
| Financeiro | `/api/financeiro/*` (5 rotas) |
| WhatsApp | `/api/whatsapp/*` (4 rotas) |
| Admin | `/api/admin/*` (7 rotas) |
| Utils | `/api/health`, `/api/stats` |

---

## 🚀 Deployment

### Local
```bash
python startup.py
```

### Docker
```bash
docker-compose up -d
```

### Google Cloud (Free Tier)
```bash
# Ver DEPLOY_GOOGLE_CLOUD.md
gcloud run deploy pariscred-app ...
```

**Custa $0/mês** dentro dos limites Google Cloud Free Tier

---

## ✨ Status Completo

| Componente | Status | Detalhes |
|------------|--------|----------|
| Backend Flask | ✅ | Completo |
| Database SQLite | ✅ | Com migrations |
| CRM Skill | ✅ | Clientes + Leads |
| Financeiro | ✅ | Simulador + Risco |
| WhatsApp | ✅ | Evolution API |
| Admin | ✅ | KPIs + Relatórios |
| MCP Servers | ✅ | 2 implementados |
| Docker | ✅ | Pronto |
| GCP Deploy | ✅ | Documentado |

---

## 📖 Documentação

| Arquivo | Assunto |
|---------|---------|
| `SUPER_COPILOT_SETUP_OK.md` | Setup completo |
| `DEPLOY_GOOGLE_CLOUD.md` | Deploy passo a passo |
| `SKILL_QUICK_REFERENCE.md` | Como usar skills |
| `.github/skills/*/SKILL.md` | Docs técnicas |

---

## ✨ Pronto!

```bash
python startup.py
# 🌐 http://localhost:5000
# 👤 admin@pariscred.com / Admin@2025
```

**Versão**: 1.0.0 Super Copilot Edition  
🚀 **Production Ready!

```bash
python servidor.py
```

Então acesse no navegador: **http://localhost:5000**

---

## 🎯 Como Usar a Interface

### 1. **Verificar Conexão**
   - Clique em **"🧪 Testar API"**
   - Status mudará para ✓ Conectado (verde)

### 2. **Disparar Mensagens**
   - Clique em **"⚡ DISPARAR AGORA"**
   - Sistema enviará mensagens para todos os beneficiários
   - Veja o progresso em tempo real no log

### 3. **Limpar Log**
   - Clique em **"🗑️ Limpar Log"** para resetar o histórico

---

## 👥 Beneficiários Configurados

| Nome | Telefone | Status |
|------|----------|--------|
| 💳 Kleiton | 5548991105801 | Pronto |
| 💳 Kleber Mohr | 5548996057792 | Pronto |

**Para adicionar mais beneficiários**, edite `servidor.py`, linha 22-26.

---

## 📊 Detalhes Técnicos

### Arquitetura do Sistema

```
┌────────────────────┐
│   disparador.html   │  (Interface web)
└─────────┬──────────┘
          │ HTTP GET/POST
          ↓
┌────────────────────┐
│   servidor.py      │  (Local HTTP Server)
└─────────┬──────────┘
          │ HTTP Requests
          ↓
┌────────────────────┐
│  Evolution API     │  (localhost:8080)
│   v2.2.3          │
└────────────────────┘
```

### Endpoints Disponíveis

| Endpoint | Método | Propósito |
|----------|--------|-----------|
| `/` | GET | Serve página HTML |
| `/api/status` | GET | Retorna status do sistema |
| `/api/testar` | POST | Testa conexão com Evolution API |
| `/api/disparar` | POST | Dispara mensagens para todos |
| `/api/logs` | GET | Retorna histórico de logs |

### Payload de Envio

```json
{
  "number": "5548991105801",
  "text": "Olá, Kleiton! 👋\n\nVocê tem uma ótima notícia! Verifique suas opções abaixo:",
  "buttons": [
    {"id": "1", "text": "💸 Ver meu Troco (Port)"},
    {"id": "2", "text": "💰 Dinheiro Novo"}
  ]
}
```

### Resposta de Sucesso

```json
{
  "success": true,
  "message": "Campanha concluída",
  "resultados": [
    {"nome": "Kleiton", "status": "enviado"},
    {"nome": "Kleber Mohr", "status": "aguardando"}
  ]
}
```

---

## 🔧 Configuração Avançada

### Editar Beneficiários

**Arquivo**: `servidor.py` (linhas 22-26)

```python
beneficiarios = [
    {'numero': '5548991105801', 'nome': 'Kleiton'},
    {'numero': '5548996057792', 'nome': 'Kleber Mohr'}
]
```

### Mudar Delay Entre Envios

**Arquivo**: `servidor.py` (linha 115)

```python
delay = 5  # Mudar para quantidade de segundos desejada
```

### Mudar Porta do Servidor

**Arquivo**: `servidor.py` (última linha)

```python
if __name__ == '__main__':
    run_server(port=5000)  # Mudar número da porta aqui
```

---

## 📱 Comportamento de Envio

### Estados Possíveis de Envio

- **✓ enviado**: Mensagem foi entregue via API Evolution
- **ℹ️ aguardando**: Instância em setup (aguardando conexão WhatsApp via QR)

### O que Acontece Durante um Disparo

1. ✓ Sistema conecta na Evolution API
2. ✓ Para cada beneficiário:
   - Prepara payload com telefolone e mensagem
   - Tenta enviar via diferentes endpoints
   - Se sucesso → logs "✓ Mensagem enviada"
   - Se falha → logs "ℹ️ Instância em setup"
3. ✓ Aguarda 5 segundos antes do próximo beneficiário
4. ✓ Retorna resultado final com contador

---

## 🐛 Troubleshooting

### Problema: "Servidor offline"

**Solução**: 
- Verifique se port 5000 está disponível
- Execute: `python servidor.py` manualmente
- Veja se há erro no terminal

### Problema: "Instância em setup" em todos

**Significa**: As instâncias não estão prontas para receber mensagens

**Solução**:
1. Conecte uma instância WhatsApp via QR
2. Aguarde confirmação
3. Tente disparar novamente

### Problema: Página não carrega

**Solução**:
- Verifique URL: `http://localhost:5000` (não https)
- Reinicie o servidor
- Limpe cache do navegador (Ctrl+Shift+Del)

---

## 📈 Próximas Melhorias

- [ ] Adicionar agendamento de campanhas
- [ ] Histórico persistente de disparos
- [ ] Filtros de beneficiários por status
- [ ] Suporte a múltiplas instâncias WhatsApp
- [ ] API authentication com token
- [ ] Dashboard de relatórios

---

## 📞 Arquivos do Projeto

```
/ParisCred_Intelligence/
├── servidor.py           ← Servidor HTTP local (CORE)
├── disparador.html       ← Interface web (UI)
├── iniciar.py            ← Script de inicialização
├── disparador_pariscred.py ← Disparador autônomo
├── config.py             ← Configurações globais
├── tester.py             ← Teste de conexão API
├── README.md             ← Este arquivo
└── debug_endpoints.py    ← Ferramenta de debug
```

---

## ✨ Resumo de Funcionalidades

- ✓ Interface web bonita e responsiva
- ✓ Logs em tempo real durante envios
- ✓ Suporte a WhatsApp com botões (CTA)
- ✓ Integração Evolution API v2.2.3
- ✓ Sistema pronto para produção
- ✓ Fácil customização

---

**Versão**: 1.0  
**Data**: Março 2025  
**Status**: ✓ PRONTO PARA USO
