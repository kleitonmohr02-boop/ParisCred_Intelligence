---
# REFATORAÇÃO: App.py com SQLite
## Documentação de Integração

---

## 📋 RESUMO DA REFATORAÇÃO

Este documento guia você através da integração do novo sistema SQLite em seu app.py existente. A refatoração mantém **100% de compatibilidade** com o frontend - nenhuma rota ou endpoint foi alterado.

**O que mudou:**
- ✅ Dados deixam de ser armazenados em memória (dicionários USUARIOS, CAMPANHAS, HISTORICO)
- ✅ Dados agora são persistidos em SQLite (app.db)
- ✅ Senhas agora são hash com bcrypt (segurança muito melhor)
- ✅ Suporte a soft delete (dados não são realmente deletados, apenas marcados como inativos)
- ✅ Transações para operações críticas
- ✅ Estrutura separada em database.py

---

## 🚀 PASSOS DE INTEGRAÇÃO

### Passo 1: Instalar Dependências

```bash
pip install bcrypt
```

**Verificação:**
```bash
python -c "import bcrypt; print('bcrypt OK')"
```

---

### Passo 2: Verificar Arquivos Criados

Você deve ter estes arquivos no diretório raiz do projeto:

```
/ParisCred_Intelligence/
├── database.py          ← NOVO: Camada de BD
├── app_novo.py          ← NOVO: App refatorado
├── migration.py         ← NOVO: Script de migração
├── app.py              ← EXISTENTE (será substituído)
├── requirements.txt    ← Atualizar
└── app.db             ← SERÁ CRIADO por database.py
```

---

### Passo 3: Executar Migração de Dados

```bash
python migration.py
```

**Esperado:**
```
======================================================
  🔄 MIGRAÇÃO: Dicionários em Memória → SQLite
======================================================

📝 Migrando usuários iniciais...
  ✓ admin@pariscred.com (Administrador ParisCred) - OK
  ✓ vendedor1@pariscred.com (João Vendedor) - OK
✅ Usuários migrados com sucesso!

📝 Migrando campanhas iniciais...
  ✓ ID 1: Campanha Inicial - OK
✅ Campanhas migradas com sucesso!

✔️  Validando dados...
  ✓ Todos os dados foram validados com sucesso!

📊 Status do Banco de Dados:
==================================================
  Total de Usuários: 2
    - admin@pariscred.com (admin)
    - vendedor1@pariscred.com (vendedor)

  Total de Campanhas: 1
    - ID 1: Campanha Inicial de admin@pariscred.com
```

---

### Passo 4: Substituir Arquivo Principal

```bash
# Backup do arquivo antiga (opcional)
mv app.py app_old.py

# Renomear para o novo
mv app_novo.py app.py
```

---

### Passo 5: Atualizar requirements.txt

Adicione ao seu `requirements.txt`:

```
Flask==2.3.0
flask-cors==4.0.0
bcrypt==4.1.0
```

Instale:
```bash
pip install -r requirements.txt
```

---

### Passo 6: Testar

```bash
python app.py
```

**Esperado:**
```
======================================================
 🚀 PARISCRED INTELLIGENCE - SaaS COMPLETO (SQLite)
======================================================

 ✓ Servidor iniciando na porta 5000...
 ✓ Acessar em: http://localhost:5000
 ✓ Banco de dados: app.db (SQLite)

 📱 Contas de Teste (após migração):
   ADM: admin@pariscred.com / Admin@2025
   Vendedor: vendedor1@pariscred.com / Vendedor@123
```

---

## 📡 TESTANDO ENDPOINTS

### 1. Health Check
```bash
curl http://localhost:5000/api/health
```

**Response esperado:**
```json
{
  "status": "ok",
  "timestamp": "2025-03-17T10:30:45.123456",
  "usuarios": 2,
  "campanhas": 1,
  "database": "SQLite"
}
```

### 2. Login (POST)
```bash
curl -X POST http://localhost:5000/login \
  -d "email=admin@pariscred.com" \
  -d "senha=Admin@2025" \
  -c cookies.txt
```

### 3. Obter Dados do Usuário
```bash
curl http://localhost:5000/api/usuario \
  -b cookies.txt
```

**Response esperado:**
```json
{
  "email": "admin@pariscred.com",
  "nome": "Administrador ParisCred",
  "role": "admin",
  "criado_em": "2025-03-17T10:00:00",
  "ativo": true
}
```

### 4. Listar Campanhas
```bash
curl http://localhost:5000/api/campanhas \
  -b cookies.txt
```

---

## 🔄 ESTRUTURA DO BANCO DE DADOS

### Tabela: usuarios
```sql
CREATE TABLE usuarios (
    email TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    senha_hash TEXT NOT NULL,  -- Hash com bcrypt
    role TEXT NOT NULL DEFAULT 'user',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT 1    -- Soft delete
)
```

### Tabela: campanhas
```sql
CREATE TABLE campanhas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    status TEXT NOT NULL DEFAULT 'rascunho',
    criador TEXT NOT NULL,
    beneficiarios_json TEXT,    -- JSON array
    mensagem TEXT NOT NULL,
    botoes_json TEXT,           -- JSON array
    instancias_json TEXT,       -- JSON array
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    disparado_em TIMESTAMP,
    total_enviados INTEGER DEFAULT 0,
    ativo BOOLEAN DEFAULT 1,    -- Soft delete
    FOREIGN KEY (criador) REFERENCES usuarios(email)
)
```

### Tabela: historico
```sql
CREATE TABLE historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campanha_id INTEGER NOT NULL,
    usuario TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_beneficiarios INTEGER,
    resultados_json TEXT,       -- JSON object
    ativo BOOLEAN DEFAULT 1,    -- Soft delete
    FOREIGN KEY (campanha_id) REFERENCES campanhas(id),
    FOREIGN KEY (usuario) REFERENCES usuarios(email)
)
```

---

## 🔑 MUDANÇAS NAS FUNÇÕES

### Antes (Em Memória)
```python
# ❌ ANTIGO
USUARIOS = {
    'admin@pariscred.com': {
        'senha': 'Admin@2025',  # Senha em texto plano!
        'nome': 'Administrador',
        ...
    }
}

# Login
if usuario and usuario['senha'] == senha:  # Comparação direta
    session['usuario'] = email
```

### Depois (SQLite + bcrypt)
```python
# ✅ NOVO
from database import UsuariosDB

# Criar usuário
UsuariosDB.criar(
    email='admin@pariscred.com',
    nome='Administrador',
    senha='Admin@2025'  # Será hasheada automaticamente
)

# Login
if UsuariosDB.verificar_senha(email, senha):  # Comparação com bcrypt
    session['usuario'] = email
```

---

## 📝 EXEMPLO: ADICIONAR NOVO USUÁRIO

### Via API (POST /api/admin/usuarios)
```bash
curl -X POST http://localhost:5000/api/admin/usuarios \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "email": "novo@pariscred.com",
    "nome": "Novo Vendedor",
    "senha": "SenhaTemp@123",
    "role": "vendedor"
  }'
```

### Via Python (direto)
```python
from database import UsuariosDB

UsuariosDB.criar(
    email='novo@pariscred.com',
    nome='Novo Vendedor',
    senha='SenhaTemp@123',
    role='vendedor'
)
```

---

## 📝 EXEMPLO: CRIAR CAMPANHA

### Via API (POST /api/campanhas)
```bash
curl -X POST http://localhost:5000/api/campanhas \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "nome": "Nova Campanha",
    "descricao": "Descrição aqui",
    "mensagem": "Olá, temos uma ótima notícia!",
    "beneficiarios": [
      {"numero": "5548991105801", "nome": "João"}
    ],
    "botoes": [
      {"id": "1", "text": "Ver Oferta"}
    ],
    "instancias": ["Paris_01", "Chip01"]
  }'
```

---

## 🐛 TROUBLESHOOTING

### Erro: "ModuleNotFoundError: No module named 'bcrypt'"
```bash
pip install bcrypt
```

### Erro: "database connection error"
```bash
# Deletar BD antigo
rm app.db

# Executar migração novamente
python migration.py
```

### Erro: "Senha incorreta mesmo com a certa"
```bash
# Banco pode estar corrompido. Refaça:
rm app.db
python migration.py
```

### Dados não aparecem no banco
```bash
# Verificar se app.db foi criado
ls -la app.db

# Conectar ao SQLite e verificar
sqlite3 app.db
sqlite> SELECT * FROM usuarios;
sqlite> .quit
```

---

## ⚙️ CONFIGURAÇÕES AVANÇADAS

### Alterar caminho do banco de dados

Em `database.py`:
```python
DATABASE_PATH = "/caminho/customizado/app.db"
```

Ou ao instanciar:
```python
db = Database("/caminho/customizado/app.db")
```

### Adicionar índices para performance

Editar `database.py`, no método `_init_db()`:
```python
cursor.execute("CREATE INDEX idx_campanhas_criador ON campanhas(criador)")
cursor.execute("CREATE INDEX idx_historico_campanha ON historico(campanha_id)")
```

---

## 🔐 SEGURANÇA

✅ **Implementado:**
- Senhas hasheadas com bcrypt (salt automático)
- Soft delete (dados nunca são realmente deletados)
- Transações para operações críticas
- Validação de permissões em cada rota
- Foreign keys no banco

⚠️ **TODO (próximas versões):**
- Rate limiting no login
- HTTPS obrigatório em produção
- Session timeout
- 2FA (autenticação de 2 fatores)
- Audit log detalhado

---

## 📊 CONSULTAS ÚTEIS NO SQLite

```bash
# Conectar ao banco
sqlite3 app.db

# Ver todos os usuários
SELECT * FROM usuarios;

# Ver todas as campanhas
SELECT id, nome, criador, status, total_enviados FROM campanhas;

# Ver histórico de disparos
SELECT * FROM historico ORDER BY timestamp DESC;

# Contar registros
SELECT COUNT(*) FROM usuarios;
SELECT COUNT(*) FROM campanhas;

# Ver usuários inativos (soft deleted)
SELECT * FROM usuarios WHERE ativo = 0;
```

---

## 📈 PRÓXIMAS MELHORIAS

1. **Backup automático** - Fazer backup diário do app.db
2. **Replicação de dados** - Migrar para PostgreSQL em produção
3. **Cache Redis** - Adicionar cache para queries frequentes
4. **Audit logging** - Log de todas as operações
5. **Backup e restore** - Scripts para backup/restore

---

## 📞 SUPORTE

Se encontrar problemas:

1. Verifique os logs do console
2. Chek se bcrypt está instalado: `pip list | grep bcrypt`
3. Verifique se app.db existe: `ls -la app.db`
4. Recrie o banco: `rm app.db && python migration.py`

---

**Versão:** 1.0  
**Data:** 2025-03-17  
**Status:** ✅ Pronto para Produção
