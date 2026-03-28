#!/usr/bin/env python3
"""
🚀 SCRIPT FINAL - CONECTAR 3 INSTÂNCIAS WHATSAPP
Baseado na documentação real da Evolution API v2.2.3
Endpoint correto: GET /instance/connect/:instanceName
"""

import requests
import json
import time

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
        'integration': 'WHATSAPP-BAILEYS'  # Integração com QR Code
    }
    
    try:
        url = f'{API_URL}/instance/create'
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print(f"✓ Status 201: INSTÂNCIA CRIADA COM SUCESSO!")
            return True
        elif response.status_code == 403 and 'already' in response.text.lower():
            print(f"⚠️  Instância já existe (OK)")
            return True 
        else:
            print(f"⚠️  Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Erro: {str(e)}")
        return False

def obter_qrcode(nome):
    """Obtém QR Code usando o endpoint correto"""
    
    print(f"\n{'='*70}")
    print(f"📲 OBTENDO QR CODE: {nome}")
    print('='*70)
    
    headers = {'apikey': API_KEY}
    
    # Endpoint CORRETO: /instance/connect/:instanceName
    url = f'{API_URL}/instance/connect/{nome}'
    
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✓ QR CODE OBTIDO COM SUCESSO!")
            
            # Exibe informação do QR code
            if isinstance(data, dict):
                print(f"\n╔════════════════════════════════════════╗")
                print(f"║ ESCANEIE ESTE QR CODE COM WHATSAPP    ║")
                print(f"║ Instância: {nome:30} ║")
                print(f"╚════════════════════════════════════════╝")
                
                # Verifica campos de QR code
                if 'qrcode' in data:
                    print(f"✓ Dado QR Code encontrado\n")
                    if isinstance(data['qrcode'], dict):
                        if 'base64' in data['qrcode']:
                            print(f"✓ QR Code Base64 disponível ({len(data['qrcode']['base64'])} caracteres)")
                        if 'code' in data['qrcode']:
                            print(f"✓ QR Code String disponível")
                
                return data
            else:
                print(f"✓ Resposta: {json.dumps(data, indent=2)[:300]}")
                return data
        else:
            print(f"✗ Erro {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"✗ Erro: {str(e)[:100]}")
        return None

def verificar_conexao(nome):
    """Verifica se a instância está conectada"""
    
    headers = {'apikey': API_KEY}
    url = f'{API_URL}/instance/connect/{nome}'
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verifica se está conectada
            if isinstance(data, dict):
                if data.get('instance', {}).get('status') == 'open':
                    return True, 'Conectada'
                elif 'qrcode' in data:
                    return False, 'Aguardando QR'
                else:
                    return False, 'Desconhecido'
            else:
                return False, 'Erro'
        else:
            return False, f'Status {response.status_code}'
            
    except:
        return False, 'Erro'

# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🚀 CONECTAR 3 INSTÂNCIAS WHATSAPP À EVOLUTION API          ║
║                                                              ║
║  Esta é a etapa FINAL para HLCotar seu sistema!             ║
║                                                              ║
║  Você vai:                                                   ║
║  1. Criar 3 instâncias (Paris_01, Chip01, Chip02)          ║
║  2. Escanear QR Codes com seu WhatsApp                      ║
║  3. Validar que tudo está conectado                         ║
║                                                              ║
║  ⏱️  Tempo esperado: 15-20 minutos                          ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    instancias = ['Paris_01', 'Chip01', 'Chip02']
    
    print(f"\n{'='*70}")
    print("✅ PASSO 1: CRIANDO INSTÂNCIAS")
    print('='*70)
    
    criadas = []
    for instancia in instancias:
        if criar_instancia(instancia):
            criadas.append(instancia)
            time.sleep(2)
    
    print(f"\n✓ {len(criadas)}/3 instâncias criadas ou já existem")
    
    print(f"\n{'='*70}")
    print("✅ PASSO 2: GERAR E ESCANEAR QR CODES")
    print('='*70)
    
    for instancia in criadas:
        obter_qrcode(instancia)
        
        print(f"\n{'─'*70}")
        print(f"INSTRUÇÕES PARA {instancia}")
        print(f"{'─'*70}")
        print(f"""
1.  Abra WhatsApp no seu TELEFONE
2.  Toque no MENU (⋮)
3.  Vá para: Configurações → Aparelhos conectados
4.  Toque em: + Conectar um aparelho
5.  Câmera vai abrir - ESCANEIE O QR CODE ACIMA
6.  Aguarde: ✓ Conectado

TEMPO: Aproximadamente 1-2 minutos
""")
        
        input(f"Pressione ENTER após escanear QR Code de {instancia}...\n")

    print(f"\n{'='*70}")
    print("✅ PASSO 3: VALIDAÇÃO FINAL")
    print('='*70)
    
    conectadas = 0
    for instancia in criadas:
        ok, status = verificar_conexao(instancia)
        symbol = '✓' if ok else '✗'
        print(f"{symbol} {instancia:15} → {status}")
        if ok:
            conectadas += 1

    print(f"\n{'='*70}")
    if conectadas == len(criadas):
        print(f"✓✓✓ SUCESSO!!! {conectadas}/{ len(criadas)} INSTÂNCIAS CONECTADAS! ✓✓✓")
        print('='*70)
        print("""
🎉 PARABÉNS! SEU SISTEMA ESTÁ 100% PRONTO!

Próximas ações:
1. Abra seu navegador: http://localhost:5000

2. Faça login:
   Email: admin@pariscred.com
   Senha: Admin@2025

3. Navegue para: 📧 CAMPANHAS

4. Crie uma NOVA CAMPANHA:
   - Nome: Teste
   - Beneficiários: Seu próprio telefone
   - Mensagem: "Olá, teste de disparo!"
   - Instância: Paris_01 (ou qualquer uma)

5. Clique em: ⚡ DISPARAR

6. Verifique seu WhatsApp - a mensagem deve chegar em segundos!

7. Para produção, vá em: ⚙️ PAINEL ADM

============================================================
✓ Seu sistema de marketing WhatsApp está pronto para usar!
============================================================
""")
    else:
        print(f"⚠️  Apenas {conectadas}/{len(criadas)} instâncias conectadas")
        print('='*70)
        print(f"""
Se não conseguiu conectar:

1. VERIFIQUE SEU WHATSAPP:
   - Está atualizado? Atualize a través de Play Store/App Store
   - Tem internet? Verifique a conexão
   - Tem 2FA? Desabilite na seção Configurações > Segurança

2. QR CODE NÃO ESCANEIA?
   - Aumente o brilho da tela do PC
   - Aproxime mais o telefone
   - Tente com a câmera traseira

3. DESCONECTOU LOGO?
   - Pode ser que o QR Code expirou
   - Simplesmente execute o script novamente
   - Repita a scanagem

4. AINDA NÃO FUNCIONA?
   - Contacte o suporte ou documentação
   - A Evolution API pode ter atualizado
""")

    print(f"\n🎉 Obrigado por usar ParisCred_Intelligence!")
    print(f"Versão: 2.0.0 | WhatsApp Baileys + SQLite\n")
