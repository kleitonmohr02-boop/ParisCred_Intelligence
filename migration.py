"""
Script de Migração: Dicionários em Memória → SQLite
Executa: python migration.py
"""

import os
import sys
import json
from datetime import datetime

# Importar o database
from database import Database, UsuariosDB, CampanhasDB, HistoricoDB

def migrar_usuarios_iniciais():
    """Migra os usuários padrão para SQLite"""
    print("\n📝 Migrando usuários iniciais...")
    
    usuarios_iniciais = [
        {
            'email': 'admin@pariscred.com',
            'nome': 'Administrador ParisCred',
            'senha': 'Admin@2025',
            'role': 'admin'
        },
        {
            'email': 'vendedor1@pariscred.com',
            'nome': 'João Vendedor',
            'senha': 'Vendedor@123',
            'role': 'vendedor'
        }
    ]
    
    for usuario in usuarios_iniciais:
        try:
            # Verificar se já existe
            if UsuariosDB.obter(usuario['email']):
                print(f"  ⚠️  {usuario['email']} já existe, pulando...")
                continue
            
            # Criar novo usuário
            if UsuariosDB.criar(
                email=usuario['email'],
                nome=usuario['nome'],
                senha=usuario['senha'],
                role=usuario['role']
            ):
                print(f"  ✓ {usuario['email']} ({usuario['nome']}) - OK")
            else:
                print(f"  ✗ {usuario['email']} - ERRO ao criar")
        except Exception as e:
            print(f"  ✗ {usuario['email']} - ERRO: {str(e)}")
    
    print(f"✅ Usuários migrados com sucesso!")


def migrar_campanhas_iniciais():
    """Migra as campanhas padrão para SQLite"""
    print("\n📝 Migrando campanhas iniciais...")
    
    campanhas_iniciais = [
        {
            'nome': 'Campanha Inicial',
            'descricao': 'Primeira campanha de teste',
            'criador': 'admin@pariscred.com',
            'mensagem': 'Olá! Você tem uma ótima notícia!',
            'beneficiarios': [
                {'numero': '5548991105801', 'nome': 'Kleiton'},
                {'numero': '5548996057792', 'nome': 'Kleber Mohr'}
            ],
            'botoes': [
                {'id': '1', 'text': '💸 Ver meu Troco (Port)'},
                {'id': '2', 'text': '💰 Dinheiro Novo'}
            ],
            'instancias': ['Paris_01', 'Chip01', 'Chip02']
        }
    ]
    
    for campanha_dados in campanhas_iniciais:
        try:
            campanha_id = CampanhasDB.criar(
                nome=campanha_dados['nome'],
                descricao=campanha_dados['descricao'],
                criador=campanha_dados['criador'],
                mensagem=campanha_dados['mensagem'],
                beneficiarios=campanha_dados['beneficiarios'],
                botoes=campanha_dados['botoes'],
                instancias=campanha_dados['instancias']
            )
            
            if campanha_id:
                print(f"  ✓ ID {campanha_id}: {campanha_dados['nome']} - OK")
            else:
                print(f"  ✗ {campanha_dados['nome']} - ERRO ao criar")
        except Exception as e:
            print(f"  ✗ {campanha_dados['nome']} - ERRO: {str(e)}")
    
    print(f"✅ Campanhas migradas com sucesso!")


def exibir_status():
    """Exibe status do banco após migração"""
    print("\n📊 Status do Banco de Dados:")
    print("="*50)
    
    usuarios = UsuariosDB.listar_todos()
    campanhas = CampanhasDB.listar_todas()
    
    print(f"  Total de Usuários: {len(usuarios)}")
    for u in usuarios:
        print(f"    - {u['email']} ({u['role']})")
    
    print(f"\n  Total de Campanhas: {len(campanhas)}")
    for c in campanhas:
        print(f"    - ID {c['id']}: {c['nome']} de {c['criador']}")
    
    print("\n" + "="*50)


def validar_dados():
    """Valida integridade dos dados migrados"""
    print("\n✔️  Validando dados...")
    
    usuarios = UsuariosDB.listar_todos()
    campanhas = CampanhasDB.listar_todas()
    
    assert len(usuarios) > 0, "Nenhum usuário foi migrado"
    assert len(campanhas) > 0, "Nenhuma campanha foi migrada"
    
    # Verificar se admin existe
    admin = UsuariosDB.obter('admin@pariscred.com')
    assert admin is not None, "Admin não encontrado"
    assert admin['role'] == 'admin', "Admin não tem role 'admin'"
    
    # Verificar senha do admin (deve fazer login)
    senha_ok = UsuariosDB.verificar_senha('admin@pariscred.com', 'Admin@2025')
    assert senha_ok, "Senha do admin não funciona"
    
    print("  ✓ Todos os dados foram validados com sucesso!")


def backup_banco_anterior():
    """Cria backup do banco anterior se existir"""
    if os.path.exists('app.db'):
        import shutil
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'app_backup_{timestamp}.db'
        shutil.copy('app.db', backup_name)
        print(f"💾 Backup do BD anterior: {backup_name}")
        return backup_name
    return None


def main():
    """Função principal"""
    print("\n" + "="*60)
    print("  🔄 MIGRAÇÃO: Dicionários em Memória → SQLite")
    print("="*60)
    
    try:
        # Backup do banco anterior (se houver)
        backup_banco_anterior()
        
        # Inicializar banco
        print("\n🔧 Inicializando banco de dados...")
        db = Database("app.db")
        print("  ✓ Banco criado/conectado com sucesso")
        
        # Migrar dados iniciais
        migrar_usuarios_iniciais()
        migrar_campanhas_iniciais()
        
        # Validar dados
        validar_dados()
        
        # Exibir status
        exibir_status()
        
        print("\n" + "="*60)
        print("  ✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("\n📋 Próximos passos:")
        print("  1. Renomear app.py → app_old.py")
        print("  2. Renomear app_novo.py → app.py")
        print("  3. Executar: pip install bcrypt (se não tiver)")
        print("  4. Executar: python app.py")
        print("\n" + "="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NA MIGRAÇÃO: {str(e)}")
        print("\nTrecho do erro:")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    sucesso = main()
    sys.exit(0 if sucesso else 1)
