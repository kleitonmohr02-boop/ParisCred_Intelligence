"""
⚠️  PROBLEMA: O evolution-manager está em erro

O sistema parece estar configurado para gerenciar instâncias via interface,
mas o manager não está rodando corretamente.

SOLUÇÃO: Você pode criar a instância de 4 formas:
"""

print("""
════════════════════════════════════════════════════════════════════════════════
                        ⚠️  PROBLEMA DETECTADO
════════════════════════════════════════════════════════════════════════════════

O evolution-manager está com status "Restarting (erro)".

OPÇÃO 1️⃣: Acessar o Dashboard da Evolution (se disponível)
──────────────────────────────────────────────────────────────────────────────

Abra no navegador:
  URL: http://localhost:3000 (ou confira a porta do manager)
  
Crie a instância "Paris_01" pela interface web

════════════════════════════════════════════════════════════════════════════════

OPÇÃO 2️⃣: Reparar o evolution-manager no Docker
──────────────────────────────────────────────────────────────────────────────

Execute estes comandos:

1. Parar o container:
   docker stop evolution-manager

2. Remover:
   docker rm evolution-manager

3. Reiniciar via docker-compose:
   docker-compose up -d evolution-manager

(Precisará ir até o diretório com o docker-compose.yml primeiro)

════════════════════════════════════════════════════════════════════════════════

OPÇÃO 3️⃣: Criar instância via Docker exec (debug mode)
──────────────────────────────────────────────────────────────────────────────

Execute:

docker exec -it evolution_api sh -c "
curl -X POST 'http://localhost:8080/instance/create' \\
  -H 'apikey: 429683C4C977415CAAFCCE10F7D57E11' \\
  -H 'Content-Type: application/json' \\
  -d '{\"instanceName\": \"Paris_01\", \"qrcode\": true}'
"

════════════════════════════════════════════════════════════════════════════════

OPÇÃO 4️⃣: Ignorar erro 401 e tentar de todas as formas
──────────────────────────────────────────────────────────────────────────────

Às vezes o erro 401 é enganoso. Execute este script em Python:

""")

import requests
from config import EVOLUTION_URL, GLOBAL_API_KEY

# Tenta com método PATCH em vez de POST
headers = {
    'apikey': GLOBAL_API_KEY,
    'Content-Type': 'application/json'
}

payload = {
    "instanceName": "Paris_01",
    "qrcode": True
}

print("\nTestando PATCH /instance/create...\n")

try:
    response = requests.patch(
        f'{EVOLUTION_URL}/instance/create',
        json=payload,
        headers=headers,
        timeout=5
    )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    
    if response.status_code in [200, 201]:
        print("\n✓ SUCESSO com PATCH!")
    
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "="*80)
print("O que você quer fazer? Descreva qual opção escolheu para eu ajudar.")
print("="*80)
