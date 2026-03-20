"""
🚀 GUIA DE CONEXÃO - EVOLUTION API v2.2.3

Este arquivo contém os comandos exatos para criar e conectar uma instância.
Execute os comandos no PowerShell ou CMD.
"""

print("""
════════════════════════════════════════════════════════════════════════════════
                   ⚙️  SETUP INICIAL - CRIAR INSTÂNCIA
════════════════════════════════════════════════════════════════════════════════

A API Evolution requer que você crie uma instância ANTES de gerar o QR Code.

PASSO 1️⃣: CRIAR A INSTÂNCIA "Paris_01"
─────────────────────────────────────────────────────────────────────────────

Execute este comando no PowerShell:

curl -X POST "http://localhost:8080/instance/create" `
  -H "apikey: SUA_API_KEY_AQUI" `
  -H "Content-Type: application/json" `
  -d '{
    "instanceName": "Paris_01",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'

OU use este Python:

import requests
import json

EVOLUTION_URL = 'http://localhost:8080'
GLOBAL_API_KEY = 'SUA_API_KEY_AQUI'

headers = {
    'apikey': GLOBAL_API_KEY,
    'Content-Type': 'application/json'
}

payload = {
    "instanceName": "Paris_01",
    "qrcode": True,
    "integration": "WHATSAPP-BAILEYS"
}

response = requests.post(
    f'{EVOLUTION_URL}/instance/create',
    json=payload,
    headers=headers
)

print(response.status_code)
print(response.json())

─────────────────────────────────────────────────────────────────────────────

PASSO 2️⃣: GERAR QR CODE PARA A INSTÂNCIA
─────────────────────────────────────────────────────────────────────────────

Após criar, gere o QR Code:

curl -X GET "http://localhost:8080/instance/Paris_01/qrcode" `
  -H "apikey: SUA_API_KEY_AQUI"

─────────────────────────────────────────────────────────────────────────────

PASSO 3️⃣: VERIFICAR SE ESTÁ CONECTADO
─────────────────────────────────────────────────────────────────────────────

curl -X GET "http://localhost:8080/instance/Paris_01" `
  -H "apikey: SUA_API_KEY_AQUI"

Procure por "instance_status": "connected"

════════════════════════════════════════════════════════════════════════════════

📌 IMPORTANTE: Substitua 'SUA_API_KEY_AQUI' pela chave real no config.py

════════════════════════════════════════════════════════════════════════════════
""")

# Fornece um script Python pronto para usar
import sys
sys.path.insert(0, '/ParisCred_Intelligence')

try:
    from config import EVOLUTION_URL, GLOBAL_API_KEY
    
    print(f"\n✓ Config carregado:")
    print(f"  URL: {EVOLUTION_URL}")
    print(f"  API Key: {GLOBAL_API_KEY[:20]}...")
    
except Exception as e:
    print(f"\n⚠️  Erro ao carregar config: {e}")
