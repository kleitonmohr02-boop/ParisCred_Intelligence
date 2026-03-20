# 🚀 GUIA RÁPIDO: Integração SQLite

## Arquivos Criados

```
✅ database.py          - Camada de banco de dados com SQLite
✅ app_novo.py          - Versão refatorada do app.py
✅ migration.py         - Script para migrar dados
✅ INTEGRACAO_SQLITE.md - Documentação completa
```

---

## 5 Passos para Integrar

### 1️⃣ Instalar bcrypt
```bash
pip install bcrypt
```

### 2️⃣ Executar Migração
```bash
python migration.py
```

### 3️⃣ Substituir o app.py
```bash
mv app.py app_old.py
mv app_novo.py app.py
```

### 4️⃣ Iniciar o servidor
```bash
python app.py
```

### 5️⃣ Testar
Abra: http://localhost:5000/api/health

---

## Credenciais de Teste

```
Login: admin@pariscred.com
Senha: Admin@2025
Role: admin
```

---

## Estrutura do Código

### database.py
- `Database()` - Context manager para conexões
- `UsuariosDB` - CRUD de usuários (com bcrypt)
- `CampanhasDB` - CRUD de campanhas 
- `HistoricoDB` - CRUD de histórico

**Funções principais:**
```python
# Usuários
UsuariosDB.criar(email, nome, senha, role)
UsuariosDB.obter(email)
UsuariosDB.verificar_senha(email, senha)
UsuariosDB.listar_todos()
UsuariosDB.deletar(email)  # Soft delete

# Campanhas
CampanhasDB.criar(nome, descricao, criador, mensagem, ...)
CampanhasDB.obter(id)
CampanhasDB.listar_todas()
CampanhasDB.listar_por_criador(email)
CampanhasDB.atualizar(id, **kwargs)
CampanhasDB.deletar(id)  # Soft delete

# Histórico
HistoricoDB.registrar(campanha_id, usuario, total_beneficiarios, resultados)
HistoricoDB.obter(id)
HistoricoDB.listar_por_campanha(campanha_id)
HistoricoDB.listar_por_usuario(email)
```

### app.py (mudanças internas)
Todas as rotas permanecem iguais! Apenas a implementação mudou:

```python
# ❌ ANTES
usuario = USUARIOS.get(email)
if usuario['senha'] == senha:
    session['usuario'] = email

# ✅ DEPOIS
if UsuariosDB.verificar_senha(email, senha):
    session['usuario'] = email
```

---

## API Endpoints (Todos mantém compatibilidade)

| Método | Rota | Função |
|--------|------|--------|
| GET | `/api/health` | Health check |
| GET | `/api/usuario` | Dados do usuário logado |
| GET | `/api/stats` | Estatísticas |
| GET | `/api/campanhas` | Listar campanhas |
| POST | `/api/campanhas` | Criar campanha |
| GET | `/api/campanhas/<id>` | Detalhes de 1 campanha |
| PUT | `/api/campanhas/<id>` | Atualizar campanha |
| DELETE | `/api/campanhas/<id>` | Deletar campanha |
| POST | `/api/campanhas/<id>/disparar` | Disparar campanha |
| GET | `/api/admin/usuarios` | Listar usuários (ADM) |
| POST | `/api/admin/usuarios` | Criar usuário (ADM) |
| PUT | `/api/admin/usuarios/<email>` | Atualizar usuário (ADM) |
| DELETE | `/api/admin/usuarios/<email>` | Desativar usuário (ADM) |
| GET | `/api/admin/historico` | Ver histórico (ADM) |

---

## O que Mudou Internamente

### ✅ Senhas
- Antes: String plana no dicionário
- Depois: Hash bcrypt, muito mais seguro

### ✅ Persistência
- Antes: Dados perdidos ao reiniciar
- Depois: SQLite persiste tudo

### ✅ Exclusões
- Antes: Deletar removia do dicionário
- Depois: Soft delete marca como `ativo=0`

### ✅ Transações
- Adicionadas transações SQL para dados críticos

---

## Exemplo de Uso Direto do database.py

```python
from database import UsuariosDB, CampanhasDB, HistoricoDB

# Criar usuário
UsuariosDB.criar(
    email='novo@email.com',
    nome='Novo User',
    senha='Senha123',
    role='vendedor'
)

# Verificar senha
if UsuariosDB.verificar_senha('novo@email.com', 'Senha123'):
    print("Login OK!")

# Criar campanha
campanha_id = CampanhasDB.criar(
    nome='Campanha Teste',
    descricao='Teste',
    criador='novo@email.com',
    mensagem='Olá!',
    beneficiarios=[{'numero': '55991234567', 'nome': 'João'}],
    botoes=[{'id': '1', 'text': 'Clique aqui'}]
)

# Listar campanhas do usuário
campanhas = CampanhasDB.listar_por_criador('novo@email.com')

# Registrar disparo no histórico
HistoricoDB.registrar(
    campanha_id=campanha_id,
    usuario='novo@email.com',
    total_beneficiarios=1,
    resultados={'enviados': [...]}
)
```

---

## Rollback (Voltar para versão antiga)

Se algo der errado:

```bash
# 1. Parar o servidor (Ctrl+C)

# 2. Restaurar o app.py antigo
mv app.py app_novo_backup.py
mv app_old.py app.py

# 3. Remover banco de dados
rm app.db

# 4. Reiniciar
python app.py
```

**Nota:** Você perderá dados criados después da migração. O banco SQLite anterior é mantido como backup.

---

## Verificação Rápida

```bash
# Verificar se bcrypt está instalado
python -c "import bcrypt; print('✓ bcrypt OK')"

# Verificar se database.py carrega
python -c "from database import Database; print('✓ database.py OK')"

# Verificar se app.py inicia
python app.py
# Deve exibir mensagens de inicialização normalmente
```

---

## Arquivos Importantes

| Arquivo | Purpose |
|---------|---------|
| `database.py` | Todas as funções de BD |
| `app.py` | Aplicação Flask (rotas) |
| `app.db` | Banco SQLite (criado após migration.py) |
| `migration.py` | Script para popular o banco |
| `INTEGRACAO_SQLITE.md` | Documentação completa |

---

## Suporte

Dúvidas? Veja `INTEGRACAO_SQLITE.md` para mais detalhes, troubleshooting e exemplos avançados.
