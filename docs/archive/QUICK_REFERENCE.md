# ⚡ ParisCred - Quick Reference Guide

## 📍 Where Am I?

You're working on **ParisCred Intelligence** - a SaaS platform for credit consignment with WhatsApp integration.

**Current Status:** 65% done - Core backend working, waiting on WhatsApp connection.

---

## 🎯 Files You Should Know

### Critical Files (Edit These)
```
app_novo.py          → Main Flask app (520 lines) - PRODUCTION VERSION
database.py          → SQLite + ORM classes (450 lines)
config.py            → Settings (4 lines - TOO SHORT!)
migration.py         → Initialize database
templates/*.html     → Frontend pages (7 files)
requirements.txt     → Dependencies (INCOMPLETE - missing bcrypt!)
```

### Files to IGNORE (Legacy/Test)
```
app.py              → OLD in-memory version (ignore this)
teste_*.py          → Test files (helpful but not critical)
CONECTAR_WHATSAPP*.py → Multiple versions (use FINAL.py)
descobrir_*.py      → Discovery scripts (can delete)
```

---

## 🚀 Get Started in 5 Minutes

### 1. Fix Dependencies
```bash
cd C:\ParisCred_Intelligence

# IMPORTANT: requirements.txt is incomplete!
# Add these lines:
# bcrypt>=4.1.0
# gunicorn>=21.0.0

pip install -r requirements.txt
```

### 2. Set Up Database
```bash
python migration.py
# Creates app.db with initial users/campaigns
```

### 3. Start Evolution API (Docker)
```bash
docker-compose up evolution-api
# Listens on localhost:8080
```

### 4. Connect WhatsApp (Important!)
```bash
python CONECTAR_WHATSAPP_FINAL.py
# Connects 3 WhatsApp instances
# Scan QR codes with your phone
```

### 5. Run Flask App
```bash
python app_novo.py
# Visits http://localhost:5000
# Login: admin@pariscred.com / Admin@2025
```

---

## 🗄️ Database Quick Reference

### 3 Tables
```
usuarios
  email (PRIMARY KEY) → User email/username
  nome → Display name
  senha_hash → Bcrypt hashed password (NOT plain!)
  role → 'admin' or 'vendedor'
  ativo → Boolean (soft delete flag)

campanhas
  id → Auto-increment campaign ID
  nome, descricao → Campaign info
  status → 'rascunho' | 'disparado'
  beneficiarios_json → List of phone numbers
  criador → Which user owns this campaign
  
historico
  campanha_id → Which campaign was executed
  usuario → Who ran it
  total_beneficiarios → Count of recipients
  resultados_json → Results of sending
```

### 4 ORM Classes (Use These in Code)
```python
Database() → Context manager for DB connections
UsuariosDB → User CRUD + password verification
CampanhasDB → Campaign CRUD + JSON handling
HistoricoDB → Log campaign executions
```

---

## 🔌 API Endpoints (Quick List)

### Public
- GET `/login`
- POST `/login` - authenticate
- GET `/logout`
- GET `/api/health` - check if running

### User (Any Authenticated User)
- GET `/dashboard` - HTML page
- GET `/api/usuario` - your data
- GET `/api/stats` - your statistics

### Campaigns (Any Authenticated User)
- GET `/api/campanhas` - list your campaigns
- POST `/api/campanhas` - create campaign
- PUT `/api/campanhas/<id>` - edit campaign
- DELETE `/api/campanhas/<id>` - delete (draft only)
- POST `/api/campanhas/<id>/disparar` - SEND MESSAGES

### Admin Only
- GET `/admin` - admin dashboard
- GET `/api/admin/usuarios` - list all users
- POST `/api/admin/usuarios` - create user
- PUT/DELETE `/api/admin/usuarios/<email>` - edit/remove user
- GET `/api/admin/historico` - all execution logs

---

## 🔐 Authentication

### Login Flow
```
User enters email + password
    ↓
UsuariosDB.verificar_senha() → bcrypt.checkpw()
    ↓
If match: session['usuario'] = email
    ↓
Redirect to /dashboard
    ↓
@requer_login decorator checks session
    ↓
Access granted ✓
```

### Test Accounts
```
Admin:
  Email: admin@pariscred.com
  Password: Admin@2025
  Access: All admin functions

Seller:
  Email: vendedor1@pariscred.com
  Password: Vendedor@123
  Access: Own campaigns only
```

### Soft Delete (Important!)
- Deleted users/campaigns aren't removed
- Just marked `ativo = 0`
- Can be recovered (WHERE ativo = 1 checks)

---

## 📱 WhatsApp Integration (Evolution API)

### How It Works
1. Evolution API runs in Docker on localhost:8080
2. Manages WhatsApp instances (can have multiple)
3. Each instance = one WhatsApp account
4. App creates instances + handles connections

### Default Instances
```
Paris_01  → First WhatsApp number
Chip01    → Second WhatsApp number
Chip02    → Third WhatsApp number
```

### Key Functions
```python
evolution_criar_instancia(name)
  → Creates new instance in Evolution API
  
evolution_obter_qrcode(name)
  → Gets QR code for instance
  → Scan with phone WhatsApp
  
evolution_conectar_instancia(name)
  → Initiates connection
  → Returns QR code
  
evolution_listar_instancias()
  → Lists all instances + their status
```

### Status Values
```
desconectado → Not connected
conectando → In progress
conectado → Ready to send
aguardando_confirmacao → Waiting for user
```

---

## ⚠️ Critical Issues (Fix These First!)

### Issue 1: bcrypt Missing
```
Error: "ModuleNotFoundError: No module named 'bcrypt'"
File: database.py line 3
Fix: Add "bcrypt>=4.1.0" to requirements.txt
```

### Issue 2: Two App Versions
```
app.py → OLD (in-memory, no persistence)
app_novo.py → NEW (SQLite, persistent) ← USE THIS ONE
Fix: Delete app.py to avoid confusion
```

### Issue 3: hardcoded API Key
```
Location: app.py line 27 + app_novo.py
Value: GLOBAL_API_KEY = 'CONSIGNADO123'
Issue: Found in code (security risk)
Fix: Move to environment variables:
  export EVOLUTION_API_KEY=CONSIGNADO123
```

### Issue 4: No Database Persistence (Cloud)
```
Platform: Render.com
Issue: SQLite file deleted on restart
Current: app.db stored locally
Fix: Use PostgreSQL instead or mount volume
```

---

## 🛠️ Common Tasks

### Create New User (via API)
```bash
curl -X POST http://localhost:5000/api/admin/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@company.com",
    "nome": "New User",
    "senha": "TempPass@123",
    "role": "vendedor"
  }'
```

### Create Campaign (via API)
```bash
curl -X POST http://localhost:5000/api/campanhas \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "My Campaign",
    "descricao": "Test campaign",
    "mensagem": "Hello!",
    "beneficiarios": [
      {"numero": "5548991105801", "nome": "John"}
    ],
    "instancias": ["Paris_01"]
  }'
```

### Launch Campaign (Send Messages)
```bash
curl -X POST http://localhost:5000/api/campanhas/1/disparar
# Returns: {sucesso: true, resultados: [...]}
```

### Export Campaign History
```python
from database import HistoricoDB
history = HistoricoDB.listar_por_campanha(campanha_id=1)
for record in history:
    print(record['resultados_json'])
```

---

## 📊 Tech Stack Summary

```
Frontend:     HTML5 + CSS3 + Vanilla JavaScript
Backend:      Flask 3.0 (Python 3.11)
Database:     SQLite 3 (app.db)
Auth:         bcrypt password hashing
API Calls:    requests library (to Evolution API)
Deployment:   Gunicorn (WSGI server)
Cloud:        Render.com or Railway
```

---

## 🚀 Deployment Checklist

Before going live:

- [ ] Fix requirements.txt (bcrypt, gunicorn)
- [ ] Delete app.py (keep app_novo.py only)
- [ ] Run migration.py (initialize database)
- [ ] Set environment variables (no hardcoding)
- [ ] Connect WhatsApp instances
- [ ] Test all CRUD operations
- [ ] Test campaign launching
- [ ] Set up HTTPS certificate
- [ ] Configure database backup
- [ ] Enable rate limiting
- [ ] Set up logging/monitoring
- [ ] Push to GitHub
- [ ] Deploy to Render.com (via render.yaml)
- [ ] Test production instance
- [ ] Set up SSL renewal

---

## 🆘 Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| ModuleNotFoundError: bcrypt | Not installed | pip install bcrypt |
| "Banco de dados não conecta" | SQLite locked | Delete app.db, run migration.py |
| "QR Code não aparece" | Evolution API not running | docker-compose up evolution-api |
| "Próximo passo" msg repeated | Database schema not initialized | Run migration.py |
| 500 Server Error | Typo in app.py imports | Check database.py path |

---

## 📚 Documentation Reference

### Files in This Project
- **PROJECT_OVERVIEW.md** ← READ THIS FIRST (you are here)
- **ARCHITECTURE_DIAGRAMS.md** → System design + flows
- **STATUS_PROJETO.md** → Current progress (Portuguese)
- **GUIA_RAPIDO.md** → Step-by-step setup (Portuguese)
- **00_COMECE_AQUI.md** → Quick start (Portuguese)

### Key Code Files
- **database.py** → How to query data
- **app_novo.py** → All 29 API endpoint implementations
- **config.py** → Configuration variables
- **templates/** → HTML/frontend code

---

## 💡 Next Steps

### This Week (Critical)
1. Fix requirements.txt
2. Delete app.py
3. Run migration.py
4. Connect WhatsApp instances
5. Test endpoints

### Next Week (Important)
6. Add environment variables
7. Set up HTTPS
8. Deploy to Render.com
9. Connect to live Evolution API

### Later (Nice to Have)
10. Add CRM module
11. Add financial calculations
12. Add reporting engine
13. Mobile app

---

**Last Updated:** March 19, 2026  
**Version:** 2.0  
**Status:** ✅ Production-ready (pending final checks)
