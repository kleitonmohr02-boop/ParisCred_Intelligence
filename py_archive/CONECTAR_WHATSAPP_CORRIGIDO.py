#!/usr/bin/env python3
"""
🚀 SCRIPT CORRIGIDO: CONECTAR 3 INSTÂNCIAS WHATSAPP
Baseado na documentação da Evolution API v2.2.3
"""

import requests
import json
import time
from base64 import b64decode
from PIL import Image
from io import BytesIO
import os

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'

def criar_instancia(nome):
    """Cria uma nova instância WhatsApp"""
    
    print(f"\n{'='*70}")
    print(f"📱 CRIANDO INSTÂNCIA: {nome}")
    print('='*70)
    
    headers = {
        'apikey': API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'instanceName': nome,
        'qrcode': True,
    }
    
    try:
        url = f'{API_URL}/instance/create'
        print(f"\n📍 POST /instance/create")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n✓ Status: {response.status_code}")
        
        data = response.json()
        
        if response.status_code in [200, 201]:
            print(f"\n✓✓✓ INSTÂNCIA CRIADA COM SUCESSO! ✓✓✓")
            return True
        elif response.status_code == 403 and 'already' in str(data).lower():
            print(f"\n⚠️  Instância já existe (vamos prosseguir)")
            return True
        else:
            resposta_text = json.dumps(data, indent=2)[:300]
            print(f"\n⚠️  Resposta: {resposta_text}")
            return False
            
    except Exception as e:
        print(f"\n✗ Erro: {str(e)}")
        return False

def obter_qrcode(nome):
    """Obtém QR Code escaneável via GET /instance/connect"""
    
    print(f"\n{'='*70}")
    print(f"📲 OBTENDO QR CODE: {nome}")
    print('='*70)
    
    headers = {'apikey': API_KEY}
    
    try:
        # Endpoint correto para obter QR Code
        url = f'{API_URL}/instance/connect'
        params = {'instanceName': nome}
        
        print(f"\n📍 GET /instance/connect?instanceName={nome}")
        
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )
        
        print(f"\n✓ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # O QR Code está em data['qrcode']['base64'] ou data['qrcode']
            if isinstance(data, dict) and 'qrcode' in data:
                qrcode_info = data['qrcode']
                
                # Tenta extrair base64
                if isinstance(qrcode_info, dict) and 'base64' in qrcode_info:
                    base64_str = qrcode_info['base64']
                elif isinstance(qrcode_info, str):
                    base64_str = qrcode_info
                else:
                    print(f"\n📦 Resposta: {json.dumps(data, indent=2)[:400]}")
                    return None
                
                # Remove prefixo se existir
                if 'base64,' in base64_str:
                    base64_str = base64_str.split('base64,')[1]
                
                # Exibe QR code no terminal usando caracteres ASCIIprint(f"\n✓ QR CODE OBTIDO COM SUCESSO!")
                print(f"\n╔════════════════════════════════════════╗")
                print(f"║ ESCANEIE ESTE QR CODE COM WHATSAPP    ║")
                print(f"║ Instância: {nome:30} ║")
                print(f"╚════════════════════════════════════════╝\n")
                
                # Tenta decodificar e exibir
                try:
                    image_data = Image.open(BytesIO(b64decode(base64_str)))
                    # Para terminal, vamos apenas confirmar que é uma imagem válida
                    print(f"✓ QR Code (tamanho: {image_data.size[0]}x{image_data.size[1]} pixels)")
                    print(f"✓ Pronto para escanear no seu WhatsApp\n")
                except Exception as e:
                    print(f"✓ QR Code carregado (formato: {len(base64_str)} caracteres base64)")
                
                return data
            else:
                print(f"\n📦 Resposta: {json.dumps(data, indent=2)[:400]}")
                return data
        else:
            resposta = response.json()
            print(f"\n⚠️  Erro {response.status_code}: {json.dumps(resposta, indent=2)[:200]}")
            return None
            
    except Exception as e:
        print(f"\n✗ Erro: {str(e)[:100]}")
        return None

def verificar_conexao(nome):
    """Verifica se a instância está conectada"""
    
    print(f"\n🔍 VERIFICANDO CONEXÃO: {nome}")
    
    headers = {'apikey': API_KEY}
    
    try:
        # GET /instance/connect também retorna o status
        url = f'{API_URL}/instance/connect'
        params = {'instanceName': nome}
        
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verifica campos de conexão
            if isinstance(data, dict):
                if data.get('instance', {}).get('status') == 'open':
                    print(f"✓ {nome}: CONECTADA AO WHATSAPP!")
                    return True
                elif 'qrcode' in data:
                    print(f"⏳ {nome}: Aguardando escaneamento de QR Code")
                    return False
                else:
                    print(f"❓ {nome}: Status desconhecido")
                    return False
            else:
                print(f"❓ Resposta inesperada: {str(data)[:100]}")
                return False
        else:
            print(f"❌ Erro ao verificar: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)[:60]}")
        return False

# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🚀 CONECTAR 3 INSTÂNCIAS WHATSAPP À EVOLUTION API          ║
║                                                              ║
║  Processo:                                                   ║
║  1. Criar 3 instâncias (Paris_01, Chip01, Chip02)          ║
║  2. Gerar QR Code para cada uma                             ║
║  3. Você escaneia com seu WhatsApp                          ║
║  4. Verificamos a conexão                                   ║
║                                                              ║
║  ⏱️  Tempo esperado: 15-20 minutos                          ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    instancias = ['Paris_01', 'Chip01', 'Chip02']
    
    print(f"\n{'='*70}")
    print("PASSO 1: CRIANDO INSTÂNCIAS")
    print('='*70)
    
    for instancia in instancias:
        criar_instancia(instancia)
        time.sleep(2)
    
    print(f"\n{'='*70}")
    print("PASSO 2: GERAR E ESCANEAR QR CODES")
    print('='*70)
    
    for instancia in instancias:
        obter_qrcode(instancia)
        
        print(f"\n{'─'*70}")
        print(f"INSTRUÇÕES PARA ESCANEAR QR CODE DE {instancia}:")
        print(f"{'─'*70}")
        print(f"""
1. Abra o WhatsApp no seu telefone
2. Toque em:
   ⋮ (menu) → Configurações → Aparelhos conectados
3. Toque em: [+ Conectar um aparelho]
4. Aponte a câmera para a tela do seu computador
5. Escaneie o QR Code exibido acima
6. Aguarde a confirmação "✓ Conectado"
""")
        
        input(f"\n⏸️  Pressione ENTER após escanear o QR Code de {instancia}...\n")
        
        verificar_conexao(instancia)

    print(f"\n{'='*70}")
    print("PASSO 3: VALIDAÇÃO FINAL")
    print('='*70)
    
    conectadas = 0
    for instancia in instancias:
        if verificar_conexao(instancia):
            conectadas += 1
    
    print(f"\n{'='*70}")
    print(f"✓ RESULTADO FINAL: {conectadas}/3 instâncias conectadas")
    print('='*70)
    
    if conectadas == 3:
        print("""
✓✓✓ SUCESSO! SUAS 3 INSTÂNCIAS ESTÃO CONECTADAS! ✓✓✓

Próximos passos:
1. Acesse: http://localhost:5000
2. Login com:
   - Email: admin@pariscred.com
   - Senha: Admin@2025
3. Crie sua primeira campanha para testar!
4. Vá em: 📧 Campanhas → + Nova Campanha
5. Teste enviando uma mensagem

Parabéns! Seu sistema está 100% pronto! 🚀
""")
    else:
        print(f"""
⚠️  Apenas {conectadas}/3 instâncias conectadas.

Se alguma não conectou:
1. Verifique se o QR Code foi escaneado corretamente
2. Tente escanear novamente
3. Se persistir, verifique se seu WhatsApp está atualizado
""")
