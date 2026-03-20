#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🚀 AUTO SETUP - Cria instância e gera QR Code automaticamente
"""

import requests
import json
import time
from config import EVOLUTION_URL, GLOBAL_API_KEY

def criar_instancia(nome_instancia: str):
    """Cria uma nova instância na Evolution API."""
    
    headers = {
        'apikey': GLOBAL_API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "instanceName": nome_instancia,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    
    print(f"\n📝 Criando instância '{nome_instancia}'...")
    
    try:
        response = requests.post(
            f'{EVOLUTION_URL}/instance/create',
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"✓ Instância criada com sucesso!")
            return True
        elif response.status_code == 400:
            data = response.json()
            if 'already exists' in str(data).lower():
                print(f"⚠️  Instância '{nome_instancia}' já existe (continuar...)")
                return True
            else:
                print(f"✗ Erro: {response.text[:200]}")
                return False
        else:
            print(f"✗ Erro {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Erro de conexão: {str(e)}")
        return False

def gerar_qrcode(nome_instancia: str):
    """Gera e exibe o QR Code para conectar a instância."""
    
    headers = {
        'apikey': GLOBAL_API_KEY
    }
    
    print(f"\n📱 Gerando QR Code para '{nome_instancia}'...")
    time.sleep(1)
    
    endpoints = [
        f'{EVOLUTION_URL}/instance/{nome_instancia}/qrcode',
        f'{EVOLUTION_URL}/{nome_instancia}/qrcode',
    ]
    
    for url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                print("\n" + "=" * 70)
                print("✓ QR CODE GERADO COM SUCESSO!")
                print("=" * 70)
                
                if 'qrcode' in data:
                    print("\n📲 ESCANEIE COM SEU CELULAR (WhatsApp):\n")
                    print(data['qrcode'])
                    print("\n" + "=" * 70)
                    print("⏱️  Aguardando sua confirmação...")
                    print("   (Abra WhatsApp → Escanear código QR)")
                    print("=" * 70 + "\n")
                    return True
                    
        except:
            continue
    
    print(f"✗ Não consegui gerar QR Code")
    return False

def verificar_conexao(nome_instancia: str, max_tentativas=30):
    """Verifica se a instância está conectada."""
    
    headers = {
        'apikey': GLOBAL_API_KEY
    }
    
    print(f"🔍 Verificando conexão...")
    
    endpoints = [
        f'{EVOLUTION_URL}/instance/{nome_instancia}',
        f'{EVOLUTION_URL}/{nome_instancia}',
    ]
    
    for tentativa in range(max_tentativas):
        for url in endpoints:
            try:
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    status = data.get('instance', {}).get('instance_status') or data.get('status')
                    
                    if status and 'connected' in str(status).lower():
                        print("\n" + "=" * 70)
                        print("✓ INSTÂNCIA CONECTADA COM SUCESSO!")
                        print("=" * 70)
                        print(f"\nStatus: {status}")
                        print(f"Instância: {nome_instancia}")
                        print("\n✓ Você está pronto para disparar mensagens!")
                        print("=" * 70 + "\n")
                        return True
                    else:
                        print(f"  [{tentativa+1}/{max_tentativas}] Status: {status} (aguardando...)")
                        
            except:
                continue
        
        time.sleep(2)
    
    print(f"\n⚠️  Não foi possível confirmar conexão após {max_tentativas} tentativas.")
    print("Verifique manualmente com:")
    print(f"\ncurl -X GET '{endpoints[0]}' -H 'apikey: {GLOBAL_API_KEY}'")
    return False

def main():
    """Executa o setup completo."""
    
    print("\n" + "=" * 70)
    print("🚀 AUTO SETUP - EVOLUTION API")
    print("=" * 70)
    
    nome_instancia = 'Paris_01'
    
    # Valida API Key
    if GLOBAL_API_KEY == 'SUA_API_KEY_AQUI':
        print("\n❌ ERRO: API Key não foi configurada!")
        print("\n📝 Edite o arquivo config.py e substitua:")
        print("   GLOBAL_API_KEY = 'SUA_API_KEY_AQUI'")
        print("\n   Por sua chave real do dashboard Evolution API.")
        return False
    
    print(f"\n✓ API Key configurada: {GLOBAL_API_KEY[:20]}...")
    print(f"✓ URL: {EVOLUTION_URL}")
    
    # 1. Criar instância
    if not criar_instancia(nome_instancia):
        print("\n❌ Não foi possível criar a instância. Verifique a API Key.")
        return False
    
    # 2. Gerar QR Code
    if not gerar_qrcode(nome_instancia):
        print("\n⚠️  QR Code não foi gerado. Tente manualmente.")
        return False
    
    # 3. Verificar conexão
    verificar_conexao(nome_instancia)
    
    return True

if __name__ == '__main__':
    sucesso = main()
    
    if sucesso:
        print("\n" + "=" * 70)
        print("✅ SETUP CONCLUÍDO!")
        print("=" * 70)
        print("\nAgora você pode executar:")
        print("  python disparador_pariscred.py")
        print("\n" + "=" * 70 + "\n")
