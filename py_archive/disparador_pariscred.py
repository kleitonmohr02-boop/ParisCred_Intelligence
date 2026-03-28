import requests
import json
import time
import random
from itertools import cycle
from config import EVOLUTION_URL, GLOBAL_API_KEY, DELAY_MIN, DELAY_MAX

class DispuradorParisCred:
    """
    Gerenciador de disparos de mensagens interativas via Evolution API.
    Implementa rodízio entre instâncias e envio de mensagens com botões CTA.
    """
    
    def __init__(self, instancias: list):
        """
        Inicializa o disparador.
        
        Args:
            instancias: Lista de nomes de instâncias (ex: ['Chip01', 'Chip02', 'Chip03'])
        """
        self.instancias = instancias
        self.rodizio = cycle(instancias)
        self.contador = 0
        self.headers = {
            'apikey': GLOBAL_API_KEY,
            'Content-Type': 'application/json'
        }
        
        print(f"✓ Disparador inicializado com {len(instancias)} instâncias")
        print(f"  Instâncias: {', '.join(instancias)}\n")
    
    def proxima_instancia(self):
        """Retorna a próxima instância no rodízio."""
        instancia = next(self.rodizio)
        self.contador += 1
        return instancia
    
    def criar_mensagem_com_botoes(self, numero_destinatario: str, nome_cliente: str):
        """
        Cria uma mensagem interativa com botões CTA.
        
        Args:
            numero_destinatario: Número no formato +5511999999999
            nome_cliente: Nome do cliente para personalização
            
        Returns:
            dict: Payload da mensagem
        """
        saudacao = f"Olá, {nome_cliente}! 👋\n\nVocê tem uma ótima notícia! Verifique suas opções abaixo:"
        
        payload = {
            "number": numero_destinatario,
            "text": saudacao,
            "buttons": [
                {
                    "id": "1",
                    "text": "💸 Ver meu Troco (Port)"
                },
                {
                    "id": "2", 
                    "text": "💰 Dinheiro Novo"
                }
            ]
        }
        
        return payload
    
    def enviar_mensagem(self, numero_destinatario: str, nome_cliente: str):
        """
        Envia uma mensagem com botões para um beneficiário, alternando instâncias.
        
        Args:
            numero_destinatario: Número do WhatsApp (+5511999999999)
            nome_cliente: Nome do cliente
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        
        # Pega próxima instância
        instancia = self.proxima_instancia()
        
        # Cria payload
        payload = self.criar_mensagem_com_botoes(numero_destinatario, nome_cliente)
        
        # Constrói URL
        url = f"{EVOLUTION_URL}/{instancia}/message/send"
        
        try:
            print(f"📤 Envio #{self.contador} | Instância: {instancia}")
            print(f"   Destinatário: {numero_destinatario}")
            print(f"   Cliente: {nome_cliente}")
            
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✓ Sucesso!\n")
                return True
            else:
                print(f"   ✗ Erro {response.status_code}: {response.text[:100]}\n")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"   ✗ Erro de conexão\n")
            return False
        except requests.exceptions.Timeout:
            print(f"   ✗ Timeout\n")
            return False
        except Exception as e:
            print(f"   ✗ Erro: {str(e)}\n")
            return False
    
    def campanhas_automaticas(self, dados_beneficiarios: list, executar=True):
        """
        Executa campanha de envios automáticos com delay.
        
        Args:
            dados_beneficiarios: Lista de dicts com 'numero' e 'nome'
                                Exemplo: [
                                    {'numero': '+5511999999999', 'nome': 'João'},
                                    {'numero': '+5511988888888', 'nome': 'Maria'}
                                ]
            executar: Se False, apenas simula (não envia de verdade)
        """
        
        total = len(dados_beneficiarios)
        
        print("=" * 60)
        print(f"🚀 INICIANDO CAMPANHA - {total} beneficiários")
        print("=" * 60 + "\n")
        
        for idx, beneficiario in enumerate(dados_beneficiarios, 1):
            numero = beneficiario.get('numero')
            nome = beneficiario.get('nome', 'Cliente')
            
            if not numero:
                print(f"⚠️  Beneficiário #{idx} sem número. Pulando...\n")
                continue
            
            # Envia mensagem
            if executar:
                self.enviar_mensagem(numero, nome)
            else:
                print(f"[SIMULADO] Envio #{idx} | {nome} ({numero})\n")
            
            # Pula último delay
            if idx < total:
                delay = random.randint(DELAY_MIN, DELAY_MAX)
                print(f"⏳ Aguardando {delay}s antes do próximo envio...\n")
                time.sleep(delay)
        
        print("=" * 60)
        print("✓ Campanha concluída!")
        print("=" * 60)


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == '__main__':
    # Configuração das instâncias (chips)
    # Usando Paris_01 como principal (criada) + fallbacks
    instancias = ['Paris_01', 'Chip01', 'Chip02']
    
    # Cria disparador
    disparador = DispuradorParisCred(instancias)
    
    # Dados dos beneficiários (número + nome)
    beneficiarios = [
        {'numero': '5548991105801', 'nome': 'Kleiton'},
        {'numero': '5548996057792', 'nome': 'Kleber Mohr'},
    ]
    
    # Executa campanha
    # Mude executar=False para simular sem enviar de verdade
    disparador.campanhas_automaticas(beneficiarios, executar=True)
