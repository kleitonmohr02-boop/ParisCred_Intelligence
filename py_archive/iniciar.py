#!/usr/bin/env python3
"""
Script de inicialização do Disparador ParisCred
Inicia o servidor e abre o navegador automaticamente
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

# Adiciona o diretório do projeto ao PATH
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def main():
    print("\n" + "="*70)
    print(" 🚀 DISPARADOR PARISCRED - SISTEMA DE INICIALIZAÇÃO")
    print("="*70 + "\n")
    
    # Verifica se servidor.py existe
    servidor_path = project_dir / 'servidor.py'
    if not servidor_path.exists():
        print("❌ ERRO: servidor.py não encontrado!")
        return 1
    
    print("📍 Diretório do projeto:", project_dir)
    print("📄 Servidor encontrado:", servidor_path)
    print()
    
    # Tenta importar requisitos
    try:
        import requests
        print("✓ requests importado com sucesso")
    except ImportError:
        print("⚠️  Instalando dependências...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests', '-q'])
    
    print("\n" + "-"*70)
    print(" Iniciando servidor...")
    print("-"*70 + "\n")
    
    # Inicia o servidor em um subprocesso
    try:
        # Muda para o diretório do projeto
        os.chdir(project_dir)
        
        # Inicia o servidor
        servidor = subprocess.Popen([sys.executable, 'servidor.py'])
        
        # Aguarda o servidor iniciar
        time.sleep(2)
        
        # Abre o navegador
        url = 'http://localhost:5000'
        print(f"\n✓ Servidor iniciado!")
        print(f"📱 Abrindo navegador em {url}...")
        
        time.sleep(1)
        webbrowser.open(url)
        
        print(f"\n{'='*70}")
        print(f" ✓ SISTEMA PRONTO!")
        print(f"{'='*70}")
        print(f"\n📍 URL: {url}")
        print(f"📋 Pressione Ctrl+C para parar o servidor\n")
        
        # Mantém o servidor rodando
        servidor.wait()
        
    except KeyboardInterrupt:
        print("\n\n✓ Finalizando servidor...")
        servidor.terminate()
        servidor.wait()
        print("✓ Servidor finalizado com sucesso")
        return 0
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
