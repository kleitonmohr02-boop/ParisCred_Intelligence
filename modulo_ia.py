"""
Módulo de Inteligência Artificial Local para ParisCred
Usa Ollama (Qwen) para automação de conversas
"""

import os
import requests
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class IAAgente:
    """Agente de IA Local usando Ollama"""
    
    def __init__(self, model: str = "qwen2.5:7b"):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = model
        self.timeout = 30
        
        # System Prompt focado em ParisCred
        self.system_prompt = """
Você é o assistente virtual da ParisCred Intelligence, uma empresa líder em crédito consignado. 
Seu objetivo é ser extremamente educado, rápido, prestativo e persuasivo de forma ética.

REGRAS DE NEGÓCIO:
1. Você ajuda com empréstimo consignado para aposentados e pensionistas do INSS.
2. As taxas da ParisCred variam de 1.2% a 1.7% ao mês (as melhores do mercado).
3. Prazos podem chegar a até 84 parcelas.
4. Se o cliente perguntar o valor, peça o CPF ou peça para ele simular chamando um atendente humano.
5. Seja sempre gentil e use emojis moderadamente. 🚀👋💰
6. Se não souber algo, peça para o cliente aguardar que um consultor já irá responder.

FORMATO DE RESPOSTA:
- Responda de forma curta e direta para o WhatsApp.
- Não envie listas muito longas.
- Sempre encerre com uma pergunta para manter a conversa ativa.
"""

    def esta_online(self) -> bool:
        """Verifica se Ollama está respondendo"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def gerar_resposta(self, mensagem: str, contexto_cliente: Dict = None) -> Optional[str]:
        """Gera uma resposta usando o modelo local"""
        if not self.esta_online():
            logger.warning("IA Offline - Usando sistema de fallback")
            return None
            
        try:
            nome_cliente = contexto_cliente.get('nome', 'Cliente') if contexto_cliente else 'Cliente'
            
            prompt_final = f"{self.system_prompt}\n\nMensagem do Cliente ({nome_cliente}): {mensagem}\n\nResposta da IA:"
            
            payload = {
                "model": self.model,
                "prompt": prompt_final,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 150
                }
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                resposta = data.get('response', '').strip()
                logger.info(f"IA gerou resposta para {nome_cliente}")
                return resposta
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta na IA: {str(e)}")
            return None

# Instância global
agente_ia = IAAgente()
