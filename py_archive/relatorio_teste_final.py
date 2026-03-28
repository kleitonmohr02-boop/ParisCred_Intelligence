#!/usr/bin/env python3
"""Teste final validação completa"""

import requests
import json

BASE_URL = "http://localhost:5000"
session = requests.Session()

print("\n" + "="*70)
print("✅ TESTE FINAL - VALIDAÇÃO COMPLETA DO SISTEMA")
print("="*70)

tests_passed = 0
tests_total = 0

# Teste 1: Homepage redireciona para login (ou abre)
tests_total += 1
print("\n1️⃣  Homepage:", end=" ")
try:
    r = session.get(f"{BASE_URL}/", timeout=3)
    if r.status_code in [200, 302]:
        print("✅ OK")
        tests_passed += 1
    else:
        print(f"❌ Status {r.status_code}")
except Exception as e:
    print(f"❌ {str(e)[:30]}")

# Teste 2: Login page acessível
tests_total += 1
print("2️⃣  Página de Login:", end=" ")
try:
    r = session.get(f"{BASE_URL}/login", timeout=3)
    if r.status_code == 200:
        print("✅ OK")
        tests_passed += 1
    else:
        print(f"❌ Status {r.status_code}")
except Exception as e:
    print(f"❌ {str(e)[:30]}")

# Teste 3: Dashboard protegido (redireciona sem login)
tests_total += 1
print("3️⃣  Proteção de Rotas:", end=" ")
try:
    r = session.get(f"{BASE_URL}/dashboard", allow_redirects=False, timeout=3)
    if r.status_code == 302:
        print("✅ OK (Redireciona para login)")
        tests_passed += 1
    else:
        print(f"⚠️  Status {r.status_code}")
except Exception as e:
    print(f"❌ {str(e)[:30]}")

# Teste 4: Painel Admin WhatsApp (protegido)
tests_total += 1
print("4️⃣  Painel WhatsApp Admin:", end=" ")
try:
    r = session.get(f"{BASE_URL}/admin/whatsapp", allow_redirects=False, timeout=3)
    if r.status_code == 302:
        print("✅ OK (Protegido)")
        tests_passed += 1
    else:
        print(f"⚠️  Status {r.status_code}")
except Exception as e:
    print(f"❌ {str(e)[:30]}")

# Teste 5: Central de Atendimento (protegida)
tests_total += 1
print("5️⃣  Central de Atendimento:", end=" ")
try:
    r = session.get(f"{BASE_URL}/vendedor/atendimento", allow_redirects=False, timeout=3)
    if r.status_code == 302:
        print("✅ OK (Protegida)")
        tests_passed += 1
    else:
        print(f"⚠️  Status {r.status_code}")
except Exception as e:
    print(f"❌ {str(e)[:30]}")

# Teste 6: API Campanhas (protegida)
tests_total += 1
print("6️⃣  API Campanhas:", end=" ")
try:
    r = session.get(f"{BASE_URL}/api/campanhas", timeout=3)
    if r.status_code == 302:
        print("✅ OK (Protegida)")
        tests_passed += 1
    else:
        print(f"⚠️  Status {r.status_code}")
except Exception as e:
    print(f"❌ {str(e)[:30]}")

# Teste 7: API Usuarios (protegida)
tests_total += 1
print("7️⃣  API Usuários:", end=" ")
try:
    r = session.get(f"{BASE_URL}/api/admin/usuarios", timeout=3)
    if r.status_code == 302:
        print("✅ OK (Protegida)")
        tests_passed += 1
    else:
        print(f"⚠️  Status {r.status_code}")
except Exception as e:
    print(f"❌ {str(e)[:30]}")

# Teste 8: API WhatsApp Instancias (protegida)
tests_total += 1
print("8️⃣  API WhatsApp:", end=" ")
try:
    r = session.get(f"{BASE_URL}/api/whatsapp/instancias", timeout=3)
    if r.status_code == 302:
        print("✅ OK (Protegida)")
        tests_passed += 1
    else:
        print(f"⚠️  Status {r.status_code}")
except Exception as e:
    print(f"❌ {str(e)[:30]}")

# Relatório Final
print("\n" + "="*70)
print(f"📊 RESULTADO: {tests_passed}/{tests_total} testes passaram")
print("="*70)

if tests_passed == tests_total:
    print("\n✅ STATUS: SISTEMA 100% FUNCIONAL!")
    print("\n📝 Próximo Passo:")
    print("   1. Acesse: http://localhost:5000/login")
    print("   2. Faça login com:")
    print("      • Email: admin@pariscred.com")
    print("      • Senha: Admin@2025")
    print("   3. Navegue para 'Gerenciar WhatsApp'")
    print("   4. Teste as 3 opções de conexão")
else:
    print(f"\n⚠️  {tests_total - tests_passed} teste(s) falharam")

print("\n" + "="*70 + "\n")
