#!/usr/bin/env python3
"""Cria instâncias WhatsApp corretamente com integração suportada"""

import requests
import json
import time
from datetime import datetime

API_URL = 'http://localhost:8080'
API_KEY = 'CONSIGNADO123'

def delete_instance(name):
    """Deleta uma instância se existir"""
    
    endpoints = [
        f'/instance/{name}/delete',
        f'/instance/{name}',
        f'/webhook/delete/{name}',
        f'/api/instance/{name}/delete',
    ]
    
    headers = {
        'apikey': API_KEY,
        'Content-Type': 'application/json'
    }
    
    for endpoint in endpoints:
        try:
            url = API_URL + endpoint
            response = requests.delete(
                url,
                headers=headers,
                timeout=5
            )
            
            if response.status_code in [200, 204]:
                print(f"✓ Instância '{name}' deletada")
                return True
        except:
            pass
    
    return False

def create_instance(name):
    """Cria uma nova instância WhatsApp"""
    
    print(f"\n{'='*70}")
    print(f"📱 CRIANDO INSTÂNCIA: {name}")
    print('='*70)
    
    # Primeiro tenta deletar se já existir
    print(f"🔄 Verificando se precisa deletar versão anterior...")
    delete_instance(name)
    time.sleep(2)
    
    payload = {
        'instanceName': name,
        'qrcode': True,
    }
    
    headers = {
        'apikey': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        url = API_URL + '/instance/create'
        print(f"\n📍 Endpoint: POST /instance/create")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30  # Aguardar mais já que pode ser lento
        )
        
        print(f"\n✓ Status: {response.status_code}")
        
        data = response.json()
        print(f"\n📦 Resposta completa:")
        print(json.dumps(data, indent=2)[:800])
        
        if response.status_code in [200, 201]:
            print(f"\n✓✓✓ INSTÂNCIA CRIADA COM SUCESSO! ✓✓✓")
            return data
        else:
            print(f"\n⚠️  Erro ao criar")
            return None
            
    except requests.exceptions.Timeout:
        print(f"\n⏳ Timeout (pode estar criando em background)")
        return None
    except Exception as e:
        print(f"\n✗ Erro: {str(e)}")
        return None

def get_qrcode(name):
    """Obtém QR Code de uma instância"""
    
    print(f"\n{'='*70}")
    print(f"📲 OBTENDO QR CODE: {name}")
    print('='*70)
    
    endpoints = [
        f'/instance/{name}/qrcode',
        f'/{name}/qrcode',
        f'/qrcode/{name}',
    ]
    
    headers = {'apikey': API_KEY}
    
    for endpoint in endpoints:
        try:
            url = API_URL + endpoint
            print(f"\n🔍 Tentando: GET {endpoint}")
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"\n✓ QR CODE OBTIDO!")
                data = response.json()
                
                if 'qrcode' in data:
                    qr_content = data['qrcode']
                    print(f"\n📲 QR Code (primeiros 100 chars): {qr_content[:100]}")
                    return data
                else:
                    print(f"\n📦 Resposta: {json.dumps(data, indent=2)[:300]}")
                    return data
        except Exception as e:
            print(f"   ✗ Erro: {str(e)[:60]}")
    
    return None

# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🚀 CRIADOR DE INSTÂNCIAS WHATSAPP - CORRIGIDO              ║
║                                                              ║
║  Este script vai:                                            ║
║  1. Criar 3 instâncias WhatsApp                             ║
║  2. Gerar QR Code para cada uma                             ║
║  3. Guiar você a escanear no telefone                       ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    instancias = ['Paris_01', 'Chip01', 'Chip02']
    
    for instancia in instancias:
        # Criar
        resultado = create_instance(instancia)
        
        # Aguardar (a Evolution API é lenta)
        time.sleep(3)
        
        # Obter QR Code
        qr = get_qrcode(instancia)
        
        # Pedir para o usuário escanear
        input(f"\n✅ Escaneie o QR Code de {instancia} com seu WhatsApp e pressione ENTER\n")
    
    print(f"\n{'='*70}")
    print(f"✓✓✓ PROCESSO CONCLUÍDO!")
    print(f"{'='*70}")
