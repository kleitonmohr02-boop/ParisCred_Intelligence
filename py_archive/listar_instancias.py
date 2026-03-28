#!/usr/bin/env python3
"""Descobre as instâncias existentes"""

import requests
import json

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'

def list_instances():
    """Lista todas as instâncias"""
    
    endpoints = [
        '/instance/list',
        '/instances',
        '/instances/list',
        '/instance',
        '/api/instances',
        '/api/instance/list',
    ]
    
    headers = {
        'apikey': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=" * 70)
    print("PROCURANDO ENDPOINT DE LISTAGEM")
    print("=" * 70)
    
    for endpoint in endpoints:
        try:
            url = API_URL + endpoint
            print(f"\n🔍 Testando: GET {endpoint}")
            
            response = requests.get(
                url,
                headers=headers,
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✓ ENCONTRADO!")
                data = response.json()
                print(f"   Response:\n{json.dumps(data, indent=2)}")
                return
            else:
                print(f"   ❌ Status {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Erro: {str(e)[:80]}")

if __name__ == '__main__':
    list_instances()
