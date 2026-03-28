#!/usr/bin/env python3
"""Teste rápido da integração Evolution API"""

import requests
import json

BASE_URL = "http://localhost:5000"
EVOLUTION_API = "http://localhost:8080"

print("\n" + "="*70)
print("🧪 TESTE: INTEGRAÇÃO COM EVOLUTION API")
print("="*70)

# 1. Testar Evolution API
print("\n1️⃣  Testando Evolution API...")
try:
    r = requests.get(EVOLUTION_API, timeout=5)
    data = r.json()
    print(f"   ✅ Evolution API versão: {data.get('version')}")
    print(f"   ✅ Status: {data.get('message')}")
except Exception as e:
    print(f"   ❌ Evolution API offline: {e}")
    exit(1)

# 2. Testar endpoint de instâncias
print("\n2️⃣  Testando endpoint /api/whatsapp/instancias...")
try:
    session = requests.Session()
    
    # Fazer login
    r_login = session.post(f"{BASE_URL}/login", data={
        'email': 'admin@pariscred.com',
        'senha': 'Admin@2025'
    })
    
    # Buscar instâncias
    r = session.get(f"{BASE_URL}/api/whatsapp/instancias", timeout=10)
    
    if r.status_code == 200:
        instancias = r.json()
        print(f"   ✅ Instâncias obtidas: {len(instancias)}")
        for inst in instancias[:3]:  # Mostrar primeiras 3
            nome = inst.get('instance', {}).get('instanceName', 'N/A')
            status = inst.get('instance', {}).get('instanceStatus', 'N/A')
            print(f"      - {nome}: {status}")
    else:
        print(f"   ❌ Status {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ Erro: {str(e)[:100]}")

# 3. Testar endpoint de conectar QR Code
print("\n3️⃣  Testando endpoint /api/whatsapp/conectar-qrcode...")
try:
    r = session.post(f"{BASE_URL}/api/whatsapp/conectar-qrcode", 
        json={'instancia_nome': 'Chip01'},
        timeout=10
    )
    
    if r.status_code == 200:
        data = r.json()
        print(f"   ✅ Conexão iniciada: {data.get('mensagem')}")
    else:
        print(f"   ❌ Status {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ Erro: {str(e)[:100]}")

print("\n" + "="*70)
print("✅ TESTES CONCLUÍDOS!")
print("="*70)
print("\n📝 Próximo passo:")
print("   1. Abra: http://localhost:5000/admin/whatsapp")
print("   2. Faça login (já autenticado)")
print("   3. Clique em '📲 Conectar QR' em uma instância")
print("   4. Escaneie o QR Code com seu WhatsApp")
print("\n" + "="*70 + "\n")
