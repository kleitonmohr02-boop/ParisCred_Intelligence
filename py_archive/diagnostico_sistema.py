"""
ParisCred Intelligence - Script de Diagnóstico
Verifica o estado completo do sistema
"""

import requests
import json
import os
from datetime import datetime

print("="*70)
print(" DIAGNÓSTICO DO PARISCRED INTELLIGENCE")
print("="*70)
print()

LOG = []
LOG_FILE = "logs/diagnostico.log"

def log(msg):
    """Adiciona ao log e print"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] {msg}"
    print(linha)
    LOG.append(linha)

def save_log():
    """Salva log em arquivo"""
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    print(f"\nLog salvo em: {LOG_FILE}")

# ============================================================
# 1. VERIFICAR EVOLUTION API
# ============================================================
log("="*50)
log("1. VERIFICANDO EVOLUTION API")
log("="*50)

EVOLUTION_URL = "http://localhost:8080"
EVOLUTION_KEY = "CONSIGNADO123"
HEADERS = {"Content-Type": "application/json", "apikey": EVOLUTION_KEY}

try:
    response = requests.get(f"{EVOLUTION_URL}/instance/fetchInstances", headers=HEADERS, timeout=5)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            instancias = data
        else:
            instancias = data.get("value", []) if isinstance(data, dict) else []
        log(f"OK - Evolution API OK - {len(instancias)} instancia(s)")
        
        for inst in instancias:
            nome = inst.get("name", "N/A")
            status = inst.get("connectionStatus", "N/A")
            numero = inst.get("number", "não conectado")
            log(f"  - {nome}: {status} ({numero})")
    else:
        log(f"[ERRO] Evolution API retornou: {response.status_code}")
except Exception as e:
    log(f"[ERRO] Evolution API ERRO: {e}")

log("")

# ============================================================
# 2. VERIFICAR BANCO DE DADOS
# ============================================================
log("="*50)
log("2. VERIFICANDO BANCO DE DADOS")
log("="*50)

import sqlite3

db_path = "app.db"
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [r[0] for r in cursor.fetchall()]
        log(f"[OK] Banco SQLite OK - {len(tabelas)} tabelas: {tabelas}")
        
        # Contar registros
        for tabela in tabelas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            total = cursor.fetchone()[0]
            log(f"  - {tabela}: {total} registro(s)")
        
        conn.close()
    except Exception as e:
        log(f"[ERRO] Banco SQLite ERRO: {e}")
else:
    log(f"[ERRO] Banco SQLite NÃO ENCONTRADO: {db_path}")
    log("  O app está rodando em MODO DEMONSTRAÇÃO (dados em memória)")

log("")

# ============================================================
# 3. VERIFICAR ARQUIVO app.py
# ============================================================
log("="*50)
log("3. VERIFICANDO app.py")
log("="*50)

app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8") as f:
        conteudo = f.read()
    
    # Verificar se usa banco de dados
    if "from database import" in conteudo or "import database" in conteudo:
        log("[OK] app.py importa módulo de banco de dados")
    else:
        log("[ERRO] app.py NÃO importa banco de dados - usa dados em MEMÓRIA")
        log("  >> MODO DEMONSTRAÇÃO ATIVO")
    
    # Verificar dados hardcoded
    if "USUARIOS = {" in conteudo:
        log("[ERRO] app.py tem USUARIOS hardcoded (demonstração)")
    if "CAMPANHAS = {" in conteudo:
        log("[ERRO] app.py tem CAMPANHAS hardcoded (demonstração)")

log("")

# ============================================================
# 4. VERIFICAR VARIÁVEIS DE AMBIENTE
# ============================================================
log("="*50)
log("4. VARIÁVEIS DE AMBIENTE")
log("="*50)

from dotenv import load_dotenv
load_dotenv()

env_vars = [
    "DATABASE_PATH",
    "DATABASE_URL", 
    "EVOLUTION_API_URL",
    "EVOLUTION_API_KEY",
    "SECRET_KEY"
]

for var in env_vars:
    valor = os.getenv(var)
    if valor:
        if "KEY" in var and len(valor) > 5:
            log(f"  {var}: {'*' * 10}{valor[-4:]}")
        else:
            log(f"  {var}: {valor}")
    else:
        log(f"  {var}: (não definido)")

log("")

# ============================================================
# 5. RESUMO
# ============================================================
log("="*50)
log("RESUMO DO DIAGNÓSTICO")
log("="*50)

tem_bd = os.path.exists(db_path)
importa_bd = "from database import" in conteudo if os.path.exists(app_path) else False

if tem_bd and importa_bd:
    log("[OK] SISTEMA COMPLETO - Banco + app integrados")
elif tem_bd and not importa_bd:
    log("AVISO: Banco existe mas app.py NAO usa!")
    log("  >> SOLUCAO: Integrar database.py no app.py")
else:
    log("AVISO: MODO DEMONSTRACAO ATIVO")
    log("  >> SOLUCAO: Criar banco de dados e integrar no app.py")

print()
save_log()

print("\n" + "="*70)
print("FIM DO DIAGNÓSTICO")
print("="*70)
