import requests
import json
from config import EVOLUTION_URL, GLOBAL_API_KEY

def gerar_qr_code(nome_instancia: str):
    """
    Gera QR Code para conexão de uma instância WhatsApp.
    
    Args:
        nome_instancia: Nome da instância (ex: 'Paris_01')
    """
    
    headers = {
        'apikey': GLOBAL_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=" * 60)
    print(f"🔗 GERANDO QR CODE - {nome_instancia}")
    print("=" * 60 + "\n")
    
    # Tenta vários endpoints comuns
    endpoints = [
        f"{EVOLUTION_URL}/{nome_instancia}/qrcode",
        f"{EVOLUTION_URL}/{nome_instancia}/qr-code",
        f"{EVOLUTION_URL}/{nome_instancia}/connect",
        f"{EVOLUTION_URL}/{nome_instancia}/qr",
    ]
    
    for url in endpoints:
        try:
            print(f"Testando: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"✓ Sucesso!\n")
                
                data = response.json()
                
                if 'qrcode' in data:
                    print("📱 ESCANEIE ESTE QR CODE COM SEU CELULAR:")
                    print("-" * 60)
                    print(data['qrcode'])
                    print("-" * 60)
                    print(f"\n✓ Instância: {nome_instancia}")
                    print("Aguardando conexão...")
                    
                else:
                    print("Resposta completa:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                
                return True
                
            elif response.status_code == 404:
                print(f"✗ Endpoint não encontrado\n")
            else:
                print(f"✗ Status {response.status_code}\n")
                
        except Exception as e:
            print(f"✗ Erro: {str(e)}\n")
    
    print("=" * 60)
    print("⚠️  Nenhum endpoint funcionou.")
    print("Tente verificar o nome da instância ou use curl manualmente:")
    print(f"\ncurl -X GET '{EVOLUTION_URL}/Paris_01/qrcode' \\")
    print(f"  -H 'apikey: {GLOBAL_API_KEY}'")
    print("=" * 60)

def verificar_conexao(nome_instancia: str):
    """Verifica o status de conexão de uma instância."""
    
    headers = {
        'apikey': GLOBAL_API_KEY
    }
    
    try:
        # Tenta vários endpoints de status
        endpoints = [
            f"{EVOLUTION_URL}/{nome_instancia}/status",
            f"{EVOLUTION_URL}/{nome_instancia}",
            f"{EVOLUTION_URL}/instance/{nome_instancia}/status",
        ]
        
        for url in endpoints:
            try:
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    
                    if 'status' in data or 'instance' in data:
                        print("\n" + "=" * 60)
                        print(f"📊 STATUS DA INSTÂNCIA: {nome_instancia}")
                        print("=" * 60)
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                        print("=" * 60 + "\n")
                        return True
                        
            except:
                continue
                
    except Exception as e:
        print(f"Erro ao verificar: {str(e)}")
    
    return False

if __name__ == '__main__':
    instancia = 'Paris_01'
    
    print("\n🚀 GERADOR DE QR CODE - EVOLUTION API\n")
    
    # Gera QR Code
    gerar_qr_code(instancia)
    
    print("\n💡 Dica: Escaneie o QR Code com WhatsApp Web para conectar a instância.")
    print("Depois, execute: python gerador_qrcode.py para verificar o status.")
