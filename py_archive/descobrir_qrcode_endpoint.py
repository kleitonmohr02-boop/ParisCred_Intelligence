#!/usr/bin/env python3
"""Descobre o endpoint correto para obter QR Code de instância existente"""

import requests
import json

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'
INSTANCE_NAME = 'Paris_01'

endpoints = [
    f'/instance/{INSTANCE_NAME}/qrcode',
    f'/{INSTANCE_NAME}/qrcode',
    f'/qrcode/{INSTANCE_NAME}',
    f'/instance/{INSTANCE_NAME}',
    f'/{INSTANCE_NAME}',
    f'/instance/{INSTANCE_NAME}/status',
    f'/{INSTANCE_NAME}/status',
    f'/instance/{INSTANCE_NAME}/fetch',
    f'/{INSTANCE_NAME}/fetch',
    f'/instance/fetch-instances/{INSTANCE_NAME}',
    f'/manager',
    f'/info',
]

print("=" * 70)
print(f"PROCURANDO ENDPOINT PARA QR CODE DE {INSTANCE_NAME}")
print("=" * 70)

headers = {'apikey': API_KEY}

for endpoint in endpoints:
    try:
        url = API_URL + endpoint
        print(f"\n🔍 Testando: GET {endpoint}")
        
        response = requests.get(url, headers=headers, timeout=5)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✓ SUCESSO!")
            try:
                data = response.json()
                print(f"   Response (primeiros 500 chars):")
                print(json.dumps(data, indent=2)[:500])
            except:
                print(f"   Response (text): {response.text[:300]}")
        elif response.status_code in [400, 403]:
            print(f"   ⚠️  {response.status_code} - pode ser auth ou estado")
            try:
                data = response.json()
                print(f"   Error: {json.dumps(data, indent=2)[:200]}")
            except:
                print(f"   Text: {response.text[:200]}")
        else:
            print(f"   ❌ {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Erro: {str(e)[:60]}")

print("\n" + "=" * 70)
print("PROCURANDO ENDPOINT PARA DELETE")
print("=" * 70)

delete_endpoints = [
    f'/instance/{INSTANCE_NAME}/delete',
    f'/{INSTANCE_NAME}/delete',
    f'/instance/{INSTANCE_NAME}',
    f'/{INSTANCE_NAME}',
    f'/instance/delete/{INSTANCE_NAME}',
    f'/delete/{INSTANCE_NAME}',
]

for endpoint in delete_endpoints:
    try:
        url = API_URL + endpoint
        print(f"\n🔍 Testando: DELETE {endpoint}")
        
        response = requests.delete(url, headers=headers, timeout=5)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print(f"   ✓ SUCESSO!")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}")
                except:
                    print(f"   Response: {response.text[:200]}")
        else:
            print(f"   {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Erro: {str(e)[:60]}")
