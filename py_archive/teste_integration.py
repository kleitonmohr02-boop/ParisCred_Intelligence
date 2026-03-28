#!/usr/bin/env python3
"""Descobre o tipo correto de integration"""

import requests
import json

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'

integrations = [
    'WHATSAPP-BAILEYS',
    'WHATSAPP',
    'BAILEYS',
    'DEFAULT',
    'NATIVE',
    '',
]

def test_integrations():
    """Testa vários tipos de integration"""
    
    print("=" * 70)
    print("TESTANDO TIPOS DE INTEGRATION")
    print("=" * 70)
    
    for integration in integrations:
        payload = {
            'instanceName': 'TestIntegration',
            'qrcode': True,
        }
        
        if integration:
            payload['integration'] = integration
        
        headers = {
            'apikey': API_KEY,
            'Content-Type': 'application/json'
        }
        
        try:
            url = API_URL + '/instance/create'
            print(f"\n🔍 Testando integration='{integration}'")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            
            data = response.json()
            
            if response.status_code in [200, 201]:
                print(f"   ✓ SUCESSO!")
                print(f"   Response: {json.dumps(data, indent=2)[:400]}")
            else:
                print(f"   Response: {json.dumps(data, indent=2)[:200]}")
                
        except Exception as e:
            print(f"   ✗ Erro: {str(e)[:80]}")

if __name__ == '__main__':
    test_integrations()
