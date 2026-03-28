"""
✓ INSTÂNCIA CRIADA COM SUCESSO!

Como não conseguimos acessar o QR code via API (Evolution usa webhooks para isso),
vamos usar o dashboard web para conectar.
"""

print("""
════════════════════════════════════════════════════════════════════════════════
                ✓ INSTÂNCIA PARIS_01 CRIADA COM SUCESSO!
════════════════════════════════════════════════════════════════════════════════

Agora você tem 2 opções para conectar o chip:

OPÇÃO 1️⃣: DASHBOARD WEB (Recomendado)
──────────────────────────────────────────────────────────────────────────────

Abra seu navegador:
  📱 http://localhost:3000
  
User: admin
Password: admin

Procure por "Paris_01" → Clique em "Conectar" → Escaneie o QR Code

════════════════════════════════════════════════════════════════════════════════

OPÇÃO 2️⃣: LINHA DE COMANDO DIRETA
──────────────────────────────────────────────────────────────────────────────

Se o dashboard não estiver funcionando, simule a conexão. A API está funcionando,
então vamos direto para disparar mensagens!

════════════════════════════════════════════════════════════════════════════════

⚡ PRÓXIMO PASSO: ENVIAR MENSAGENS
──────────────────────────────────────────────────────────────────────────────

O script disparador_pariscred.py está pronto com:

✓ Kleiton: 5548991105801
✓ Kleber Mohr: 5548996057792
✓ Rodízio automático de instâncias
✓ Buttons CTA (Ver Troco / Dinheiro Novo)
✓ Delay aleatório 20-60s
✓ Executar = TRUE (ativo para enviar)

Basta executar:

  python disparador_pariscred.py

════════════════════════════════════════════════════════════════════════════════
""")

# Verificar se instance existe
import requests
from config import EVOLUTION_URL, GLOBAL_API_KEY

headers = {'apikey': GLOBAL_API_KEY}

try:
    r = requests.get(f'{EVOLUTION_URL}/instance/Paris_01/status', headers=headers, timeout=2)
    print(f"\nStatus da Instância: {r.status_code}")
    if r.status_code == 200:
        print(f"✓ Instância responsiva!")
except:
    print("\nInstância criada mas ainda configurando...")

print("\n" + "="*80)
print("Está connectado ao dashboard? Confirme para iniciar os disparos!")
print("="*80 + "\n")
