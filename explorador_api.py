import requests
import json
from config import EVOLUTION_URL, GLOBAL_API_KEY

def explorar_api():
    """Explora a API para descobrir endpoints disponíveis."""
    
    headers = {
        'apikey': GLOBAL_API_KEY
    }
    
    # Tenta listar instâncias
    endpoints_discovery = [
        '/instance',
        '/instances',
        '/api/instances',
        '/list',
        '/all',
    ]
    
    print("=" * 70)
    print("🔍 EXPLORANDO ESTRUTURA DA API EVOLUTION v2.2.3")
    print("=" * 70 + "\n")
    
    for endpoint in endpoints_discovery:
        try:
            url = f"{EVOLUTION_URL}{endpoint}"
            response = requests.get(url, headers=headers, timeout=5)
            
            print(f"📍 GET {endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    print(f"   ✓ ENCONTRADO!")
                    print(f"   Resposta: {json.dumps(data, indent=4, ensure_ascii=False)[:500]}")
                    print()
                    return data
                except:
                    print(f"   Dados: {response.text[:200]}\n")
            else:
                print(f"   ✗ Status {response.status_code}\n")
                
        except Exception as e:
            print(f"   ✗ Erro: {str(e)}\n")
    
    print("=" * 70)
    print("⚠️  Nenhum endpoint de descoberta funcionou.")
    print("=" * 70 + "\n")
    
    # Tenta criar instância
    print("🔧 TENTANDO CRIAR/INICIALIZAR INSTÂNCIA Paris_01\n")
    
    create_endpoints = [
        ('/instance', 'POST'),
        ('/instance/create', 'POST'),
        ('/create', 'POST'),
    ]
    
    payload = {
        "instanceName": "Paris_01",
        "qrcode": True
    }
    
    for endpoint, method in create_endpoints:
        try:
            url = f"{EVOLUTION_URL}{endpoint}"
            
            if method == 'POST':
                response = requests.post(url, json=payload, headers=headers, timeout=5)
            else:
                response = requests.get(url, headers=headers, timeout=5)
            
            print(f"📍 {method} {endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201, 400]:
                try:
                    data = response.json()
                    print(f"   Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:400]}")
                    print()
                except:
                    print(f"   Dados: {response.text[:200]}\n")
                    
        except Exception as e:
            print(f"   ✗ Erro: {str(e)}\n")

if __name__ == '__main__':
    explorar_api()
