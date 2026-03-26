# 🚀 DEPLOY DO PARIS CRED INTELLIGENCE - INSTRUÇÕES FINAIS

## ✅ Status Atual
- ✅ Projeto completo e funcional (104 arquivos)
- ✅ 4 Skills implementadas e testadas
- ✅ API com 30+ endpoints operacional
- ✅ Banco de dados SQLite criado
- ✅ Docker configurado
- ✅ Git repository local criado
- ⏳ **PRÓXIMA ETAPA: Push para GitHub + Deploy (escolha uma opção abaixo)**

---

## 🔧 OPÇÃO 1: Deploy via Render.com (Mais fácil - Recomendado)

### Passo 1: Upload Manual do Projeto no GitHub
Como o `git push` pode estar pendente, faça o upload manualmente:

1. Acesse: https://github.com/kleitonmohr02-boop/ParisCred_Intelligence
2. Clique em "Upload files" (ou "Add files" → "Upload files")
3. Arraste toda a pasta `C:\ParisCred_Intelligence` para o upload
4. Ou use GitHub Desktop (mais fácil): https://desktop.github.com
5. Commit com mensagem: "Initial project commit"

### Passo 2: Deploy no Render
1. Acesse: https://render.com/dashboard
2. Clique em "New" → "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: pariscred-intelligence
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app_novo:app --bind 0.0.0.0:$PORT`
   - **Python Version**: 3.11
5. Clique em "Deploy"
6. **Seu link será**: `https://pariscred-intelligence.onrender.com`

---

## 🔧 OPÇÃO 2: Deploy via Railway.app

### Passo 1: Git Push (Se não foi feito)
```bash
cd C:\ParisCred_Intelligence
git push -u origin main
```

### Passo 2: Railway Deploy
1. Acesse: https://railway.app/dashboard
2. Criar novo projeto
3. Import from GitHub: `ParisCred_Intelligence`
4. Railway detectará automaticamente `Procfile` e `railway.json`
5. Seu link será gerado automaticamente

---

## 🔧 OPÇÃO 3: Deploy via Heroku (Método Alternativo)

1. Instalar Heroku CLI
2. `heroku login`
3. `heroku create pariscred-intelligence`
4. `git push heroku main`

---

## 📱 Credenciais de Acesso

**Email**: admin@pariscred.com  
**Senha**: Admin@2025

**Ou use conta secundária**:  
**Email**: vendedor@pariscred.com  
**Senha**: Vendedor@123

---

## 🌐 Endpoints Principais

```
POST   /api/login                    # Fazer login
GET    /api/health                   # Verificar status
POST   /api/crm/clientes             # Criar cliente
GET    /api/crm/clientes             # Listar clientes
POST   /api/financeiro/simular       # Simular empréstimo
POST   /api/whatsapp/instancia       # Criar instância WhatsApp
GET    /api/admin/kpis               # Dashboard KPIs
```

---

## 🗂️ Estrutura de Arquivos Importantes

```
C:\ParisCred_Intelligence\
├── app_novo.py              # Aplicação principal Flask
├── skill_crm.py             # Módulo CRM
├── skill_financeiro.py      # Módulo Financeiro
├── skill_whatsapp.py        # Módulo WhatsApp
├── skill_admin.py           # Módulo Admin
├── skills_routes.py         # Rotas API (30+ endpoints)
├── database.py              # Camada de dados
├── app.db                   # Banco SQLite
├── Dockerfile               # Container Docker
├── Procfile                 # Configuração Heroku/Railway
├── render.yaml              # Configuração Render
├── requirements.txt         # Dependências Python
├── templates/               # Páginas HTML
└── .github/                 # Documentação Skills/MCP
```

---

## 🔐 Segurança em Produção

1. **Alterar pré-senha**:
   - Após fazer login, altere as senhas no banco
   - Use `bcrypt` para hash

2. **Variáveis de Ambiente**:
   - Criar `.env` com:
     ```
     DATABASE_URL=postgresql://...
     SECRET_KEY=seu-secret-key
     FLASK_ENV=production
     ```

3. **HTTPS**:
   - Render e Railway fornecem HTTPS automaticamente

---

## 📞 Links Úteis

- Render Dashboard: https://render.com/dashboard
- Railway Dashboard: https://railway.app/dashboard
- GitHub Repo: https://github.com/kleitonmohr02-boop/ParisCred_Intelligence
- Heroku: https://www.heroku.com/

---

## ❓ Troubleshooting

**Erro ao fazer push:**
```bash
# Se credenciais falham:
git credential reject
git credential approve

# Ou use GitHub CLI:
gh auth login
gh repo create ParisCred_Intelligence --public
```

**Erro ao fazer deploy:**
- Verificar `requirements.txt` tem todas as dependências
- Verificar `app_novo.py` existe
- Verificar porta é `$PORT` (dinâmica)

**App não inicia:**
- Verificar logs: `gunicorn app_novo:app --log-level debug`
- Verificar Docker: `docker build -t pariscred .`
- Testar localmente: `python app_novo.py`

---

## ✨ Próximas Etapas (Após Deploy)

1. Conectar Evolution API para WhatsApp
2. Configurar banco de dados PostgreSQL em produção
3. Adicionar autenticação 2FA
4. Integrar payment gateway (Stripe/PagSeguro)
5. Setup CI/CD com GitHub Actions

---

**STATUS**: Sistema pronto para deploy! Escolha uma opção acima e siga os passos.

🎉 **Parabéns! O Paris Cred Intelligence está pronto para ir ao ar!**
