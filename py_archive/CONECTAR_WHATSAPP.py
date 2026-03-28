#!/usr/bin/env python3
"""
🚀 GUIA: CONECTAR 3 INSTÂNCIAS WHATSAPP
Instruções passo-a-passo com comandos prontos

RESUMO:
1. Você vai criar 3 instâncias
2. Para cada uma, vai gerar um QR Code
3. Vai escanear com seu telefone
4. Depois testa disparo de mensagens
"""

import requests
import json
from datetime import datetime

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'

def criar_instancia(nome):
    """Cria uma Nova instância WhatsApp"""
    print(f"\n{'='*70}")
    print(f"📱 CRIANDO INSTÂNCIA: {nome}")
    print('='*70)
    
    headers = {
        'apikey': API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'instanceName': nome,
        'qrcode': True  # Retorna QR Code na resposta
    }
    
    # Tenta criar
    endpoints = [
        f'/instance/create',
        f'/instance',
        f'/create',
    ]
    
    for endpoint in endpoints:
        try:
            url = API_URL + endpoint
            print(f"\n Tentando: POST {endpoint}")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            print(f" Status: {response.status_code}")
            
            if response.status_code in [200, 201, 404]:  # 404 pode ser endpoint errado
                data = response.json()
                print(f"\n Resposta:")
                print(json.dumps(data, indent=2)[:800])
                
                if response.status_code in [200, 201]:
                    print(f"\n✓ SUCESSO!")
                    return data
        except Exception as e:
            print(f" ✗ Erro: {str(e)[:100]}")
    
    print(f"\n❌ Não consegui criar via API")
    return None

def obter_qrcode(nome_instancia):
    """Obtém QR Code de uma instância"""
    print(f"\n{'='*70}")
    print(f"📲 OBTENDO QR CODE: {nome_instancia}")
    print('='*70)
    
    headers = {'apikey': API_KEY}
    
    endpoints = [
        f'/{nome_instancia}/qrcode',
        f'/instance/{nome_instancia}/qrcode',
        f'/qrcode/{nome_instancia}',
    ]
    
    for endpoint in endpoints:
        try:
            url = API_URL + endpoint
            print(f"\n Tentando: GET {endpoint}")
            
            response = requests.get(url, headers=headers, timeout=5)
            print(f" Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ QR CODE OBTIDO!")
                print(f"\nConteúdo: {json.dumps(data, indent=2)[:500]}")
                return data
        except Exception as e:
            print(f" ✗ Erro: {str(e)[:80]}")
    
    return None

def status_instancia(nome_instancia):
    """Verifica status de uma instância"""
    print(f"\n{'='*70}")
    print(f"🔍 STATUS: {nome_instancia}")
    print('='*70)
    
    headers = {'apikey': API_KEY}
    
    endpoints = [
        f'/{nome_instancia}',
        f'/instance/{nome_instancia}',
        f'/instance/{nome_instancia}/status',
        f'/status/{nome_instancia}',
    ]
    
    for endpoint in endpoints:
        try:
            url = API_URL + endpoint
            print(f"\n Tentando: GET {endpoint}")
            
            response = requests.get(url, headers=headers, timeout=5)
            print(f" Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n Resposta:")
                print(json.dumps(data, indent=2)[:800])
                
                # Verifica se está conectada
                if isinstance(data, dict):
                    conectada = data.get('instance', {}).get('qrcode', {}).get('connected', False)
                    if conectada:
                        print(f"\n✓ CONECTADA AO WHATSAPP!")
                    else:
                        print(f"\n⏳ Aguardando escanear QR Code...")
                
                return data
        except Exception as e:
            print(f" ✗ Erro: {str(e)[:80]}")
    
    return None

# ============================================================
# EXECUÇÃO MANUAL
# ============================================================

if __name__ == '__main__':
    print("""
    
    ╔══════════════════════════════════════════════════════════════╗
    ║  🚀 GUIA PARA CONECTAR WHATSAPP À EVOLUTION API             ║
    ║                                                              ║
    ║  O que você precisa fazer:                                  ║
    ║  1. Executar este script                                    ║
    ║  2. Seguir as instruções na tela                            ║
    ║  3. Escanear QR Codes com seu telefone                      ║
    ║  4. Confirmação de conexão                                  ║
    ║  5. Testar disparos de mensagens                            ║
    ║                                                              ║
    ║  Instâncias a criar:                                        ║
    ║  • Paris_01                                                 ║
    ║  • Chip01                                                   ║
    ║  • Chip02                                                   ║
    ╚══════════════════════════════════════════════════════════════╝
    
    """)
    
    instancias = ['Paris_01', 'Chip01', 'Chip02']
    
    print("\n📋 PASSO 1: CRIAR INSTÂNCIAS\n")
    
    for nome in instancias:
        resultado = criar_instancia(nome)
        
        if resultado:
            print(f"\n✓ {nome} criada com sucesso")
        else:
            print(f"\n⚠️  Verifique a criação de {nome} manualmente")
        
        input(f"\n[Pressione ENTER para próxima...]")
    
    print(f"\n\n{'='*70}")
    print("📲 PASSO 2: ESCANEAR QR CODES")
    print('='*70)
    print("""
    Para cada instância:
    1. Vou gerar um QR Code
    2. Abra seu WhatsApp no telefone
    3. Vá em: Configurações → Aparelhos Conectados → Conectar Aparelho
    4. Escaneie o QR Code
    5. Aguarde a marcação de "Conectado"
    """)
    
    for nome in instancias:
        print(f"\n⏳ Gerando QR Code para {nome}...")
        qr = obter_qrcode(nome)
        
        if qr:
            print(f"""
    ╔════════════════════════════════════════╗
    ║ ESCANEIE ESTE QR CODE COM SEU WHATSAPP║
    ║                                        ║
    ║ [Imagem do QR Code aqui]              ║
    ║                                        ║
    ║ Instância: {nome}
    ║ Gerado em: {datetime.now().strftime('%H:%M:%S')}
    ╚════════════════════════════════════════╝
            """)
        
        input(f"\n[Pressione ENTER após escanear {nome}...]")
    
    print(f"\n\n{'='*70}")
    print("✓ PASSO 3: VALIDAR CONEXÕES")
    print('='*70)
    
    for nome in instancias:
        status = status_instancia(nome)
        
        if status:
            print(f"\n✓ {nome} - Status obtido")
        else:
            print(f"\n⚠️  {nome} - Não consegui validar")
    
    print(f"""
    
    {'='*70}
    ✅ PRÓXIMA ETAPA:
    {'='*70}
    
    Se todas as 3 instâncias foram conectadas com sucesso:
    
    1. Volte para o DASHBOARD
    2. Vá em: CAMPANHAS → Nova Campanha
    3. Crie uma campanha de teste
    4. Adicione 2 beneficiários
    5. Clique em: ⚡ DISPARAR
    
    Se alguma falhou:
    - Verifique conexão de WiFi
    - Teste novamente escanear o QR Code
    - Verifique se WhatsApp está atualizado
    
    Dúvidas?
    - Verifique: debug_endpoints.py
    - Ou execute: python explorador_api.py
    
    """)
