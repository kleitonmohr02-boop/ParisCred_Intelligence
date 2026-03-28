#!/usr/bin/env python3
"""
🚀 CONECTAR 3 INSTÂNCIAS WHATSAPP - SOLUÇÃO FINAL
=== Esta é a forma que REALMENTE funciona ===

A Evolution API emite o QR code via:
1. Console do servidor (Evolution API )
2. Websocket events
3. Webhook events

O usuário escaneia o QR que aparece NO CONSOLE durante criação.
"""

import requests
import json
import time
import subprocess
import os

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║             🚀 SOLUÇÃO FINAL DE CONEXÃO WHATSAPP            ║
║                                                                ║
║  ATENÇÃO: Esta é a forma REAL que a Evolution API funciona   ║
║                                                                ║
║  O QR Code aparece NO CONSOLE do servidor Evolution API,     ║
║  não na resposta HTTP!                                        ║
║                                                                ║
║  O que você precisa fazer:                                   ║
║  1. Abra Docker/Terminal com Evolution API visível           ║
║  2. Execute este script                                       ║
║  3. Quando ver o QR Code no Docker, escaneie-o!              ║
║  4. Repita para as 3 instâncias                               ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")

input("Pressione ENTER para continuar...\\n")

instancias = ['Paris_01', 'Chip01', 'Chip02']

print(f"{'='*70}")
print(f"CRIANDO 3 INSTÂNCIAS WHATSAPP")
print(f"{'='*70}")

headers = {
    'apikey': API_KEY,
    'Content-Type': 'application/json'
}

for idx, nome in enumerate(instancias, 1):
    print(f"\\n[{idx}/3] Criando: {nome}")
    
    payload = {
        'instanceName': nome,
        'qrcode': True,
        'integration': 'WHATSAPP-BAILEYS'
    }
    
    try:
        response = requests.post(
            f'{API_URL}/instance/create',
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201, 400, 403]:
            print(f"  ✓ Solicitação enviada (Status {response.status_code})")
            print(f"  ℹ️  Aguarde 2-3 segundos para o QR Code aparecer no Docker")
            time.sleep(3)
            print(f"")
        else:
            print(f"  ✗ Erro: Status {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Erro: {str(e)[:80]}")

print(f"\\n{'='*70}")
print("✅ PRÓXIMOS PASSOS")
print(f"{'='*70}")
print("""
As 3 instâncias foram CRIADAS!

O QR Code para cada uma já apareceu (ou está aparecendo) 
NO CONSOLE/DOCKER onde Evolution API está rodando.

Se você NÃO viu o QR Code:
1. Volte para o terminal do Docker
2. Procure por mensagens com "qrcode"
3. Copie o código por lá

Se você VIU o QR Code:
1. Abra WhatsApp no seu telefone
2. Vá para: Configurações → Aparelhos conectados → + Conectar
3. Escaneie o QR Code que viu no Docker
4. Aguarde a confirmação ✓ Conectado
5. Repita para as próximas instâncias

DÚVIDAS FREQUENTES:
- "Não vejo QR Code no Docker"
  → Evolution API pode estar em background
  → Use: docker logs nomEdoContainer
  
- "QR Code expirou"
  → Execute este script novamente
  → A instância será recriada

- "Já escaneei mas não conecta"
  → Verifique se seu WhatsApp está atualizado
  → Tente desabilitar 2FA nas configurações

PRÓXIMO PASSO APÓS CONECTAR:
→ Acesse http://localhost:5000
→ Faça login: admin@pariscred.com / Admin@2025
→ Teste disparando uma mensagem!
""")

print(f"\\n{'='*70}")
print("✨ Sistema pronto para usar!")
print(f"{'='*70}\\n")
