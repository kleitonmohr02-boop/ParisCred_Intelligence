# ParisCred Intelligence - Progresso do Projeto

## Sistema SaaS para Crédito Consignado

**Data da última atualização:** 28/03/2026
**Status:** Parcialmente concluído - Próximos passos necessários

---

## O que foi implementado até agora

### ✅ Funcionalidades Concluídas

1. **Sistema de Login e Autenticação**
   - Login com usuário/senha
   - Diferentes perfis (admin, vendedor)
   - Sessão persistida

2. **Dashboard**
   - Visão geral do sistema
   - Estatísticas de clientes e vendas

3. **CRM (Gestão de Clientes)**
   - Lista de clientes
   - Adicionar/editar clientes
   - Status de evolução

4. **Módulo Financeiro**
   - Controle de margem consignável
   - Cálculos de benefício

5. **Campanhas de Marketing**
   - Envio de mensagens via WhatsApp
   - Integração com Evolution API

6. **Administração**
   - Painel admin
   - Gerenciamento de usuários

7. **Importação de Leads (NOVO)**
   - Upload de Excel (.xlsx, .xls)
   - Rota: `/importar`
   - Template: `templates/importar.html`

8. **Chat IA Coach (NOVO)**
   - Chat com inteligência artificial (Gemini)
   - Orientação sobre técnicas de venda, cálculos, taxas
   - Rota: `/coach`
   - Template: `templates/coach.html`
   - API: `api/chat-ia`

9. **Análise de Extrato (NOVO)**
   - Upload de PDF de extrato bancário
   - Análise via IA (Gemini)
   - Rota: `/extrato`
   - Template: `templates/extrato.html`
   - API: `api/analisar-extrato`

10. **Menu Atualizado**
    - Todos os templates agora têm acesso:
      - 📊 Importar Leads (`/importar`)
      - 🤖 Chat IA Coach (`/coach`)
      - 📄 Análise Extrato (`/extrato`)

---

## O que ainda falta fazer

### 🔴 Pendente - Para continuar o projeto

1. **Pipeline Kanban**
   - Visualização de pipeline no CRM
   - Colunas: Novo Lead → Em Negociação → Pendente → Finalizado
   - Arastar e soltar clientes entre estágios

2. **Testes Online**
   - Testar todas as funcionalidades no ambiente de produção
   - Verificar se a API do Gemini está funcionando

3. **Melhorias**
   - Adicionar mais dados de demonstração
   - Melhorar UX/UI
   - Relatórios avançados

---

## Como fazer o deploy

### Opção 1: Deploy Automático (Render.com)

1. Acesse: https://dashboard.render.com
2. Selecione o serviço "pariscred-intelligence"
3. Clique em "Manual Deploy" → "Deploy build"
4. Aguarde o deploy finalizar

### Opção 2: Deploy Manual

```bash
git add .
git commit -m "feat: adiciona importação, chat IA e análise de extrato"
git push origin main
```

---

## Variáveis de Ambiente

O sistema usa as seguintes variáveis:

| Variável | Descrição | Valor atual |
|----------|------------|-------------|
| `GEMINI_API_KEY` | Chave da API Google Gemini | Configurada no Render |
| `EVOLUTION_API_URL` | URL da Evolution API | http://localhost:8080 (local) |
| `EVOLUTION_API_KEY` | Chave da Evolution API | Configurada localmente |
| `SECRET_KEY` | Chave secreta do Flask | Configurada |

---

## Estrutura de Arquivos Principais

```
C:\ParisCred_Intelligence\
├── app_novo.py              # Aplicação Flask principal
├── database.py              # Gerenciamento do SQLite
├── modulo_ia.py             # Integração com Gemini
├── modulo_importacao.py     # Importação de Excel
├── render.yaml              # Configuração do Render
├── templates/               # Páginas HTML
│   ├── dashboard.html
│   ├── crm.html
│   ├── financeiro.html
│   ├── campanhas.html
│   ├── admin.html
│   ├── importar.html        # NOVO
│   ├── coach.html           # NOVO
│   └── extrato.html         # NOVO
└── PROGRESSO_PROJETO.md     # Este arquivo
```

---

## URLs do Sistema

- **Produção:** https://pariscred-intelligence.onrender.com
- **Local:** http://localhost:5000

---

## Contato do Desenvolvedor

Este documento foi criado para garantir continuidade do projeto.
Caso precise continuar, basta ler este arquivo e seguir os próximos passos.

---

*ParisCred Intelligence - Sistema de Crédito Consignado com IA*
