import requests
import json

headers = {'apikey': 'CONSIGNADO123', 'Content-Type': 'application/json'}

print("=" * 60)
print("TESTANDO ENDPOINTS")
print("=" * 60 + "\n")

# Testar listar instâncias
print("1. LISTANDO INSTÂNCIAS:\n")

list_eps = ['/instance/fetch', '/instance/all', '/fetched', '/instances']
for ep in list_eps:
    try:
        r = requests.get(f'http://localhost:8080{ep}', headers=headers, timeout=2)
        if r.status_code in [200, 201]:
            print(f"✓ {ep}: {r.status_code}")
            print(f"  {r.text[:300]}\n")
    except Exception as e:
        pass

# Testar envio de mensagem
print("\n2. TESTANDO ENVIO DE MENSAGEM:\n")

payload = {'number': '5548991105801', 'text': 'Teste'}

send_eps = [
    '/instance/Paris_01/send',
    '/Paris_01/send',
    '/instance/Paris_01/message/send',
    '/Paris_01/message/send',
]

for ep in send_eps:
    try:
        r = requests.post(f'http://localhost:8080{ep}', json=payload, headers=headers, timeout=2)
        status = "✓" if r.status_code in [200, 201] else "✗"
        print(f"{status} {ep}: {r.status_code}")
        if r.status_code in [200, 201]:
            print(f"  SUCCESS: {r.json()}\n")
    except Exception as e:
        print(f"✗ {ep}: {str(e)[:40]}\n")
