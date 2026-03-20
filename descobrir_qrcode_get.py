#!/usr/bin/env python3
"""Descobre como obter QR Code via API"""

import requests
import json

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'
INSTANCE = 'Paris_01'

# Testa GET com diferentes estruturas
urls = [
    # Endpoint que obtém a instância
    f'/instance',
    # Variações
    f'/instance/fetch-instances',
    f'/instance/fetchInstances', 
    f'/instance/list-instances',
    f'/instance/listInstances',
    # Com nome
    f'/api/instance/Paris_01',
    f'/api/fetch-instances/Paris_01',
    f'/fetch-instances/Paris_01',
    f'/fetchInstances/Paris_01',
    # Documentação pode estar ali
    f'/api/docs',
    f'/docs',
    f'/swagger',
]

print("=" * 70)
print("PROCURANDO ENDPOINT PARA OBTER DETALHES DE INSTÂNCIA")
print("=" * 70)

headers = {'apikey': API_KEY}

for url in urls:
    try:
        full_url = API_URL + url
        print(f"\n🔍 GET {url}")
        
        response = requests.get(full_url, headers=headers, timeout=5)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✓ SUCESSO!")
            try:
                data = response.json()
                # Se é lista de instâncias, mostra
                if isinstance(data, list):
                    print(f"   Lista com {len(data)} instâncias:")
                    for inst in data[:2]:
                        print(f"     - {inst}")
                else:
                    text = json.dumps(data, indent=2)[:400]
                    print(f"   Response: {text}")
            except:
                text = response.text[:300]
                print(f"   Response: {text[:100]}...")
        else:
            print(f"   ❌ Status {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Erro: {str(e)[:50]}")

# Tenta POST para obter QR code
print("\n\n" + "=" * 70)
print("TESTANDO POST PARA OBTER / RENOVAR QR CODE")
print("=" * 70)

post_urls = [
    f'/instance/{INSTANCE}/qrcode',
    f'/{INSTANCE}/qrcode',
    f'/instance/{INSTANCE}/fetch',
    f'/qrcode',
    f'/instance/fetch',
]

for url in post_urls:
    try:
        full_url = API_URL + url
        print(f"\n🔍 POST {url}")
        
        response = requests.post(
            full_url,
            json={'instanceName': INSTANCE},
            headers=headers,
            timeout=5
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"   ✓ SUCESSO!")
            data = response.json()
            text = json.dumps(data, indent=2)[:400]
            print(f"   Response: {text}")
        else:
            print(f"   ❌ Status {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Erro: {str(e)[:50]}")
