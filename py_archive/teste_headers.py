import requests
import json
from config import EVOLUTION_URL, GLOBAL_API_KEY

def testar_criacao_instancia():
    """Testa várias formas de criar instância."""
    
    headers_opcoes = [
        # Opção 1: apikey no header
        {'apikey': GLOBAL_API_KEY, 'Content-Type': 'application/json'},
        # Opção 2: Authorization
        {'Authorization': f'Bearer {GLOBAL_API_KEY}', 'Content-Type': 'application/json'},
        # Opção 3: X-API-KEY
        {'X-API-KEY': GLOBAL_API_KEY, 'Content-Type': 'application/json'},
        # Opção 4: Token
        {'Authorization': GLOBAL_API_KEY, 'Content-Type': 'application/json'},
    ]
    
    endpoints = [
        '/instance/create',
        '/instances/create',
        '/instance',
        '/create-instance',
    ]
    
    payload = {
        "instanceName": "Paris_01",
        "qrcode": True
    }
    
    for header_idx, headers in enumerate(headers_opcoes, 1):
        header_name = list(headers.keys())[0]
        print(f"\n{'='*60}")
        print(f"Tentativa {header_idx}: Header '{header_name}'")
        print(f"{'='*60}\n")
        
        for endpoint in endpoints:
            try:
                url = f"{EVOLUTION_URL}{endpoint}"
                print(f"  POST {endpoint}...", end=" ")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=5
                )
                
                print(f"Status {response.status_code}")
                
                if response.status_code in [200, 201]:
                    print(f"    ✓ SUCESSO!")
                    print(f"    Resposta: {response.json()}")
                    return True
                else:
                    try:
                        data = response.json()
                        print(f"    Erro: {data.get('message', data)}")
                    except:
                        print(f"    Erro: {response.text[:100]}")
                        
            except Exception as e:
                print(f"Erro de conexão: {str(e)}")
    
    return False

if __name__ == '__main__':
    testar_criacao_instancia()
