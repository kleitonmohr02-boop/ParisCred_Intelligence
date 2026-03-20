#!/usr/bin/env python3
"""Descobre os endpoints corretos da Evolution API"""

import requests
import json

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'

def test_create_endpoints():
    """Testa vários endpoints para criar instância"""
    
    endpoints = [
        '/instance/create',
        '/webhook/create',
        '/instances',
        '/instance',
        '/create',
        '/api/instance/create',
        '/api/instances/create',
    ]
    
    payload = {
        'instanceName': 'Test_Discovery',
        'qrcode': True
    }
    
    headers = {
        'apikey': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=" * 70)
    print("TESTANDO ENDPOINTS DE CRIAÇÃO")
    print("=" * 70)
    
    for endpoint in endpoints:
        try:
            url = API_URL + endpoint
            print(f"\n🔍 Testando: POST {endpoint}")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"   ✓ SUCESSO!")
                print(f"   Response: {response.text[:200]}")
                return endpoint
            elif response.status_code == 400:
                print(f"   ⚠️  Bad Request (endpoint pode estar OK)")
                print(f"   Response: {response.text[:200]}")
            elif response.status_code == 403:
                print(f"   🔒 Forbidden (precisa auth diferente?)")
            else:
                print(f"   ❌ Status {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Erro: {str(e)[:80]}")
    
    print("\n" + "=" * 70)
    print("TESTANDO ENDPOINTS DE QR CODE")
    print("=" * 70)
    
    qr_endpoints = [
        '/instance/Paris_01/qrcode',
        '/Paris_01/qrcode',
        '/instance/Paris_01',
        '/Paris_01',
        '/api/instance/Paris_01/qrcode',
        '/api/Paris_01/qrcode',
    ]
    
    for endpoint in qr_endpoints:
        try:
            url = API_URL + endpoint
            print(f"\n🔍 Testando: GET {endpoint}")
            
            response = requests.get(
                url,
                headers={'apikey': API_KEY},
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✓ SUCESSO!")
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:300]}")
                return endpoint
            else:
                print(f"   ❌ Status {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Erro: {str(e)[:80]}")

if __name__ == '__main__':
    test_create_endpoints()
