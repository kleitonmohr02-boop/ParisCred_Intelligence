"""
Skill: CRM Management
Gestão de clientes, leads, relacionamentos
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from database import Database
import json


class ClientesDB:
    """Gerencia clientes no banco de dados"""
    
    @staticmethod
    def criar_tabelas():
        """Cria tabelas de CRM se não existirem"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de clientes
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS clientes (
                    id {db.pk_auto()},
                    nome TEXT NOT NULL,
                    email TEXT,
                    phone TEXT UNIQUE NOT NULL,
                    cpf TEXT UNIQUE,
                    status TEXT DEFAULT 'lead',
                    empresa TEXT,
                    cargo TEXT,
                    renda DECIMAL(10,2),
                    margem_consignavel DECIMAL(10,2),
                    custom_fields JSON,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ativo BOOLEAN DEFAULT { db.bool_def(True) }
                )
            """)
            
            # Tabela de interações
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS interacoes (
                    id {db.pk_auto()},
                    cliente_id INTEGER NOT NULL,
                    tipo TEXT,
                    descricao TEXT,
                    resultado TEXT,
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ativo BOOLEAN DEFAULT { db.bool_def(True) },
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )
            """)
            
            conn.commit()
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida CPF (simplificado)"""
        cpf_clean = cpf.replace('.', '').replace('-', '')
        return len(cpf_clean) == 11 and cpf_clean.isdigit()
    
    @staticmethod
    def calcular_margem(renda: float, percentual: int = 30) -> float:
        """Calcula margem consignável"""
        if renda < 1000:
            return 0
        return renda * (percentual / 100)
    
    @staticmethod
    def criar_cliente(nome: str, phone: str, cpf: str = None, empresa: str = None, 
                     cargo: str = None, renda: float = None, email: str = None) -> Dict:
        """Cria novo cliente"""
        
        # Validações
        if not phone:
            return {"erro": "Telefone é obrigatório"}
        
        if cpf and not ClientesDB.validar_cpf(cpf):
            return {"erro": "CPF inválido"}
        
        try:
            db = Database()
            margem = ClientesDB.calcular_margem(renda) if renda else 0
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                p = db.placeholder()
                cursor.execute(f"""
                    INSERT INTO clientes (nome, email, phone, cpf, empresa, cargo, renda, margem_consignavel, status)
                    VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, 'lead')
                """, (nome, email, phone, cpf, empresa, cargo, renda, margem))
                
                cliente_id = cursor.lastrowid
                conn.commit()
                
                return {
                    "sucesso": True,
                    "cliente_id": cliente_id,
                    "nome": nome,
                    "margem_consignavel": margem
                }
        
        except sqlite3.IntegrityError as e:
            return {"erro": f"Erro ao criar cliente: {str(e)}"}
    
    @staticmethod
    def obter_cliente(cliente_id: int) -> Optional[Dict]:
        """Obtém dados do cliente"""
        db = Database()
        ativo_val = db.bool_def(True)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM clientes WHERE id = {db.placeholder()} AND ativo = {ativo_val}", (cliente_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def listar_clientes(status: str = None, limite: int = 50) -> List[Dict]:
        """Lista clientes com filtro opcional"""
        db = Database()
        ativo_val = db.bool_def(True)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute(f"""
                    SELECT * FROM clientes 
                    WHERE status = {db.placeholder()} AND ativo = {ativo_val}
                    LIMIT {db.placeholder()}
                """, (status, limite))
            else:
                cursor.execute(f"SELECT * FROM clientes WHERE ativo = {ativo_val} LIMIT {db.placeholder()}", (limite,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def atualizar_status(cliente_id: int, novo_status: str) -> Dict:
        """Atualiza status do cliente"""
        status_validos = ['Novo Lead', 'Em Negociação', 'Pendente', 'Finalizado']
        
        if novo_status not in status_validos:
            return {"erro": f"Status deve ser um de: {status_validos}"}
        
        db = Database()
        ativo_val = db.bool_def(True)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            p = db.placeholder()
            cursor.execute(f"""
                UPDATE clientes SET status = {p} WHERE id = {p} AND ativo = {ativo_val}
            """, (novo_status, cliente_id))
            conn.commit()
        
        return {"sucesso": True, "novo_status": novo_status}
    
    @staticmethod
    def registrar_interacao(cliente_id: int, tipo: str, descricao: str, resultado: str = None) -> Dict:
        """Registra interação com cliente"""
        
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            p = db.placeholder()
            cursor.execute(f"""
                INSERT INTO interacoes (cliente_id, tipo, descricao, resultado)
                VALUES ({p}, {p}, {p}, {p})
            """, (cliente_id, tipo, descricao, resultado))
            
            interacao_id = cursor.lastrowid if not db.is_postgres else 0 # No postgres o cursor.lastrowid pode variar
            conn.commit()
        
        # Atualizar status para 'contatado' se era lead
        cliente = ClientesDB.obter_cliente(cliente_id)
        if cliente and cliente['status'] == 'lead':
            ClientesDB.atualizar_status(cliente_id, 'contatado')
        
        return {"sucesso": True, "interacao_id": interacao_id}
    
    @staticmethod
    def obter_historico(cliente_id: int, limite: int = 20) -> List[Dict]:
        """Obtém histórico de interações"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            p = db.placeholder()
            cursor.execute(f"""
                SELECT descricao, resultado, data FROM interacoes 
                WHERE cliente_id = {p} AND ativo = {db.bool_def(True)} 
                ORDER BY data DESC
                LIMIT {p}
            """, (cliente_id, limite))
            
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def relatorio_por_status() -> Dict:
        """Relatório de clientes por status"""
        db = Database()
        ativo_val = db.bool_def(True)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT status, COUNT(*) as total, 
                       COALESCE(SUM(margem_consignavel), 0) as margem_total
                FROM clientes
                WHERE ativo = {ativo_val}
                GROUP BY status
            """)
            
            resultado = {}
            for row in cursor.fetchall():
                resultado[row['status']] = {
                    "total": row['total'],
                    "margem_total": row['margem_total']
                }
            
            return resultado
    
    @staticmethod
    def buscar_por_phone(phone: str) -> Optional[Dict]:
        """Busca cliente por telefone"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM clientes WHERE phone = {db.placeholder()} AND ativo = {db.bool_def(True)}
            """, (phone,))
            row = cursor.fetchone()
            return dict(row) if row else None


# Inicializar tabelas ao importar
ClientesDB.criar_tabelas()
