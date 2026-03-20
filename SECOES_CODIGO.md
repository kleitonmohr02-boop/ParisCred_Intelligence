# 📝 SEÇÕES DE CÓDIGO A SUBSTITUIR NO app.py

Este documento mostra EXATAMENTE quais seções do app.py original devem ser substituídas.

---

## SEÇÃO 1: Imports

### ❌ REMOVER (linhas 1-16 do app.py original)
```python
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import requests
import json
from datetime import datetime
import secrets
import os
```

### ✅ SUBSTITUIR POR
```python
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
from datetime import datetime
import secrets
import os

# Importar funções do database
from database import (
    Database,
    UsuariosDB,
    CampanhasDB,
    HistoricoDB
)
```

---

## SEÇÃO 2: Inicialização

### ❌ REMOVER (linhas 17-26 do app.py original)
```python
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# ============================================================
# DATABASE SIMULADO (Será expandido com Firebase)
# ============================================================
```

### ✅ SUBSTITUIR POR
```python
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# Inicializar banco de dados na primeira execução
db = Database("app.db")
```

---

## SEÇÃO 3: Dicionários em Memória

### ❌ REMOVER (linhas 27-70 do app.py original)
```python
# Usuários do sistema
USUARIOS = {
    'admin@pariscred.com': {
        'senha': 'Admin@2025',
        'nome': 'Administrador ParisCred',
        'role': 'admin',
        'criado_em': '2025-01-01',
        'ativo': True
    },
    'vendedor1@pariscred.com': {
        'senha': 'Vendedor@123',
        'nome': 'João Vendedor',
        'role': 'vendedor',
        'criado_em': '2025-01-15',
        'ativo': True
    }
}

# Campanhas criadas
CAMPANHAS = {
    'camp001': {
        'id': 'camp001',
        'nome': 'Campanha Inicial',
        # ... resto dos dados
    }
}

# Histórico de disparos
HISTORICO = []
```

### ✅ SUBSTITUIR POR
```python
# REMOVIDO - Dados agora estão no SQLite
# Execute: python migration.py para popular o banco
```

---

## SEÇÃO 4: Helper Functions

### ❌ REMOVER (linhas 71-97 do app.py original)
```python
def requer_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def requer_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        
        usuario = USUARIOS.get(session['usuario'])
        if not usuario or usuario['role'] != 'admin':
            return jsonify({'erro': 'Acesso negado'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def obter_usuario_atual():
    if 'usuario' not in session:
        return None
    return USUARIOS.get(session['usuario'])
```

### ✅ SUBSTITUIR POR (no app_novo.py já está)
```python
def requer_login(f):
    """Decorator para proteger rotas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def requer_admin(f):
    """Decorator para proteger rotas ADM"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        
        usuario = UsuariosDB.obter(session['usuario'])
        if not usuario or usuario['role'] != 'admin':
            return jsonify({'erro': 'Acesso negado'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def obter_usuario_atual():
    """Retorna dados do usuário logado"""
    if 'usuario' not in session:
        return None
    return UsuariosDB.obter(session['usuario'])


def usuario_para_json(usuario):
    """Converte objeto usuário para JSON, removendo dados sensíveis"""
    if not usuario:
        return None
    
    return {
        'email': usuario['email'],
        'nome': usuario['nome'],
        'role': usuario['role'],
        'criado_em': usuario['criado_em'],
        'ativo': usuario['ativo']
    }


def campanha_para_json(campanha):
    """Converte campanha para JSON"""
    if not campanha:
        return None
    
    return {
        'id': campanha['id'],
        'nome': campanha['nome'],
        'descricao': campanha['descricao'],
        'status': campanha['status'],
        'criador': campanha['criador'],
        'beneficiarios': campanha['beneficiarios_json'],
        'mensagem': campanha['mensagem'],
        'botoes': campanha['botoes_json'],
        'instancias': campanha['instancias_json'],
        'criado_em': campanha['criado_em'],
        'disparado_em': campanha['disparado_em'],
        'total_enviados': campanha['total_enviados']
    }
```

---

## SEÇÃO 5: Rota de Login

### ❌ REMOVER (linhas 140-155 do app.py original)
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        senha = request.form.get('senha', '')
        
        usuario = USUARIOS.get(email)
        
        if usuario and usuario['senha'] == senha and usuario['ativo']:
            session['usuario'] = email
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', erro='Email ou senha incorretos')
    
    return render_template('login.html')
```

### ✅ SUBSTITUIR POR
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        senha = request.form.get('senha', '')
        
        # Verificar credenciais
        if UsuariosDB.verificar_senha(email, senha):
            usuario = UsuariosDB.obter(email)
            if usuario and usuario['ativo']:
                session['usuario'] = email
                return redirect(url_for('dashboard'))
        
        return render_template('login.html', erro='Email ou senha incorretos')
    
    return render_template('login.html')
```

---

## SEÇÃO 6: Rota de API usuario

### ❌ REMOVER (linhas 165-173 do app.py original)
```python
@app.route('/api/usuario')
@requer_login
def api_usuario():
    usuario = obter_usuario_atual()
    return jsonify({
        'email': session['usuario'],
        'nome': usuario['nome'],
        'role': usuario['role'],
        'criado_em': usuario['criado_em']
    })
```

### ✅ SUBSTITUIR POR
```python
@app.route('/api/usuario')
@requer_login
def api_usuario():
    """Retorna dados do usuário logado"""
    usuario = obter_usuario_atual()
    return jsonify(usuario_para_json(usuario))
```

---

## SEÇÃO 7: Rota de Stats

### ❌ REMOVER (linhas 175-198 do app.py original)
```python
@app.route('/api/stats')
@requer_login
def api_stats():
    usuario = obter_usuario_atual()
    
    if usuario['role'] == 'admin':
        return jsonify({
            'total_usuarios': len(USUARIOS),
            'total_campanhas': len(CAMPANHAS),
            'total_disparos': len(HISTORICO),
            'usuarios_ativos': sum(1 for u in USUARIOS.values() if u['ativo']),
            'campanhas_ativas': sum(1 for c in CAMPANHAS.values() if c['status'] == 'ativo')
        })
    else:
        campanhas_users = [c for c in CAMPANHAS.values() if c['criador'] == session['usuario']]
        return jsonify({
            'total_campanhas': len(campanhas_users),
            'total_disparos': sum(c['total_enviados'] for c in campanhas_users),
            'campanhas_ativas': sum(1 for c in campanhas_users if c['status'] == 'ativo')
        })
```

### ✅ SUBSTITUIR POR
```python
@app.route('/api/stats')
@requer_login
def api_stats():
    """Retorna estatísticas do usuário/sistema"""
    usuario = obter_usuario_atual()
    
    if usuario['role'] == 'admin':
        usuarios = UsuariosDB.listar_todos()
        campanhas = CampanhasDB.listar_todas()
        
        return jsonify({
            'total_usuarios': len(usuarios),
            'total_campanhas': len(campanhas),
            'total_disparos': sum(c['total_enviados'] for c in campanhas),
            'usuarios_ativos': len(usuarios),
            'campanhas_ativas': sum(1 for c in campanhas if c['status'] == 'disparado')
        })
    else:
        campanhas_users = CampanhasDB.listar_por_criador(session['usuario'])
        return jsonify({
            'total_campanhas': len(campanhas_users),
            'total_disparos': sum(c['total_enviados'] for c in campanhas_users),
            'campanhas_ativas': sum(1 for c in campanhas_users if c['status'] == 'disparado')
        })
```

---

## SEÇÃO 8: Rotas de Campanhas (GET/POST)

### ❌ REMOVER (linhas 206-250 do app.py original)
```python
@app.route('/api/campanhas', methods=['GET', 'POST'])
@requer_login
def api_campanhas():
    usuario = obter_usuario_atual()
    
    if request.method == 'GET':
        if usuario['role'] == 'admin':
            lista = list(CAMPANHAS.values())
        else:
            lista = [c for c in CAMPANHAS.values() if c['criador'] == session['usuario']]
        
        return jsonify(lista)
    
    elif request.method == 'POST':
        data = request.json
        
        camp_id = f"camp{len(CAMPANHAS) + 1:03d}"
        
        nova_campanha = {
            'id': camp_id,
            'nome': data.get('nome', 'Nova Campanha'),
            # ... resto dos dados
        }
        
        CAMPANHAS[camp_id] = nova_campanha
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Campanha "{nova_campanha["nome"]}" criada com sucesso!',
            'campanha': nova_campanha
        }), 201
```

### ✅ SUBSTITUIR POR
```python
@app.route('/api/campanhas', methods=['GET', 'POST'])
@requer_login
def api_campanhas():
    """API para CRUD de campanhas"""
    usuario = obter_usuario_atual()
    
    if request.method == 'GET':
        if usuario['role'] == 'admin':
            lista = CampanhasDB.listar_todas()
        else:
            lista = CampanhasDB.listar_por_criador(session['usuario'])
        
        return jsonify([campanha_para_json(c) for c in lista])
    
    elif request.method == 'POST':
        data = request.json
        
        campanha_id = CampanhasDB.criar(
            nome=data.get('nome', 'Nova Campanha'),
            descricao=data.get('descricao', ''),
            criador=session['usuario'],
            mensagem=data.get('mensagem', ''),
            beneficiarios=data.get('beneficiarios', []),
            botoes=data.get('botoes', []),
            instancias=data.get('instancias', ['Paris_01'])
        )
        
        if campanha_id:
            nova_campanha = CampanhasDB.obter(campanha_id)
            return jsonify({
                'sucesso': True,
                'mensagem': f'Campanha "{nova_campanha["nome"]}" criada com sucesso!',
                'campanha': campanha_para_json(nova_campanha)
            }), 201
        else:
            return jsonify({'erro': 'Erro ao criar campanha'}), 500
```

---

## SEÇÃO 9: Rota de Detalhes da Campanha (GET/PUT/DELETE)

### ❌ REMOVER (linhas 252-291 do app.py original - muito longo)

### ✅ SUBSTITUIR POR (veja app_novo.py linhas 245-299)

---

## SEÇÃO 10: Rota de Disparo

### ❌ REMOVER (linhas 293-341 do app.py original)

### ✅ SUBSTITUIR POR (veja app_novo.py linhas 313-369)

---

## SEÇÃO 11: Rotas Admin

### ❌ REMOVER (linhas 343-427 do app.py original - todas as rotas admin que acessam USUARIOS/CAMPANHAS/HISTORICO)

### ✅ SUBSTITUIR POR (veja app_novo.py linhas 378-497)

---

## RESUMO

A forma mais fácil é:

1. **Copie todo o conteúdo de `app_novo.py`**
2. **Sobrescreva todo o `app.py` com ele**
3. **Mantenha apenas os templates e static files**

Alternativamente, substitua as seções acima uma por uma.

---

## Teste Cada Seção

Após cada substituição, teste:

```bash
python app.py
# Verifique se não há erros de syntax
```

Depois teste cada rota no navegador ou com curl.
