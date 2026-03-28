#!/usr/bin/env python3
"""Verificar se o QR code foi gerado para TestFinal"""

import requests
import json
import time

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'
headers = {'apikey': API_KEY}

print('⏳ Aguardando QR Code ser gerado (5 segundos)...')
time.sleep(5)

print('\n📋 Buscando instâncias criadas...')

response = requests.get(
    f'{API_URL}/instance/fetchInstances',
    headers=headers,
    timeout=5
)

print(f'Status: {response.status_code}')

data = response.json()

print(f'\nTotal de instâncias: {len(data)}')

# Procura pela instância TestFinal
for inst in data:
    print(f'\n  - {inst["name"]}')
    if inst['name'] == 'TestFinal':
        print(f'\n✓ Encontrada: {inst["name"]}')
        
        # Verifica QR code
        print(f'Connection Status: {inst.get("connectionStatus")}')
        
        # Procura por campos de QR code
        for key in inst.keys():
            if 'qr' in key.lower() or 'code' in key.lower():
                print(f'  {key}: {type(inst[key]).__name__}')
        
        break
