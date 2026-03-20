#!/usr/bin/env python3
"""
Script de Inicialização - ParisCred Intelligence
Executa setup inicial e inicia a aplicação
"""

import os
import subprocess
import sys
from pathlib import Path


def print_header(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")


def print_success(msg):
    print(f"✅ {msg}")


def print_error(msg):
    print(f"❌ {msg}")
    sys.exit(1)


def print_info(msg):
    print(f"ℹ️  {msg}")


def init_database():
    """Inicializa banco de dados"""
    print_header("1. Inicializando Banco de Dados")
    
    try:
        from database import Database, UsuariosDB
        
        # Criar banco
        db = Database("app.db")
        print_success("Banco de dados criado/verificado")
        
        # Criar usuário admin padrão
        if not UsuariosDB.obter('admin@pariscred.com'):
            UsuariosDB.criar(
                email='admin@pariscred.com',
                nome='Administrador',
                senha='Admin@2025',
                role='admin'
            )
            print_success("Usuário admin criado: admin@pariscred.com / Admin@2025")
        else:
            print_info("Usuário admin já existe")
        
        # Criar usuário vendedor padrão
        if not UsuariosDB.obter('vendedor@pariscred.com'):
            UsuariosDB.criar(
                email='vendedor@pariscred.com',
                nome='Vendedor Padrão',
                senha='Vendedor@123',
                role='vendedor'
            )
            print_success("Usuário vendedor criado: vendedor@pariscred.com / Vendedor@123")
    
    except Exception as e:
        print_error(f"Erro ao inicializar banco: {e}")


def init_skills():
    """Inicializa skills"""
    print_header("2. Inicializando Skills")
    
    try:
        from skill_crm import ClientesDB
        from skill_financeiro import FinanceiroDB
        from skill_whatsapp import WhatsAppDB
        from skill_admin import AdminReportsDB
        
        print_success("CRM Skill")
        print_success("Financeiro Skill")
        print_success("WhatsApp Skill")
        print_success("Admin Skill")
        
    except Exception as e:
        print_error(f"Erro ao inicializar skills: {e}")


def check_requirements():
    """Verifica se requirements está instalado"""
    print_header("3. Verificando Dependências")
    
    required_packages = [
        'flask',
        'flask_cors',
        'bcrypt',
        'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package}")
        except ImportError:
            missing.append(package)
            print_error(f"{package} (não instalado)")
    
    if missing:
        print_info(f"\nInstale com: pip install {' '.join(missing)}")
        print_error("Dependências faltando")


def create_env():
    """Cria arquivo .env se não existir"""
    if not os.path.exists('.env'):
        print_header("4. Criando arquivo .env")
        
        with open('.env', 'w') as f:
            f.write("""FLASK_ENV=development
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=CONSIGNADO123
DATABASE_PATH=app.db
""")
        print_success(".env criado")
    else:
        print_info(".env já existe")


def show_info():
    """Mostra informações úteis"""
    print_header("5. Informações de Acesso")
    
    print("""
    🌐 Acessar em:          http://localhost:5000
    
    👤 Credenciais Admin:
       Email:               admin@pariscred.com
       Senha:               Admin@2025
       Acesso:              http://localhost:5000 → Dashboard ADM
    
    👤 Credenciais Vendedor:
       Email:               vendedor@pariscred.com
       Senha:               Vendedor@123
       Acesso:              http://localhost:5000 → Dashboard Vendedor
    
    📚 Documentações:
       - Projeto:           PROJECT_OVERVIEW.md
       - Setup:             GUIA_RAPIDO.md
       - Deploy:            DEPLOY_GOOGLE_CLOUD.md
       - Skills:            .github/skills/*/SKILL.md
    
    🚀 APIs Disponíveis:
       CRM:                 /api/crm/*
       Financeiro:          /api/financeiro/*
       WhatsApp:            /api/whatsapp/*
       Admin:               /api/admin/*
       Health:              /api/health
    """)


def main():
    """Executa setup completo"""
    
    print("\n")
    print("╔═══════════════════════════════════════════════╗")
    print("║  🚀 ParisCred Intelligence - Super Copilot  ║")
    print("║     Sistema SaaS de Crédito Consignado      ║")
    print("╚═══════════════════════════════════════════════╝\n")
    
    # Setup
    check_requirements()
    create_env()
    init_database()
    init_skills()
    show_info()
    
    # Iniciar aplicação
    print_header("6. Iniciando Aplicação")
    
    try:
        # Importar após setup
        from app_novo import app
        
        print_success("Iniciando Flask em http://localhost:5000")
        print_info("Pressione CTRL+C para parar")
        print()
        
        # Iniciar servidor
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    
    except KeyboardInterrupt:
        print_header("Aplicação Encerrada")
        print_success("Até logo!")
    
    except Exception as e:
        print_error(f"Erro ao iniciar: {e}")


if __name__ == '__main__':
    main()
