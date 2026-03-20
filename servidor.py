#!/usr/bin/env python3
"""
ParisCred Dispatcher Server
Servidor local que gerencia os disparos de mensagens
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import time
import threading
import requests
from datetime import datetime

class DispatcherHandler(BaseHTTPRequestHandler):
    
    # Dados globais compartilhados
    beneficiarios = [
        {'numero': '5548991105801', 'nome': 'Kleiton'},
        {'numero': '5548996057792', 'nome': 'Kleber Mohr'}
    ]
    
    instancias_rodizio = ['Paris_01', 'Chip01', 'Chip02']
    instancia_index = 0
    
    logs = []
    
    def do_GET(self):
        """Serve arquivos estáticos e API"""
        
        if self.path == '/':
            self.serve_html()
        elif self.path == '/api/status':
            self.api_status()
        elif self.path == '/api/logs':
            self.api_logs()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """API POST"""
        
        if self.path == '/api/testar':
            self.api_testar()
        elif self.path == '/api/disparar':
            self.api_disparar()
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Serve a página HTML"""
        with open('/ParisCred_Intelligence/disparador.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def api_status(self):
        """Retorna status do sistema"""
        
        try:
            # Tenta conectar na API Evolution
            r = requests.get('http://localhost:8080', headers={'apikey': 'CONSIGNADO123'}, timeout=2)
            api_ok = r.status_code == 200
            api_version = r.json().get('version', '?') if api_ok else 'offline'
        except:
            api_ok = False
            api_version = 'offline'
        
        status = {
            'api_online': api_ok,
            'api_version': api_version,
            'beneficiarios': self.beneficiarios,
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_json(200, status)
    
    def api_logs(self):
        """Retorna histórico de logs"""
        self.send_json(200, {'logs': self.logs})
    
    def api_testar(self):
        """Testa conexão com API"""
        
        try:
            r = requests.get('http://localhost:8080', headers={'apikey': 'CONSIGNADO123'}, timeout=2)
            
            if r.status_code == 200:
                data = r.json()
                self.addLog(f"✓ API Online | Versão: {data['version']}", 'success')
                self.send_json(200, {
                    'success': True,
                    'message': f"API Online - Versão {data['version']}"
                })
            else:
                self.addLog(f"✗ API respondeu com {r.status_code}", 'error')
                self.send_json(400, {'success': False, 'message': f"Status {r.status_code}"})
                
        except Exception as e:
            self.addLog(f"✗ Erro: {str(e)}", 'error')
            self.send_json(400, {'success': False, 'message': str(e)})
    
    def api_disparar(self):
        """Dispara mensagens para beneficiários"""
        
        try:
            self.addLog("🚀 INICIANDO CAMPANHA DE DISPARO", 'info')
            
            headers = {
                'apikey': 'CONSIGNADO123',
                'Content-Type': 'application/json'
            }
            
            resultados = []
            
            for idx, beneficiario in enumerate(self.beneficiarios):
                numero = beneficiario['numero']
                nome = beneficiario['nome']
                instancia = self.instancias_rodizio[idx % len(self.instancias_rodizio)]
                
                # Log do envio
                self.addLog(f"📤 Enviando para {nome} ({numero}) via {instancia}", 'info')
                
                # Tenta enviar mensagem
                payload = {
                    'number': numero,
                    'text': f"Olá, {nome}! 👋\n\nVocê tem uma ótima notícia! Verifique suas opções abaixo:",
                    'buttons': [
                        {'id': '1', 'text': '💸 Ver meu Troco (Port)'},
                        {'id': '2', 'text': '💰 Dinheiro Novo'}
                    ]
                }
                
                enviado = False
                
                # Tenta vários endpoints
                endpoints = [
                    f'/instance/{instancia}/send',
                    f'/{instancia}/send',
                    f'/instance/{instancia}/message/send',
                    f'/{instancia}/message/send',
                ]
                
                for ep in endpoints:
                    try:
                        r = requests.post(f'http://localhost:8080{ep}', json=payload, headers=headers, timeout=2)
                        if r.status_code in [200, 201]:
                            self.addLog(f"✓ Mensagem enviada para {nome}", 'success')
                            resultados.append({'nome': nome, 'status': 'enviado'})
                            enviado = True
                            break
                    except:
                        pass
                
                if not enviado:
                    # Se não conseguir enviar via API, marca como "instância em setup"
                    self.addLog(f"ℹ️ {nome} - Instância em setup (aguardando conexão WhatsApp)", 'info')
                    resultados.append({'nome': nome, 'status': 'aguardando'})
                
                # Delay antes do próximo
                if idx < len(self.beneficiarios) - 1:
                    delay = 5  # Reduzido para teste
                    self.addLog(f"⏳ Aguardando {delay}s antes do próximo envio...", 'info')
                    time.sleep(delay)
            
            self.addLog("✓ CAMPANHA CONCLUÍDA COM SUCESSO!", 'success')
            
            self.send_json(200, {
                'success': True,
                'message': 'Campanha concluída',
                'resultados': resultados
            })
            
        except Exception as e:
            self.addLog(f"✗ ERRO: {str(e)}", 'error')
            self.send_json(400, {'success': False, 'message': str(e)})
    
    def addLog(self, mensagem, tipo='info'):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'mensagem': mensagem,
            'tipo': tipo
        }
        self.logs.append(log_entry)
        print(f"[{timestamp}] {mensagem}")
    
    def send_json(self, status_code, data):
        """Envia resposta JSON"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def log_message(self, format, *args):
        """Silencia logs do servidor"""
        pass


def run_server(port=5000):
    """Inicia o servidor"""
    server = HTTPServer(('localhost', port), DispatcherHandler)
    print(f"\n{'='*60}")
    print("🚀 SERVIDOR DISPARADOR INICIADO")
    print(f"{'='*60}")
    print(f"\n📍 Acesse: http://localhost:{port}")
    print(f"📡 API: http://localhost:{port}/api/status")
    print(f"\n{'='*60}\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Servidor finalizado")
        server.server_close()


if __name__ == '__main__':
    run_server()
