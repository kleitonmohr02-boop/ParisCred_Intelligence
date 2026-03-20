# 🚀 GUIA DE DEPLOY - ParisCred Intelligence

## ✅ Status Atual
- ✓ Servidor Flask testado (Status 200)
- ✓ APIs funcionando (WhatsApp, Admin, Dashboard)
- ✓ Instâncias Evolution API integradas
- ✓ Autenticação implementada
- ✓ Arquivos de configuração prontos

---

## 📋 PASSO A PASSO PARA DEPLOY NO RENDER.COM

### 1️⃣ Preparar Repositório Git

```bash
cd C:\ParisCred_Intelligence

# Inicializar git (se não estiver)
git init
git add .
git commit -m "Deploy ParisCred Intelligence - Sistema Inicial"

# Criar repo no GitHub
# https://github.com/new
# Nome: pariscred-intelligence
# Fazer push:
git remote add origin https://github.com/SEU_USUARIO/pariscred-intelligence.git
git branch -M main
git push -u origin main
```

---

### 2️⃣ Conectar ao Render.com

**Passos:**
1. Ir para https://render.com
2. Fazer login com GitHub
3. Clicar em "New +" → "Web Service"
4. Conectar repositório `pariscred-intelligence`
5. Configurar:
   - **Name:** pariscred-ai
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan:** Free tier ou Starter

---

### 3️⃣ Variáveis de Ambiente

No Render, adicionar em "Environment Variables":

```
FLASK_ENV=production
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=CONSIGNADO123
SECRET_KEY=seu_secret_key_aqui
```

---

### 4️⃣ Deploy Automático

Após conectar ao Render, qualquer push para `main` fará deploy automático:

```bash
# Para fazer novo deploy:
git add .
git commit -m "Nova versão - [descrição]"
git push origin main

# Render fará deploy automaticamente
# Verificar status em https://dashboard.render.com
```

---

## 🔗 URLs de Produção

Após deploy no Render:
- **Aplicação:** https://pariscred-ai.onrender.com
- **API:** https://pariscred-ai.onrender.com/api/
- **Admin:** https://pariscred-ai.onrender.com/admin/whatsapp
- **Dashboard:** https://pariscred-ai.onrender.com/dashboard

---

## 🧪 Testar Deploy

```bash
# Testar se está online
curl https://pariscred-ai.onrender.com

# Testar login
curl -X POST https://pariscred-ai.onrender.com/login \
  -d "email=admin@pariscred.com&senha=Admin@2025"

# Testar API
curl https://pariscred-ai.onrender.com/api/whatsapp/instancias
```

---

## 📊 Monitoramento

1. **Logs:** Dashboard Render → Logs
2. **Métricas:** Render → Metrics
3. **Alerta:** Render → Alert

---

## 🔒 Segurança Para Produção

ANTES de colocar em produção:
- [ ] Mudar `SECRET_KEY` em produção
- [ ] Usar variáveis de ambiente para all secrets
- [ ] Habilitar HTTPS (Render faz automático)
- [ ] Adicionar rate limiting
- [ ] Implementar logging de segurança
- [ ] Usar banco de dados real (Firebase/PostgreSQL)

---

## 💾 Próximos Passos

1. Confirmar que tests passam localmente ✓
2. Fazer Git init e push para GitHub
3. Conectar Render.com
4. Configurar variáveis de ambiente
5. fazer deploy
6. Acessar URL pública
7. Testar endpoints
8. Adicionar domínio customizado (opcional)

---

**🎯 Meta:** Sistema online e acessível ao mundo em 30 minutos!

