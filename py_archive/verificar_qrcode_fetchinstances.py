#!/usr/bin/env python3
"""Verifica se fetchInstances retorna QR Code"""

import requests
import json

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'

print("=" * 70)
print("VERIFICANDO SE fetchInstances INCLUI QR CODE")
print("=" * 70)

headers = {'apikey': API_KEY}

response = requests.get(
    f'{API_URL}/instance/fetchInstances',
    headers=headers,
    timeout=5
)

if response.status_code == 200:
    data = response.json()
    
    print(f"\n✓ Response Status: 200")
    print(f"✓ Número de instâncias: {len(data)}")
    
    for inst in data:
        print(f"\n{'='*70}")
        print(f"INSTÂNCIA: {inst.get('name')}")
        print(f"{'='*70}")
        
        # Lista todas as chaves disponíveis
        print("\nCampos disponíveis:")
        for key in inst.keys():
            if isinstance(inst[key], (dict, list)):
                print(f"  - {key}: {type(inst[key]).__name__}")
            else:
                value = str(inst[key])[:100]
                print(f"  - {key}: {value}")
        
        # Procura por 'qr', 'code', 'scan', 'connect'
        print("\nProcurando campos relacionados a QR Code:")
        for key in inst.keys():
            if any(q in key.lower() for q in ['qr', 'code', 'scan', 'connect', 'websocket']):
                print(f"  ✓ ENCONTRADO: {key} = {inst[key]}")
        
        # Verifica Setting
        if inst.get('Setting'):
            print("\nCampos em Setting:")
            for key in inst['Setting'].keys():
                print(f"  - {key}")
