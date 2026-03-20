import requests
import json
from config import EVOLUTION_URL, GLOBAL_API_KEY

def try_endpoints():
    """Tenta vários endpoints comuns para descobrir a estrutura da API."""
    
    endpoints = [
        '/health',
        '/status',
        '/api/health',
        '/api/status',
        '/version',
        '/api/version',
        '/',
        '/api'
    ]
    
    headers = {
        'apikey': GLOBAL_API_KEY
    }
    
    print(f"Testando endpoints em {EVOLUTION_URL}...\n")
    
    for endpoint in endpoints:
        try:
            url = f'{EVOLUTION_URL}{endpoint}'
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"✓ {endpoint} - Status 200")
                try:
                    data = response.json()
                    print(f"  Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"  Resposta: {response.text[:100]}...")
                print()
            elif response.status_code == 404:
                print(f"✗ {endpoint} - Status 404 (não encontrado)")
            else:
                print(f"◐ {endpoint} - Status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"✗ {endpoint} - Timeout")
        except requests.exceptions.ConnectionError:
            print(f"✗ {endpoint} - Erro de conexão")
        except Exception as e:
            print(f"✗ {endpoint} - Erro: {str(e)}")

def check_api_status():
    """Verifica se a API Evolution está online e exibe a versão."""
    
    try:
        # Primeiro tenta conectar
        response = requests.get(f'{EVOLUTION_URL}', timeout=5)
        print("✓ API está ONLINE!")
        print(f"Status: {response.status_code}\n")
        
        # Extrai informações principais
        try:
            data = response.json()
            
            if 'version' in data:
                print(f"📦 Versão da API: {data['version']}")
            if 'clientName' in data:
                print(f"👤 Nome do Cliente: {data['clientName']}")
            if 'message' in data:
                print(f"📝 Mensagem: {data['message']}")
            
            print("\n" + "=" * 50)
            print("Informações Completas:")
            print("=" * 50)
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        except json.JSONDecodeError:
            print("⚠️ Resposta não é JSON válido")
            print(response.text)
        
        # Tenta descobrir outros endpoints disponíveis
        print("\n" + "=" * 50)
        print("Testando Endpoints Adicionais:")
        print("=" * 50 + "\n")
        try_endpoints()
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Erro: Não consegui conectar à API em {EVOLUTION_URL}")
        print("Verifique se a API Evolution está rodando.")
        
    except requests.exceptions.Timeout:
        print("✗ Erro: Timeout na requisição à API")
        
    except Exception as e:
        print(f"✗ Erro inesperado: {str(e)}")

if __name__ == '__main__':
    print("=" * 50)
    print("VERIFICADOR DE API EVOLUTION")
    print("=" * 50)
    print()
    check_api_status()
