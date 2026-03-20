#!/usr/bin/env python3
"""
Teste de endpoints Evolution API v2.2.3

Baseado na documentação da API, vamos descobrir os endpoints corretos
"""

import requests
import json
from config import EVOLUTION_URL, GLOBAL_API_KEY

headers = {'apikey': GLOBAL_API_KEY, 'Content-Type': 'application/json'}

# Teste 1: Criar instância via POST (pode estar falhando silenciosamente)
print("="*60)
print("TESTE 1: Criar instância novamente")
print("="*60 + "\n")

payload_create = {
    "instanceName": "TestInstance123",
    "qrcode": True,
    "integration": "WHATSAPP-BAILEYS"
}

r = requests.post(f'{EVOLUTION_URL}/instance/create', json=payload_create, headers=headers, timeout=5)
print(f"POST /instance/create: {r.status_code}")
print(f"Resposta: {r.text}\n")

# Teste 2: Se criar retornar sucesso, tentar enviar mensagem
if r.status_code in [200, 201]:
    inst_name = "TestInstance123"
    
    print("="*60)
    print(f"TESTE 2: Enviar mensagem para {inst_name}")
    print("="*60 + "\n")
    
    # Buscar endpoint correto de envio
    send_endpoints = [
        f'/{inst_name}/message/send',
        f'/instance/{inst_name}/message/send',
        f'/{inst_name}/send',
        f'/instance/{inst_name}/send',
        f'/message/send?instance={inst_name}',
    ]
    
    payload_msg = {
        "number": "5548991105801",
        "text": "Teste de Conexão"
    }
    
    for ep in send_endpoints:
        try:
            r = requests.post(f'{EVOLUTION_URL}{ep}', json=payload_msg, headers=headers, timeout=2)
            print(f"POST {ep}: {r.status_code}")
            if r.status_code in [200, 201]:
                print(f"  ✓ SUCESSO!")
                break
        except Exception as e:
            print(f"POST {ep}: Erro - {str(e)[:30]}")

# Teste 3: Procurar por rotas disponíveis
print("\n" + "="*60)
print("TESTE 3: Procurar endpoints disponíveis")
print("="*60 + "\n")

test_routes = [
    'GET', '/',
    'GET', '/users',
    'GET', '/me',
    'GET', '/stats',
    'GET', '/queue',
]

for i in range(0, len(test_routes), 2):
    method, route = test_routes[i], test_routes[i+1]
    try:
        if method == 'GET':
            r = requests.get(f'{EVOLUTION_URL}{route}', headers=headers, timeout=1)
            if r.status_code in [200, 201]:
                print(f"GET {route}: ✓ (200)")
    except:
        pass
