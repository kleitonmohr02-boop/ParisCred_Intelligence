# 🏗️ ParisCred Intelligence - Architecture & Flow Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER / CLIENT                         │
│  User navigates: http://localhost:5000                           │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP Requests
                             │ (GET /dashboard, POST /api/campanhas)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK APP (app_novo.py)                     │
│                      Port: 5000 (local)                          │
│                      Port: $PORT (cloud)                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Authentication Layer                                       │ │
│  │ ├─ POST /login (verify credentials)                       │ │
│  │ ├─ GET /logout (destroy session)                          │ │
│  │ └─ @requer_login decorator (session check)                │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ API Endpoints (17 unique routes)                           │ │
│  │ ├─ /api/campanhas (CRUD campaigns)                        │ │
│  │ ├─ /api/usuario (get user data)                           │ │
│  │ ├─ /api/admin/* (admin functions)                         │ │
│  │ └─ /api/health (system status)                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Business Logic                                             │ │
│  │ ├─ Campaign creation/editing                              │ │
│  │ ├─ Message dispatch (disparar)                            │ │
│  │ ├─ User management                                        │ │
│  │ └─ Evolution API integration                              │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
         │                   │
         │ (Data)            │ (API Calls)
         ▼                   ▼
    ┌──────────┐        ┌─────────────────────────┐
    │          │        │  Evolution API          │
    │ SQLite   │        │  Port: 8080 (Docker)    │
    │ app.db   │        │  API Key: CONSIGNADO123 │
    │          │        │  ┌───────────────────┐  │
    │ Tables:  │        │  │ WhatsApp Manager  │  │
    │ ├─usuarios       │  ├─ Create Instance  │  │
    │ ├─campanhas      │  ├─ Generate QR Code │  │
    │ └─historico      │  ├─ Send Messages    │  │
    │          │        │  └─ Check Status    │  │
    │ (3 TB)   │        │                     │  │
    └──────────┘        │  Connected to:      │  │
                        │  • Paris_01         │  │
                        │  • Chip01           │  │
                        │  • Chip02           │  │
                        └─────────────────────┘
                                   │
                                   │ WhatsApp
                                   │ Protocol
                                   ▼
                        ┌─────────────────────┐
                        │   WhatsApp (User    │
                        │   Phones)           │
                        │ • +5548991105801    │
                        │ • +5548996057792    │
                        └─────────────────────┘
```

---

## Authentication & Session Flow

```
┌─────────────┐
│   Login     │
│   Page      │
└──────┬──────┘
       │ User enters email + password
       └─────────────────────┐
                             ▼
                    ┌────────────────┐
                    │ POST /login    │
                    │ (Flask route)  │
                    └────────┬───────┘
                             │
                    ┌────────▼────────┐
                    │ UsuariosDB.     │
                    │ verificar_senha │
                    │ (bcrypt check)  │
                    └────────┬────────┘
                             │
             ┌───────────────┴───────────────┐
             │                               │
        ✓ MATCH                         ✗ NO MATCH
             │                               │
             ▼                               ▼
    ┌─────────────────────┐        ┌──────────────┐
    │ session['usuario']  │        │ Redirect to  │
    │ = email             │        │ /login with  │
    │ (server-side cookie)│        │ error msg    │
    └────────┬────────────┘        └──────────────┘
             │
             ▼
    ┌─────────────────────┐
    │ Redirect to         │
    │ /dashboard          │
    └────────┬────────────┘
             │
    ┌────────▼────────────┐
    │ @requer_login       │
    │ decorator checks    │
    │ if 'usuario' in     │
    │ session             │
    └────────┬────────────┘
             │
        ✓ YES
             │
             ▼
    ┌─────────────────────┐
    │ Load /dashboard     │
    │ Pass user data to   │
    │ dashboard.html      │
    └─────────────────────┘

Session Logout:
  User clicks /logout
    → session.clear()
    → Redirect to /login
    → All @requer_login endpoints now fail
```

---

## Campaign Creation & Dispatch Flow

```
┌─────────────────────────────┐
│ User fills Campaign Form    │
│ - Name                      │
│ - Description               │
│ - Message template          │
│ - Beneficiaries (numbers)   │
│ - WhatsApp instances        │
└──────────────┬──────────────┘
               │ POST /api/campanhas
               │ with JSON payload
               ▼
       ┌───────────────────┐
       │ api_campanhas()   │
       │ (POST route)      │
       └───────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ CampanhasDB.criar()  │
    │ - Insert new record  │
    │ - Convert lists to   │
    │   JSON               │
    └───────┬──────────────┘
            │
            ▼
   ┌──────────────────────┐
   │ candidatos table:    │
   │ {                    │
   │  id: 1               │
   │  nome: "Campanha X"  │
   │  status: "rascunho"  │
   │  criador: user@...   │
   │  beneficiarios_json: │
   │    "[{...},{...}]"   │
   │ }                    │
   └──────────┬───────────┘
              │
              ▼
    ┌──────────────────────────┐
    │ Return to Dashboard      │
    │ User sees campaign in    │
    │ list (status=rascunho)   │
    └──────────┬───────────────┘
               │ User clicks
               │ "DISPARAR AGORA"
               │
               ▼
    ┌────────────────────────────┐
    │ POST /api/campanhas/{id}/  │
    │ disparar (launch endpoint) │
    └───────┬────────────────────┘
            │
            ▼
   ┌────────────────────────────┐
   │ disparar_campanha()        │
   │ - Verify permissions       │
   │ - Check beneficiaries list │
   │ - Loop through each        │
   └───────┬────────────────────┘
           │
     ┌─────▼──────────────────────────────┐
     │ For each beneficiary:              │
     │                                    │
     │ ┌───────────────────────────────┐  │
     │ │ evolution_send_message()      │  │
     │ │ - Pick WhatsApp instance      │  │
     │ │ - Format message              │  │
     │ │ - Call Evolution API          │  │
     │ │ - Return: {status, timestamp} │  │
     │ └───────────────────────────────┘  │
     │                                    │
     │ Store result:                      │
     │ - enviado                          │
     │ - erro                             │
     │ - aguardando_confirmacao           │
     └─────┬──────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────┐
  │ CampanhasDB.atualizar()     │
  │ - status: 'disparado'       │
  │ - total_enviados: 10        │
  │ - disparado_em: timestamp   │
  └─────┬───────────────────────┘
        │
        ▼
  ┌──────────────────────────────┐
  │ HistoricoDB.registrar()      │
  │ - Log execution              │
  │ - Store results JSON         │
  │ - One record per dispatch    │
  └─────┬────────────────────────┘
        │
        ▼
  ┌──────────────────────────────┐
  │ Return results to browser    │
  │ {                            │
  │   sucesso: true              │
  │   mensagem: "10 enviadas..." │
  │   resultados: [{...}]        │
  │ }                            │
  └─────┬────────────────────────┘
        │
        ▼
   Dashboard updated with:
   - Campaign status: "disparado"
   - Messages count: 10
   - Timestamp: now
```

---

## Database Relationships

```
┌─────────────────────────────────────────┐
│              usuarios                   │
├─────────────────────────────────────────┤
│ email (PK)          ← String             │
│ nome                ← String             │
│ senha_hash          ← Bcrypt (not plain!)│
│ role                ← 'admin'|'vendedor' │
│ criado_em           ← Timestamp          │
│ ativo               ← Boolean (soft del) │
└─────────────────────────────────────────┘
            │
            │ 1 user :
            │ N campaigns
            │
            ▼
┌─────────────────────────────────────────┐
│              campanhas                  │
├─────────────────────────────────────────┤
│ id (PK)             ← AutoIncrement      │
│ nome                ← String             │
│ descricao           ← Text               │
│ status              ← 'rascunho'|...     │
│ criador (FK)        → usuarios.email     │
│ beneficiarios_json  ← JSON array         │
│ mensagem            ← Template text      │
│ botoes_json         ← JSON array         │
│ instancias_json     ← JSON array (WA)    │
│ criado_em           ← Timestamp          │
│ disparado_em        ← Timestamp or NULL  │
│ total_enviados      ← Integer count      │
│ ativo               ← Boolean (soft del) │
└─────────────────────────────────────────┘
            │
            │ 1 campaign :
            │ N executions
            │
            ▼
┌─────────────────────────────────────────┐
│              historico                  │
├─────────────────────────────────────────┤
│ id (PK)             ← AutoIncrement      │
│ campanha_id (FK)    → campanhas.id       │
│ usuario (FK)        → usuarios.email     │
│ timestamp           ← Execution time     │
│ total_beneficiarios ← Integer            │
│ resultados_json     ← Results array      │
│ ativo               ← Boolean (soft del) │
└─────────────────────────────────────────┘

PK = Primary Key
FK = Foreign Key
Soft del = Can be recovered (not truly deleted)
```

---

## API Response Patterns

### Successful Response
```json
{
    "sucesso": true,
    "mensagem": "Operação realizada com sucesso",
    "data": {
        // Response object
    }
}
```

### Error Response
```json
{
    "erro": "Descrição do erro",
    "codigo": 400
}
```

### List Response
```json
[
    {item1},
    {item2},
    {item3}
]
```

### User Response
```json
{
    "email": "admin@pariscred.com",
    "nome": "Administrador",
    "role": "admin",
    "criado_em": "2025-01-01T00:00:00",
    "ativo": true
}
```

### Campaign Response
```json
{
    "id": 1,
    "nome": "Campanha X",
    "descricao": "Descrição...",
    "status": "disparado",
    "criador": "admin@pariscred.com",
    "beneficiarios": [
        {"numero": "5548991105801", "nome": "Kleiton"},
        {"numero": "5548996057792", "nome": "Kleber"}
    ],
    "mensagem": "Olá! Você tem uma ótima notícia!",
    "botoes": [
        {"id": "1", "text": "💸 Ver meu Troco"},
        {"id": "2", "text": "💰 Dinheiro Novo"}
    ],
    "instancias": ["Paris_01", "Chip01"],
    "criado_em": "2025-03-17T10:00:00",
    "disparado_em": "2025-03-17T10:15:00",
    "total_enviados": 10
}
```

---

## File Dependencies

```
                    browser
                       │
                       │ HTTP
                       ▼
                   ┌────────────────┐
                   │ templates/     │
                   │ ├─login.html   │
                   │ ├─dashboard... │
                   │ └─admin.html   │
                   └────────┬───────┘
                            │ Jinja2 render
                            │
        ┌───────────────────▼────────────────┐
        │      app_novo.py (Main app)        │
        │                                    │
        │  imports:                         │
        │  - Flask, CORS, requests          │
        │  - database.py (models)           │
        │  - config.py (settings)           │
        └────────────────┬───────────────────┘
                         │
         ┌───────────────▼────────────┐
         │   database.py              │
         │   ├─ Database class        │
         │   ├─ UsuariosDB class      │
         │   ├─ CampanhasDB class     │
         │   └─ HistoricoDB class     │
         │                            │
         │   imports:                 │
         │   - sqlite3 (DB connector) │
         │   - bcrypt (pwd hashing)   │
         │   - json (serialization)   │
         └────────────────┬───────────┘
                          │
                          ▼
                    ┌──────────────┐
                    │   app.db     │
                    │  (SQLite)    │
                    │              │
                    │ [3 tables]   │
                    └──────────────┘


External Services:
    ▼
┌─────────────────────────┐
│ Evolution API           │
│ localhost:8080          │
│ (Docker container)      │
│                         │
│ Manages:                │
│ - WhatsApp instances    │
│ - QR codes              │
│ - Message sending       │
└─────────────────────────┘
    │
    │ WhatsApp Protocol
    │
    ▼
┌─────────────────────────┐
│ Phone WhatsApp Clients  │
│ (Registered numbers)    │
└─────────────────────────┘
```

---

## Deployment Architecture (Render.com)

```
┌──────────────────────────────────┐
│    Render.com Cloud Platform     │
│                                  │
│  ┌────────────────────────────┐  │
│  │  Push to GitHub            │  │
│  └────────────┬───────────────┘  │
│               │                  │
│               ▼                  │
│  ┌────────────────────────────┐  │
│  │ Render.com detects change  │  │
│  │ (Reads render.yaml)        │  │
│  └────────────┬───────────────┘  │
│               │                  │
│               ▼                  │
│  ┌────────────────────────────┐  │
│  │ Install Python 3.11        │  │
│  │ pip install -r requirements│  │
│  └────────────┬───────────────┘  │
│               │                  │
│               ▼                  │
│  ┌────────────────────────────┐  │
│  │ Start gunicorn             │  │
│  │ gunicorn app:app           │  │
│  │ --bind 0.0.0.0:$PORT       │  │
│  └────────────┬───────────────┘  │
│               │                  │
│               ▼                  │
│  ┌────────────────────────────┐  │
│  │ Public URL assigned        │  │
│  │ https://pariscred-ai.onrender.com  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘

Issue: SQLite database not persisted!
Need: PostgreSQL or volume mount
```

---

## Security Architecture

```
┌──────────────────────────────┐
│ Browser Cookie (Session ID)  │
└────────────────┬─────────────┘
                 │ HTTPS (production)
                 │ HTTP (local only)
                 ▼
         ┌──────────────────┐
         │ Flask Secret Key │
         │ (RSA signed)     │
         └──────────────────┘
                 │
         ┌───────▼────────┐
         │ Session data:  │
         │ usuario = email│
         └───────┬────────┘
                 │
    ┌────────────▼──────────────┐
    │ @requer_login decorator   │
    │ checks if 'usuario' exists│
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │ UsuariosDB.obter(email)   │
    │ queries database          │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │ Full user object loaded   │
    │ including password_hash   │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────┐
    │ Permission checks@requer_ │
    │ admin verifies role       │
    └────────────┬──────────────┘
                 │
            ✓ AUTHORIZED or ✗ DENIED

Password flow:
  Plain password → bcrypt.hashpw() → hash stored
  On login: bcrypt.checkpw(plain, hash) → True/False
  Never stored: plain password
```

---

## Development vs Production

```
┌─────────────────────────────────────────────────────┐
│             LOCAL DEVELOPMENT                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Flask dev server:                                  │
│  python app_novo.py                                │
│  Host: 127.0.0.1 / 0.0.0.0                        │
│  Port: 5000                                        │
│  Auto-reload: ON                                   │
│  Debug: ON                                         │
│                                                    │
│  Database: SQLite (app.db)                         │
│  Persisted: In local file                          │
│  Backups: Manual                                   │
│                                                    │
│  Evolution API: Docker (localhost:8080)            │
│  WhatsApp: Can use temp instances                  │
│                                                    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         PRODUCTION (RENDER.COM)                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Gunicorn WSGI server:                              │
│  gunicorn app:app --bind 0.0.0.0:$PORT             │
│  Host: 0.0.0.0                                     │
│  Port: $PORT (dynamic from Render)                 │
│  Auto-reload: OFF                                  │
│  Debug: OFF                                        │
│  Workers: 4+ (auto-scaling)                        │
│                                                    │
│  Database: ??? (NOT CONFIGURED!)                   │
│  ⚠️  SQLite file lost on every restart             │
│  ✅  Should use: PostgreSQL + persistent storage   │
│                                                    │
│  Evolution API: Remote                             │
│  (Must configure remote Evolution URL in env)      │
│  WhatsApp: Must have persistent instances          │
│                                                    │
│  HTTPS: Yes (Render auto-provides)                 │
│  SSL/TLS: Auto-renewed by Render                   │
│                                                    │
└─────────────────────────────────────────────────────┘

GAPS TO FIX:
  1. Production uses wrong DB (no persistence)
  2. Evolution API URL hardcoded (not env var)
  3. No rate limiting or DDoS protection
  4. No logging/monitoring configured
  5. No backup strategy
```

---

**Updated:** 2026-03-19  
**Diagrams Version:** 2.0
