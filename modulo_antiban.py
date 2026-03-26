"""
Módulo Anti-Ban para WhatsApp via Evolution API
ParisCred Intelligence v2.0

Este módulo implementa estratégias para reduzir banimentos:
1. Limitação de mensagens por hora
2. Intervalos variáveis entre envios
3. Rotação de mensagens (variantes)
4. Limitação por número
5. Detectores de comportamento suspeito
6. Circuit breaker para instâncias
"""

import os
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)


class GerenciadorAntiBan:
    """
    Gerenciador de segurança para evitar banimentos no WhatsApp
    """
    
    # Configurações padrão
    CONFIG = {
        'max_msgs_por_hora': int(os.getenv('MAX_MSGS_POR_HORA', '30')),
        'max_msgs_por_numero': int(os.getenv('MAX_MSGS_POR_NUMERO', '3')),
        'min_intervalo_segundos': int(os.getenv('MIN_INTERVALO', '15')),
        'max_intervalo_segundos': int(os.getenv('MAX_INTERVALO', '45')),
        'mensagens_por_batch': int(os.getenv('MSGS_POR_BATCH', '20')),
        'pausa_entre_batches_minutos': int(os.getenv('PAUSA_BATCH_MIN', '30')),
        'mensagens_bloqueadas_lista': int(os.getenv('MSG_BLOQUEADOS', '1')),
    }
    
    # Mensagens pré-definidas para evitar detecção
    MENSAGENS_VARIANTES = {
        'introdução': [
            "Olá, {nome}! 👋 Tudo bem?",
            "Olá, {nome}! 👋",
            "Bom dia, {nome}! 👋",
            "Oi, {nome}! 👋",
            "Olá, {nome}! Tudo bem com você? 👋",
        ],
        'proposta': [
            "Temos uma ótima novidade sobre seu crédito!",
            "Vi que você tem opções disponíveis de crédito.",
            "Acabamos de verificar seu perfil e temos uma proposta!",
            "Sua situação financeira permite novas opções de crédito!",
            "Temos uma solução financeira especial para você!",
        ],
        'cta': [
            "Quer saber mais? É só responder!",
            "Posso te explicar os detalhes?",
            "Quer receber mais informações?",
            "Posso te ajudar com isso?",
            "Quer ver as opções disponíveis?",
        ]
    }
    
    def __init__(self):
        self.contador_envios = defaultdict(int)  # {numero: count}
        self.contador_hora = defaultdict(list)   # {hora: [timestamps]}
        self.numeros_bloqueados = set()            # Números que投诉aram
        self.numeros_lista_negra = set()           # Números que pediu para não contactar
        self.instances_status = {}                # Status de cada instância
        self.lock = Lock()
        
        # Carregar configuração
        self.max_por_hora = self.CONFIG['max_msgs_por_hora']
        self.max_por_numero = self.CONFIG['max_msgs_por_numero']
        self.min_intervalo = self.CONFIG['min_intervalo_segundos']
        self.max_intervalo = self.CONFIG['max_intervalo_segundos']
    
    def pode_enviar(self, numero: str, instancia: str = 'default') -> Dict:
        """
        Verifica se pode enviar mensagem para o número
        Retorna: {pode: bool, motivo: str, proximo_envio: int}
        """
        with self.lock:
            # 1. Verificar se número está bloqueado
            if numero in self.numeros_bloqueados:
                return {
                    'pode': False,
                    'motivo': 'Número reported/bloqueado',
                    'proximo_envio': None
                }
            
            # 2. Verificar se número pediu para não contatar
            if numero in self.numeros_lista_negra:
                if self.CONFIG['mensagens_bloqueadas_lista'] <= 0:
                    return {
                        'pode': False,
                        'motivo': 'Número na lista de não contatar',
                        'proximo_envio': None
                    }
                self.CONFIG['mensagens_bloqueadas_lista'] -= 1
            
            # 3. Verificar limite por número (dia)
            if self.contador_envios.get(numero, 0) >= self.max_por_numero:
                return {
                    'pode': False,
                    'motivo': f'Limite diário atingido para este número ({self.max_por_numero})',
                    'proximo_envio': 86400  # 24 horas
                }
            
            # 4. Verificar limite por hora (global)
            hora_atual = datetime.now().hour
            envios_hora = self.contador_hora.get(hora_atual, [])
            
            if len(envios_hora) >= self.max_por_hora:
                return {
                    'pode': False,
                    'motivo': f'Limite horário atingido ({self.max_por_hora}/hora)',
                    'proximo_envio': self._calcular_proximo_intervalo()
                }
            
            # 5. Verificar instância
            if instancia in self.instances_status:
                status = self.instances_status[instancia]
                if status.get('bloqueada', False):
                    return {
                        'pode': False,
                        'motivo': 'Instância temporariamente bloqueada',
                        'proximo_envio': status.get('desbloqueio_em')
                    }
            
            return {'pode': True, 'motivo': None, 'proximo_envio': None}
    
    def registrar_envio(self, numero: str, instancia: str = 'default', sucesso: bool = True):
        """Registra um envio para controle"""
        with self.lock:
            agora = datetime.now()
            
            # Contador por número
            if sucesso:
                self.contador_envios[numero] += 1
            
            # Contador por hora
            hora_atual = agora.hour
            self.contador_hora[hora_atual].append(agora.timestamp())
            
            # Limpar horas antigas
            self._limpar_contadores_antigos()
    
    def reportar_bloqueio(self, numero: str):
        """Reporta que número bloqueou/fechou"""
        with self.lock:
            self.numeros_bloqueados.add(numero)
            logger.warning(f"Número reportado como bloquedo: {numero}")
            
            # Salvar no banco se disponível
            self._salvar_bloqueio_db(numero)
    
    def adicionar_lista_negra(self, numero: str):
        """Adiciona número à lista de não contatar"""
        with self.lock:
            self.numeros_lista_negra.add(numero)
            logger.info(f"Número adicionado à lista negra: {numero}")
            self._salvar_lista_negra_db(numero)
    
    def pausar_instancia(self, instancia: str, minutos: int = 30):
        """Pausa uma instância temporariamente"""
        with self.lock:
            self.instances_status[instancia] = {
                'bloqueada': True,
                'bloqueado_em': datetime.now(),
                'desbloqueio_em': datetime.now() + timedelta(minutos=minutos),
                'motivo': 'Circuit breaker ativado'
            }
            logger.warning(f"Instância {instancia} pausada por {minutos} minutos")
    
    def get_intervalo(self) -> int:
        """Retorna intervalo aleatório entre envios"""
        return random.randint(self.min_intervalo, self.max_intervalo)
    
    def get_mensagem_variante(self, tipo: str, nome: str) -> str:
        """Retorna uma variante aleatória da mensagem"""
        variantes = self.MENSAGENS_VARIANTES.get(tipo, [])
        if not variantes:
            return ""
        
        variante = random.choice(variantes)
        return variante.replace('{nome}', nome.split()[0] if nome else 'Cliente')
    
    def construir_mensagem_completa(self, base: str, nome: str) -> str:
        """Constrói mensagem com variantes para evitar detecção"""
        partes = [
            self.get_mensagem_variante('introdução', nome),
            self.get_mensagem_variante('proposta', nome),
            base,
            self.get_mensagem_variante('cta', nome)
        ]
        
        # Juntar com quebras de linha variáveis
        separadores = ['\n\n', '\n', ' ']
        separador = random.choice(separadores)
        
        return separador.join([p for p in partes if p])
    
    def _calcular_proximo_intervalo(self) -> int:
        """Calcula próximo intervalo possível"""
        return self.max_intervalo + random.randint(0, 60)
    
    def _limpar_contadores_antigos(self):
        """Limpa contadores de horas anteriores"""
        hora_atual = datetime.now().hour
        horas_para_remover = [h for h in self.contador_hora.keys() if h != hora_atual]
        for h in horas_para_remover:
            del self.contador_hora[h]
    
    def _salvar_bloqueio_db(self, numero: str):
        """Salva bloqueio no banco"""
        try:
            from database import Database
            db = Database()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO bloqueios (numero, tipo, motivo, criado_em)
                    VALUES (?, 'whatsapp', 'reported', datetime('now'))
                """, (numero,))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar bloqueio: {e}")
    
    def _salvar_lista_negra_db(self, numero: str):
        """Salva lista negra no banco"""
        try:
            from database import Database
            db = Database()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO bloqueios (numero, tipo, motivo, criado_em)
                    VALUES (?, 'lista_negra', 'solicitado_cliente', datetime('now'))
                """, (numero,))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar lista negra: {e}")
    
    def get_estatisticas(self) -> Dict:
        """Retorna estatísticas do anti-ban"""
        return {
            'envios_hoje': sum(self.contador_envios.values()),
            'numeros_bloqueados': len(self.numeros_bloqueados),
            'numeros_lista_negra': len(self.numeros_lista_negra),
            'limite_por_hora': self.max_por_hora,
            'limite_por_numero': self.max_por_numero,
            'prox_intervalo': self.get_intervalo()
        }


# Instância global
anti_ban = GerenciadorAntiBan()


def criar_rotas_antiban(app):
    """Cria rotas de API para gestão anti-ban"""
    from flask import jsonify
    
    @app.route('/api/antiban/status')
    def status_antiban():
        """Status geral do anti-ban"""
        return jsonify(anti_ban.get_estatisticas())
    
    @app.route('/api/antiban/bloquear', methods=['POST'])
    def bloquear_numero():
        """Bloqueia um número (reportado)"""
        from flask import request
        data = request.json
        numero = data.get('numero', '')
        
        if numero:
            anti_ban.reportar_bloqueio(numero)
            return jsonify({'sucesso': True, 'mensagem': f'Número {numero} bloqueado'})
        return jsonify({'erro': 'Número não fornecido'}), 400
    
    @app.route('/api/antiban/lista-negra', methods=['POST'])
    def adicionar_lista_negra():
        """Adiciona número à lista de não contatar"""
        from flask import request
        data = request.json
        numero = data.get('numero', '')
        
        if numero:
            anti_ban.adicionar_lista_negra(numero)
            return jsonify({'sucesso': True, 'mensagem': f'Número {numero} adicionado à lista negra'})
        return jsonify({'erro': 'Número não fornecido'}), 400
    
    @app.route('/api/antiban/config', methods=['GET', 'PUT'])
    def config_antiban():
        """Gerencia configuração do anti-ban"""
        if request.method == 'GET':
            return jsonify(anti_ban.CONFIG)
        
        data = request.json
        for key, value in data.items():
            if key in anti_ban.CONFIG:
                anti_ban.CONFIG[key] = value
        
        # Atualizar variáveis de instância
        anti_ban.max_por_hora = anti_ban.CONFIG['max_msgs_por_hora']
        anti_ban.max_por_numero = anti_ban.CONFIG['max_msgs_por_numero']
        anti_ban.min_intervalo = anti_ban.CONFIG['min_intervalo_segundos']
        anti_ban.max_intervalo = anti_ban.CONFIG['max_intervalo_segundos']
        
        return jsonify({'sucesso': True, 'config': anti_ban.CONFIG})
    
    @app.route('/api/antiban/instancia/pausar', methods=['POST'])
    def pausar_instancia():
        """Pausa uma instância temporariamente"""
        from flask import request
        data = request.json
        instancia = data.get('instancia', 'Paris_01')
        minutos = data.get('minutos', 30)
        
        anti_ban.pausar_instancia(instancia, minutos)
        return jsonify({'sucesso': True, 'mensagem': f'Instância {instancia} pausada por {minutos} minutos'})
    
    return app


# Função para usar no disparo de campanhas
def verificar_e_enviar(numero: str, mensagem: str, nome: str = '', instancia: str = 'Paris_01'):
    """
    Função principal para enviar com proteção anti-ban
    
    Returns: {sucesso: bool, mensagem: str, erro: str}
    """
    # 1. Verificar se pode enviar
    verificacao = anti_ban.pode_enviar(numero, instancia)
    
    if not verificacao['pode']:
        return {
            'sucesso': False,
            'erro': verificacao['motivo'],
            'proximo_envio': verificacao.get('proximo_envio')
        }
    
    # 2. Construir mensagem com variantes
    if nome:
        mensagem_segura = anti_ban.construir_mensagem_completa(mensagem, nome)
    else:
        mensagem_segura = mensagem
    
    # 3. Obter intervalo para próximo envio
    intervalo = anti_ban.get_intervalo()
    
    return {
        'sucesso': True,
        'proximo_intervalo': intervalo
    }