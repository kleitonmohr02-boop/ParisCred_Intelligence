#!/usr/bin/env python3
"""Tenta descobrir o endpoint para renovar QR Code"""

import requests
import json

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'
INSTANCE = 'Chip_01'  # Use a instância que já existe

print("=" * 70)
print(f"TESTANDO ENDPOINTS PARA RENOVAR QR CODE DE: {INSTANCE}")
print("=" * 70)

headers = {'apikey': API_KEY, 'Content-Type': 'application/json'}

# Teste com GET
get_endpoints = [
    f'/instance/{INSTANCE}/qrcode/request',
    f'/instance/{INSTANCE}/qrcode',
    f'/{INSTANCE}/qrcode',
    f'/instance/qrcode/{INSTANCE}',
    f'/api/instance/{INSTANCE}/qrcode',
    f'/qrcode/request/{INSTANCE}',
    f'/requestQrCode/{INSTANCE}',
    f'/instance/{INSTANCE}/connect',
    f'/connect/{INSTANCE}',
    f'/request-qr-code/{INSTANCE}',
    f'/api/qrcode/{INSTANCE}',
]

for endpoint in get_endpoints:
    try:
        url = API_URL + endpoint
        print(f"\n🔍 GET {endpoint}")
        
        response = requests.get(url, headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✓ SUCESSO!")
            data = response.json()
            text = json.dumps(data, indent=2)[:600]
            print(f"   {text}")
        elif response.status_code in [400, 403]:
            print(f"   ⚠️  {response.status_code}: {response.text[:100]}")
            
    except Exception as e:
        pass

# Teste com POST
print("\n" + "=" * 70)
print("TESTANDO POST")
print("=" * 70)

post_endpoints = [
    f'/instance/{INSTANCE}/qrcode/request',
    f'/instance/{INSTANCE}/qrcode',
    f'/instance/requestQrCode',
    f'/request-qr-code',
    f'/qrcode/request',
]

for endpoint in post_endpoints:
    try:
        url = API_URL + endpoint
        payload = {'instanceName': INSTANCE}
        
        print(f"\n🔍 POST {endpoint}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"   ✓ SUCESSO!")
            data = response.json()
            text = json.dumps(data, indent=2)[:600]
            print(f"   {text}")
        elif response.status_code in [400, 403]:
            print(f"   ⚠️  {response.status_code}: {response.text[:150]}")
            
    except Exception as e:
        pass

# Teste com PUT
print("\n" + "=" * 70)
print("TESTANDO PUT")
print("=" * 70)

put_endpoints = [
    f'/instance/{INSTANCE}/qrcode',
    f'/instance/{INSTANCE}/connect',
    f'/request-qr-code/{INSTANCE}',
]

for endpoint in put_endpoints:
    try:
        url = API_URL + endpoint
        payload = {}
        
        print(f"\n🔍 PUT {endpoint}")
        
        response = requests.put(url, json=payload, headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"   ✓ SUCESSO!")
            data = response.json()
            text = json.dumps(data, indent=2)[:600]
            print(f"   {text}")
            
    except Exception as e:
        pass
