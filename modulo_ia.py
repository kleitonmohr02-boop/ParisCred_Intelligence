"""
Módulo de Inteligência Artificial para ParisCred
Usa Google Gemini API para automação de conversas
Gratuito para começar (Google AI Studio)
"""

import os
import requests
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class IAAgente:
    """Agente de IA usando Google Gemini"""
    
    def __init__(self, model: str = "gemini-1.5-flash"):
        self.model = model
        self.api_key = os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.timeout = 30
        
        self.system_prompt = """Você é o assistente virtual da ParisCred Intelligence, uma empresa líder em crédito consignado no Brasil. 

REGRAS DE NEGÓCIO:
1. Você ajuda com empréstimo consignado para aposentados e pensionistas do INSS.
2. As taxas da ParisCred variam de 1.2% a 1.7% ao mês (as melhores do mercado).
3. Prazos podem chegar a até 84 parcelas.
4. Valores de R$ 500 a R$ 50.000.
5. Se o cliente perguntar o valor, peça o CPF ou peça para ele simular chamando um atendente humano.
6. Seja sempre gentil e use emojis moderadamente.
7. Se não souber algo, peça para o cliente aguardar que um consultor já irá responder.

FORMATO DE RESPOSTA:
- Responda de forma curta e direta para o WhatsApp (máximo 3 linhas)
- Não envie listas muito longas
- Sempre encerre com uma pergunta para manter a conversa ativa
- Use emojis moderadamente (1-2 por mensagem)
- Seja prestativo e persuativo de forma ética"""

    def esta_online(self) -> bool:
        """Verifica se a API Gemini está configurada"""
        if not self.api_key:
            logger.warning("GEMINI_API_KEY não configurada")
            return False
        return True

    def gerar_resposta(self, mensagem: str, contexto_cliente: Dict = None) -> Optional[str]:
        """Gera uma resposta usando o Gemini"""
        if not self.esta_online():
            logger.warning("IA não configurada")
            return None
            
        try:
            nome_cliente = contexto_cliente.get('nome', 'Cliente') if contexto_cliente else 'Cliente'
            
            prompt = f"""{self.system_prompt}

Cliente: {nome_cliente}
Mensagem recebida: {mensagem}

Resposta (curta e direta):"""

            url = f"{self.base_url}/models/{self.model}:generateContent"
            params = {"key": self.api_key}
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 150,
                    "topP": 0.9,
                    "topK": 40
                }
            }
            
            response = requests.post(url, json=payload, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    resposta = data['candidates'][0]['content']['parts'][0]['text'].strip()
                    logger.info(f"Gemini IA gerou resposta para {nome_cliente}")
                    return resposta
            
            logger.warning(f"Resposta vazia da API: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta na IA: {str(e)}")
            return None
    
    def gerar_resposta_simples(self, mensagem: str) -> Optional[str]:
        """Versão simples sem contexto de cliente"""
        return self.gerar_resposta(mensagem, None)


class IAFallback:
    """Sistema de fallback quando IA não está disponível"""
    
    @staticmethod
    def responder(mensagem: str) -> str:
        """Respostas baseadas em palavras-chave"""
        msg = mensagem.lower()
        
        if any(word in msg for word in ["emprestimo", "empréstimo", "loan", "credito", "crédito"]):
            return """Ótimo! Vamos ajudá-lo com um empréstimo consignado! 

Qual valor você precisa? (R$ 500 a R$ 50.000)"""
        
        elif any(word in msg for word in ["simulacao", "simular", "quanto", "parcela", "calcular"]):
            return """Para simular, me diga:
1. Valor desejado
2. Número de parcelas (12 a 84x)

Qual informação você tem?"""
        
        elif any(word in msg for word in ["taxa", "juros", "porcento", "%"]):
            return """Nossas taxas são as melhores do mercado:
- 1.2% a 1.7% ao mês
- Prazos até 84x

Quer fazer uma simulação?"""
        
        elif any(word in msg for word in ["cpf", "documento", "rg"]):
            return """Para prosseguir, preciso do seu CPF e alguns dados.

Já tem esses documentos em mãos?"""
        
        elif any(word in msg for word in ["oi", "olá", "opa", "e ai", "bom dia", "boa tarde", "boa noite"]):
            return """Olá! Bem-vindo à ParisCred! 👋

Como posso ajudá-lo hoje?"""
        
        elif any(word in msg for word in ["whatsapp", "ligar", "telefone", "contato"]):
            return """Você pode falar conosco pelo WhatsApp ou ligação.

Prefere qual meio de contato?"""
        
        elif any(word in msg for word in ["obrigado", "obrigada", "valeu", "grato"]):
            return """Por nada! 😊

Precisa de mais alguma informação?"""
        
        else:
            return """Desculpe, não entendi completamente. 😅

Posso ajudar com:
- Empréstimo consignado
- Simulação de parcelas
- Taxas e prazos
- Informações sobre documentos

O que você precisa?"""


agente_ia = IAAgente()
ia_fallback = IAFallback()
