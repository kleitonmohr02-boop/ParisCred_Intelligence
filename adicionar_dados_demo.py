# -*- coding: utf-8 -*-
"""
Script para adicionar dados de demonstração ao sistema
Executar: python adicionar_dados_demo.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from skill_crm import ClientesDB
from database import Database

def adicionar_dados_demo():
    print("="*50)
    print("  ADICIONANDO DADOS DE DEMONSTRAÇÃO")
    print("="*50)
    
    # Dados de clientes fake para crédito consignado
    clientes_demo = [
        # Novo Lead (5 clientes)
        {"nome": "Carlos Alberto Silva", "phone": "48999001101", "cpf": "12345678901", "email": "carlos.silva@email.com", "renda": 2500, "status": "Novo Lead"},
        {"nome": "Maria Aparecida Santos", "phone": "48999001102", "cpf": "12345678902", "email": "maria.santos@email.com", "renda": 3200, "status": "Novo Lead"},
        {"nome": "José Roberto Oliveira", "phone": "48999001103", "cpf": "12345678903", "email": "jose.oliveira@email.com", "renda": 1800, "status": "Novo Lead"},
        {"nome": "Ana Paula Ferreira", "phone": "48999001104", "cpf": "12345678904", "email": "ana.ferreira@email.com", "renda": 4100, "status": "Novo Lead"},
        {"nome": "Pedro Henrique Costa", "phone": "48999001105", "cpf": "12345678905", "email": "pedro.costa@email.com", "renda": 2200, "status": "Novo Lead"},
        
        # Em Negociação (5 clientes)
        {"nome": "Juliana Martins Dias", "phone": "48999001106", "cpf": "12345678906", "email": "juliana.dias@email.com", "renda": 2800, "status": "Em Negociação"},
        {"nome": "Roberto Carlos Souza", "phone": "48999001107", "cpf": "12345678907", "email": "roberto.souza@email.com", "renda": 3500, "status": "Em Negociação"},
        {"nome": "Fernanda Lima Rodrigues", "phone": "48999001108", "cpf": "12345678908", "email": "fernanda.rodrigues@email.com", "renda": 2900, "status": "Em Negociação"},
        {"nome": "Marcos Vinícius Almeida", "phone": "48999001109", "cpf": "12345678909", "email": "marcos.almeida@email.com", "renda": 3100, "status": "Em Negociação"},
        {"nome": "Camila Cristina Pereira", "phone": "48999001110", "cpf": "12345678910", "email": "camila.pereira@email.com", "renda": 2600, "status": "Em Negociação"},
        
        # Pendente (3 clientes)
        {"nome": "Ricardo Teixeira Barbosa", "phone": "48999001111", "cpf": "12345678911", "email": "ricardo.barbosa@email.com", "renda": 3800, "status": "Pendente"},
        {"nome": "Patrícia Andrade Gomes", "phone": "48999001112", "cpf": "12345678912", "email": "patricia.gomes@email.com", "renda": 4200, "status": "Pendente"},
        {"nome": "Bruno Rodrigues Lima", "phone": "48999001113", "cpf": "12345678913", "email": "bruno.lima@email.com", "renda": 2400, "status": "Pendente"},
        
        # Finalizado (4 clientes)
        {"nome": "Sandra Maria Cardoso", "phone": "48999001114", "cpf": "12345678914", "email": "sandra.cardoso@email.com", "renda": 3300, "status": "Finalizado"},
        {"nome": "Leonardo Mendes Costa", "phone": "48999001115", "cpf": "12345678915", "email": "leonardo.costa@email.com", "renda": 2700, "status": "Finalizado"},
        {"nome": "Renata Tavares Borges", "phone": "48999001116", "cpf": "12345678916", "email": "renata.borges@email.com", "renda": 4000, "status": "Finalizado"},
        {"nome": "Thiago Fernandes Alves", "phone": "48999001117", "cpf": "12345678917", "email": "thiago.alves@email.com", "renda": 3000, "status": "Finalizado"},
    ]
    
    total_adicionados = 0
    
    print(f"\nAdicionando {len(clientes_demo)} clientes...\n")
    
    for cliente in clientes_demo:
        try:
            resultado = ClientesDB.criar_cliente(
                nome=cliente["nome"],
                phone=cliente["phone"],
                cpf=cliente["cpf"],
                email=cliente["email"],
                renda=cliente["renda"]
            )
            
            if "sucesso" in resultado:
                # Atualizar status
                ClientesDB.atualizar_status(resultado["cliente_id"], cliente["status"])
                print(f"  [OK] {cliente['nome']} - {cliente['status']}")
                total_adicionados += 1
            else:
                print(f"  [ERRO] {cliente['nome']}: {resultado.get('erro', 'Erro desconhecido')}")
                
        except Exception as e:
            print(f"  [ERRO] {cliente['nome']}: {str(e)}")
    
    print("\n" + "="*50)
    print(f"  TOTAL ADICIONADOS: {total_adicionados}/{len(clientes_demo)}")
    print("="*50)
    
    # Mostrar estatísticas
    relatorio = ClientesDB.relatorio_por_status()
    print("\n📊 ESTATÍSTICAS POR STATUS:")
    for status, dados in relatorio.items():
        print(f"  {status}: {dados['total']} clientes")
    
    return total_adicionados

if __name__ == "__main__":
    adicionar_dados_demo()
