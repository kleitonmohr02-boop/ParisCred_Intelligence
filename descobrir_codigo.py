#!/usr/bin/env python3
"""
Descobrir como conectar via código na Evolution API
"""

import requests
import json

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'
headers = {'apikey': API_KEY}

print('📱 Listando instâncias e seus campos...\n')

# Listar instâncias
response = requests.get(API_URL + '/instance/fetchInstances', headers=headers, timeout=5)
data = response.json()

print(f'Total de instâncias: {len(data)}\n')

for inst in data:
    print(f'Nome: {inst["name"]}')
    print(f'Status: {inst.get("connectionStatus")}')
    print(f'Todas as chaves: {list(inst.keys())}')
    
    # Mostrar todos os campos
    for key, value in inst.items():
        if value and key not in ['Setting', '_count']:  # Skip nested objects
            print(f'  {key}: {value}')
    print()

print('\n' + '='*70)
print('Testando POST para criar instância com integração e pega o "code"\n')

# Criar nova instância para observar a resposta
payload = {
    'instanceName': 'TestCode_001',
    'integration': 'WHATSAPP-BAILEYS'
}

response = requests.post(
    f'{API_URL}/instance/create',
    json=payload,
    headers=headers,
    timeout=30
)

print(f'Status: {response.status_code}\n')
resp_data = response.json()
print(json.dumps(resp_data, indent=2))

# Verificar se há campo de code
if 'code' in resp_data:
    print(f'\n✓ ENCONTRADO: code = {resp_data["code"]}')
elif 'instance' in resp_data and 'code' in resp_data['instance']:
    print(f'\n✓ ENCONTRADO: instance.code = {resp_data["instance"]["code"]}')
else:
    print('\n✗ Nenhum campo "code" encontrado')
