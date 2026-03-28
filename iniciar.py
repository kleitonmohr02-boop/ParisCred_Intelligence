"""
ParisCred Intelligence - Script de Inicialização
Execute: python iniciar.py
"""

import os
import sys

print("="*60)
print("  PARISCREDE INTELLIGENCE - INICIANDO")
print("="*60)

# Verificar dependências
print("\n[1/4] Verificando dependências...")
try:
    import flask
    import bcrypt
    import requests
    print("   ✓ Dependências OK")
except ImportError as e:
    print(f"   ✗ Erro: {e}")
    print("   Execute: pip install -r requirements.txt")
    sys.exit(1)

# Verificar banco
print("\n[2/4] Verificando banco de dados...")
if os.path.exists('app.db'):
    print("   ✓ Banco SQLite encontrado")
else:
    print("   ✗ Banco não encontrado")
    print("   Execute: python migration.py")
    sys.exit(1)

# Verificar templates
print("\n[3/4] Verificando templates...")
if os.path.exists('templates'):
    print("   ✓ Templates OK")
else:
    print("   ✗ Templates não encontrados")
    sys.exit(1)

# Iniciar Flask
print("\n[4/4] Iniciando servidor...")
print("\n" + "="*60)
print("  ACESSE: http://localhost:5000")
print("  ADMIN:  admin@pariscred.com / Admin@2025")
print("  VENDEDOR: vendedor@pariscred.com / Vendedor@123")
print("="*60 + "\n")

from app_novo import app
app.run(host='0.0.0.0', port=5000, debug=True)
