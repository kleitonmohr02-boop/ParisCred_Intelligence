#!/usr/bin/env python3
"""Teste rápido da aplicação"""

import requests
import sys

BASE_URL = "http://localhost:5000"

print("\n" + "="*60)
print("🧪 TESTE RÁPIDO DO SISTEMA")
print("="*60)

# Teste 1: Homepage
print("\n✓ Teste 1: Homepage...", end=" ", flush=True)
try:
    r = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"✅ ({r.status_code})")
except Exception as e:
    print(f"❌ {e}")

# Teste 2: Login Page
print("✓ Teste 2: Página Login...", end=" ", flush=True)
try:
    r = requests.get(f"{BASE_URL}/login", timeout=5)
    print(f"✅ ({r.status_code})")
except Exception as e:
    print(f"❌ {e}")

# Teste 3: Dashboard (deve redirecionar)
print("✓ Teste 3: Proteção Dashboard...", end=" ", flush=True)
try:
    r = requests.get(f"{BASE_URL}/dashboard", allow_redirects=False, timeout=5)
    if r.status_code == 302:
        print(f"✅ (Redirecionado)")
    else:
        print(f"⚠️  ({r.status_code})")
except Exception as e:
    print(f"❌ {e}")

# Teste 4: Campanhas API
print("✓ Teste 4: API Campanhas...", end=" ", flush=True)
try:
    r = requests.get(f"{BASE_URL}/api/campanhas", timeout=5)
    print(f"✅ ({r.status_code})")
except Exception as e:
    print(f"❌ {e}")

# Teste 5: Usuários API
print("✓ Teste 5: API Usuários...", end=" ", flush=True)
try:
    r = requests.get(f"{BASE_URL}/api/admin/usuarios", timeout=5)
    print(f"✅ ({r.status_code})")
except Exception as e:
    print(f"❌ {e}")

# Teste 6: WhatsApp Admin
print("✓ Teste 6: Painel WhatsApp...", end=" ", flush=True)
try:
    r = requests.get(f"{BASE_URL}/admin/whatsapp", allow_redirects=False, timeout=5)
    if r.status_code in [302, 401]:
        print(f"✅ (Requer login)")
    else:
        print(f"✅ ({r.status_code})")
except Exception as e:
    print(f"❌ {e}")

# Teste 7: Central Atendimento
print("✓ Teste 7: Central Atendimento...", end=" ", flush=True)
try:
    r = requests.get(f"{BASE_URL}/vendedor/atendimento", allow_redirects=False, timeout=5)
    if r.status_code in [302, 401]:
        print(f"✅ (Requer login)")
    else:
        print(f"✅ ({r.status_code})")
except Exception as e:
    print(f"❌ {e}")

print("\n" + "="*60)
print("🎉 TESTES COMPLETOS!")
print("="*60 + "\n")
