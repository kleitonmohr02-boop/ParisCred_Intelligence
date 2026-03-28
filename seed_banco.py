"""
Script de Seed - Popula o banco com dados fictícios para testes
Executar: python seed_banco.py
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

def gerar_cpf():
    """Gera CPF fictício válido"""
    return f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"

def gerar_telefone():
    """Gera telefone fictício brasileiro"""
    ddd = random.choice([11, 21, 31, 41, 51, 61, 71, 81, 91])
    numero = f"9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    return f"({ddd}) {numero}"

def seed_clientes(db, quantidade=50):
    """Popula tabela de clientes com dados fictícios"""
    print(f"\n🌱 Criando {quantidade} clientes...")
    
    status_opcoes = ['Novo Lead', 'Em Negociação', 'Pendente', 'Finalizado']
    bancos = ['Banco do Brasil', 'Caixa Econômica', 'Bradesco', 'Itaú', 'Santander', 'Safra', 'BMG', 'Pan']
    empresas = ['INSS', 'Governo Federal', 'Governo Estadual', 'Prefeitura', 'CLT']
    
    p = db.placeholder()
    
    clientes_criados = []
    for i in range(quantidade):
        nome = random.choice([
            'João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira', 'Carlos Souza',
            'Francisca Dias', 'Marcos Rodrigues', 'Juliana Ferreira', 'Ricardo Almeida',
            'Fernanda Costa', 'Bruno Martins', 'Carla Ribeiro', 'Diego Souza', 'Emily Batista',
            'Felipe Lima', 'Gabriela Santos', 'Henrique Alves', 'Isabela Castro', 'Joaquim Mendes',
            'Karen Souza', 'Leonardo Rodrigues', 'Mariana Costa', 'Natália Oliveira', 'Otávio Lima',
            'Patrícia Santos', 'Quintino Almeida', 'Rafaela Ferreira', 'Sérgio Martins', 'Tatiana Ribeiro'
        ])
        
        if i > 0:
            nome = f"{nome} {chr(64 + (i % 26) + 1)}"
        
        cpf = gerar_cpf()
        phone = gerar_telefone()
        email = nome.lower().replace(' ', '.') + f"{i}@email.com"
        renda = float(random.randint(1500, 8000))
        margem = renda * 0.30
        banco = random.choice(bancos)
        empresa = random.choice(empresas)
        status = random.choice(status_opcoes)
        
        try:
            cursor.execute(f"""
                INSERT INTO clientes (nome, email, phone, cpf, status, empresa, renda, margem_consignavel, banco_atual)
                VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
            """, (nome, email, phone, cpf, status, empresa, renda, margem, banco))
            
            clientes_criados.append({
                'id': cursor.lastrowid if not db.is_postgres else None,
                'nome': nome
            })
        except Exception as e:
            print(f"  ⚠️ Erro ao criar cliente {nome}: {e}")
    
    if db.is_postgres:
        cursor.execute("SELECT id, nome FROM clientes ORDER BY id DESC LIMIT " + str(quantidade))
        for row in cursor.fetchall():
            r = dict(row) if hasattr(row, 'keys') else row
            for c in clientes_criados:
                if c['nome'] == r.get('nome'):
                    c['id'] = r.get('id')
                    break
    
    print(f"  ✅ {len(clientes_criados)} clientes criados")
    return clientes_criados

def seed_emprestimos(db, clientes, quantidade=20):
    """Popula tabela de empréstimos"""
    print(f"\n💰 Criando {quantidade} empréstimos...")
    
    status_opcoes = ['aprovado', 'pendente', 'reprovado']
    taxas = [1.29, 1.49, 1.59, 1.69, 1.79, 1.89]
    parcelas_opcoes = [12, 24, 36, 48, 60, 72, 84]
    
    p = db.placeholder()
    
    emprestimos_criados = []
    
    for i in range(quantidade):
        cliente_id = random.choice(clientes)['id']
        valor = float(random.randint(2000, 40000))
        taxa = random.choice(taxas)
        parcelas = random.choice(parcelas_opcoes)
        
        valor_parcela = (valor * (1 + taxa/100 * parcelas/12)) / parcelas
        
        status = random.choice(status_opcoes)
        data_solicitacao = datetime.now() - timedelta(days=random.randint(1, 90))
        
        try:
            cursor.execute(f"""
                INSERT INTO emprestimos 
                (cliente_id, valor_solicitado, taxa_juros_anual, numero_parcelas, status, data_solicitacao)
                VALUES ({p}, {p}, {p}, {p}, {p}, {p})
            """, (cliente_id, valor, taxa, parcelas, status, data_solicitacao.isoformat()))
            
            emp_id = cursor.lastrowid if not db.is_postgres else None
            if db.is_postgres:
                cursor.execute("SELECT lastval()")
                row = cursor.fetchone()
                emp_id = row[0] if row else None
            
            if emp_id:
                emprestimos_criados.append({
                    'id': emp_id,
                    'cliente_id': cliente_id,
                    'valor': valor,
                    'parcelas': parcelas,
                    'valor_parcela': valor_parcela,
                    'taxa': taxa
                })
        except Exception as e:
            print(f"  ⚠️ Erro ao criar empréstimo: {e}")
    
    if db.is_postgres:
        cursor.execute("SELECT id, cliente_id, valor_solicitado, numero_parcelas FROM emprestimos ORDER BY id DESC LIMIT " + str(quantidade))
        resultados = cursor.fetchall()
        for row in resultados:
            r = dict(row) if hasattr(row, 'keys') else row
            for e in emprestimos_criados:
                if e['cliente_id'] == r.get('cliente_id') and e['id'] is None:
                    e['id'] = r.get('id')
                    break
    
    print(f"  ✅ {len(emprestimos_criados)} empréstimos criados")
    return emprestimos_criados

def seed_parcelas(db, emprestimos):
    """Popula tabela de parcelas"""
    print(f"\n📄 Criando parcelas...")
    
    total_parcelas = 0
    p = db.placeholder()
    
    for emp in emprestimos:
        if not emp.get('id'):
            continue
            
        parcelas = emp['parcelas']
        valor_parcela = emp['valor_parcela']
        
        for num in range(1, min(parcelas + 1, 7)):
            data_venc = datetime.now() + timedelta(days=30 * num)
            status = 'paga' if num < 4 else ('pendente' if num < 6 else 'atrasada')
            
            valor_juros = valor_parcela * 0.15
            data_pagamento = None
            if status == 'paga':
                data_pagamento = (data_venc - timedelta(days=random.randint(0, 5))).isoformat()
            
            try:
                cursor.execute(f"""
                    INSERT INTO parcelas 
                    (emprestimo_id, numero_parcela, valor_parcela, valor_juros, data_vencimento, data_pagamento, status)
                    VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})
                """, (emp['id'], num, valor_parcela, valor_juros, data_venc.isoformat(), data_pagamento, status))
                
                total_parcelas += 1
            except Exception as e:
                print(f"  ⚠️ Erro ao criar parcela: {e}")
    
    print(f"  ✅ {total_parcelas} parcelas criadas")
    return total_parcelas

def seed_campanhas(db):
    """Popula tabela de campanhas"""
    print(f"\n📧 Criando campanhas...")
    
    campanhas = [
        ('Campanha Aposentados INSS 2024', 'Campanha direcionada para aposentados do INSS', 'admin@pariscred.com'),
        ('Campanha Servidores Públicos', 'Campanha para servidores públicos estaduais', 'admin@pariscred.com'),
        ('Campanha Portabilidade', 'Campanha de portabilidade de consignado', 'admin@pariscred.com'),
        ('Campanha Verano 2024', 'Promoção de verão para novos clientes', 'vendedor@pariscred.com'),
        ('Campanha-whatsapp-inicio', 'Primeiro contato via WhatsApp', 'vendedor@pariscred.com')
    ]
    
    p = db.placeholder()
    
    for nome, desc, criador in campanhas:
        try:
            cursor.execute(f"""
                INSERT INTO campanhas (nome, descricao, status, criador, mensagem, beneficiarios_json, botoes_json, instancias_json, total_enviados)
                VALUES ({p}, {p}, 'rascunho', {p}, 'Olá! Temos uma proposta especial para você!', '[]', '[]', '[]', 0)
            """, (nome, desc, criador))
        except Exception as e:
            print(f"  ⚠️ Erro ao criar campanha: {e}")
    
    print(f"  ✅ {len(campanhas)} campanhas criadas")

def seed_usuarios(db):
    """Cria usuários de teste se não existirem"""
    print(f"\n👤 Verificando usuários...")
    
    import bcrypt
    
    p = db.placeholder()
    cursor.execute(f"SELECT COUNT(*) as total FROM usuarios")
    row = cursor.fetchone()
    total = row['total'] if isinstance(row, dict) else row[0]
    
    if total == 0:
        usuarios = [
            ('admin@pariscred.com', 'Administrador', 'admin'),
            ('vendedor@pariscred.com', 'Vendedor Padrão', 'vendedor'),
            ('gerente@pariscred.com', 'Gerente de Vendas', 'gerente')
        ]
        
        for email, nome, role in usuarios:
            senha = 'Admin@2025' if role == 'admin' else 'Vendedor@123'
            senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
            
            try:
                cursor.execute(f"""
                    INSERT INTO usuarios (email, nome, senha_hash, role)
                    VALUES ({p}, {p}, {p}, {p})
                """, (email, nome, senha_hash, role))
                print(f"  ✅ Usuário criado: {email}")
            except Exception as e:
                print(f"  ⚠️ Erro ao criar usuário {email}: {e}")
    else:
        print(f"  ✅ {total} usuários já existem")

def main():
    print("=" * 60)
    print("🌿 SEED DO BANCO DE DADOS - ParisCred Intelligence")
    print("=" * 60)
    
    db = Database()
    global cursor
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        seed_usuarios(db)
        
        clientes = seed_clientes(db, 50)
        
        seed_emprestimos(db, clientes, 20)
        
        seed_parcelas(db, [
            {'id': 1, 'cliente_id': 1, 'valor': 10000, 'parcelas': 48, 'valor_parcela': 280, 'taxa': 1.69}
        ])
        
        seed_campanhas(db)
        
        conn.commit()
    
    print("\n" + "=" * 60)
    print("✅ SEED CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("\n📋 Credenciais de acesso:")
    print("   Admin: admin@pariscred.com / Admin@2025")
    print("   Vendedor: vendedor@pariscred.com / Vendedor@123")
    print("   Gerente: gerente@pariscred.com / Vendedor@123")
    print("\n💡 Acesse http://localhost:5000 para testar!")

if __name__ == "__main__":
    main()
