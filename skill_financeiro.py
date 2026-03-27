"""
Skill: Financeiro System
Cálculos de consignado, simulações, riscos, relatórios
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from database import Database
from decimal import Decimal


class FinanceiroDB:
    """Gerencia dados financeiros"""
    
    @staticmethod
    def criar_tabelas():
        """Cria tabelas de financeiro"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de empréstimos
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS emprestimos (
                    id {db.pk_auto()},
                    cliente_id INTEGER NOT NULL,
                    valor_solicitado DECIMAL(10,2),
                    taxa_juros_anual DECIMAL(5,2),
                    numero_parcelas INTEGER,
                    status TEXT DEFAULT 'pendente',
                    data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_aprovacao TIMESTAMP,
                    data_vencimento TIMESTAMP,
                    ativo BOOLEAN DEFAULT { db.bool_def(True) },
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )
            """)
            
            # Tabela de parcelas
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS parcelas (
                    id {db.pk_auto()},
                    emprestimo_id INTEGER NOT NULL,
                    numero_parcela INTEGER,
                    valor_parcela DECIMAL(10,2),
                    valor_juros DECIMAL(10,2),
                    data_vencimento TIMESTAMP,
                    data_pagamento TIMESTAMP,
                    status TEXT DEFAULT 'pendente',
                    ativo BOOLEAN DEFAULT { db.bool_def(True) },
                    FOREIGN KEY (emprestimo_id) REFERENCES emprestimos(id)
                )
            """)
            
            # Tabela de métricas financeiras
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS metricas_financeiras (
                    id {db.pk_auto()},
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_emprestimos DECIMAL(10,2),
                    total_juros_arrecadado DECIMAL(10,2),
                    emprestimos_ativos INTEGER,
                    emprestimos_atrasados INTEGER
                )
            """)
            
            conn.commit()
    
    @staticmethod
    def calcular_consignado(renda_liquida: float, percentual: int = 30) -> Dict:
        """Calcula margem de consignado"""
        if renda_liquida < 1000:
            return {"erro": "Renda mínima é R$ 1.000"}
        
        margem = renda_liquida * (percentual / 100)
        
        return {
            "renda_liquida": renda_liquida,
            "percentual": percentual,
            "margem_consignavel": round(margem, 2),
            "pode_emprestar": round(margem, 2)
        }
    
    @staticmethod
    def simular_emprestimo(valor: float, taxa_anual: float, parcelas: int) -> Dict:
        """Simula empréstimo com cronograma completo"""
        
        # Validações
        if valor < 500:
            return {"erro": "Valor mínimo é R$ 500"}
        if valor > 100000:
            return {"erro": "Valor máximo é R$ 100.000"}
        if parcelas < 12 or parcelas > 84:
            return {"erro": "Parcelas deve estar entre 12 e 84"}
        
        taxa_mensal = taxa_anual / 100 / 12
        
        # Cálculo de parcela (Price)
        if taxa_mensal == 0:
            parcela_mensal = valor / parcelas
        else:
            parcela_mensal = valor * (taxa_mensal * (1 + taxa_mensal)**parcelas) / \
                           ((1 + taxa_mensal)**parcelas - 1)
        
        # Gerar cronograma
        cronograma = []
        saldo = valor
        juros_total = 0
        
        for i in range(1, parcelas + 1):
            juros = saldo * taxa_mensal
            amortizacao = parcela_mensal - juros
            saldo -= amortizacao
            juros_total += juros
            
            data_vencimento = datetime.now() + timedelta(days=30*i)
            
            cronograma.append({
                "parcela": i,
                "valor_parcela": round(parcela_mensal, 2),
                "amortizacao": round(amortizacao, 2),
                "juros": round(juros, 2),
                "saldo_devedor": round(max(0, saldo), 2),
                "data_vencimento": data_vencimento.strftime("%Y-%m-%d")
            })
        
        return {
            "simulacao": {
                "valor_original": valor,
                "taxa_anual": taxa_anual,
                "numero_parcelas": parcelas,
                "valor_parcela": round(parcela_mensal, 2),
                "valor_total_pago": round(parcela_mensal * parcelas, 2),
                "juros_total": round(juros_total, 2),
                "custo_efetivo": round((juros_total / valor) * 100, 2)
            },
            "cronograma": cronograma
        }
    
    @staticmethod
    def analisar_risco(cliente_id: int) -> Dict:
        """Analisa risco do cliente para aprovação"""
        from skill_crm import ClientesDB
        
        cliente = ClientesDB.obter_cliente(cliente_id)
        if not cliente:
            return {"erro": "Cliente não encontrado"}
        
        # Score de risco (0-100)
        score = 0
        
        # 1. Renda
        if cliente['renda'] and cliente['renda'] >= 5000:
            score += 25
        elif cliente['renda'] and cliente['renda'] >= 3000:
            score += 15
        elif cliente['renda'] and cliente['renda'] >= 1000:
            score += 5
        
        # 2. Histórico - buscar empréstimos passados
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN status = 'pago' THEN 1 ELSE 0 END) as pagos
                FROM emprestimos WHERE cliente_id = {db.placeholder()} AND ativo = 1
            """, (cliente_id,))
            row = dict(cursor.fetchone())
            
            total_emp = row['total'] or 0
            pagos = row['pagos'] or 0
            
            if total_emp > 0:
                taxa_quitacao = (pagos / total_emp) * 100
                score += int(taxa_quitacao / 5)  # até 20 pontos
        
        # 3. Status
        status_scores = {
            'ativo': 20,
            'contatado': 15,
            'lead': 5,
            'inativo': 0,
            'bloqueado': -30
        }
        score += status_scores.get(cliente['status'], 0)
        
        # 4. Categoria
        if score >= 70:
            categoria = "BAIXO RISCO"
            recomendacao = "Aprovar com limite total"
        elif score >= 45:
            categoria = "RISCO MÉDIO"
            recomendacao = "Aprovar com limite 70%"
        else:
            categoria = "ALTO RISCO"
            recomendacao = "Análise manual obrigatória"
        
        return {
            "cliente_id": cliente_id,
            "score": score,
            "categoria_risco": categoria,
            "recomendacao": recomendacao,
            "renda": cliente['renda'],
            "margem_consignavel": cliente['margem_consignavel'],
            "status_cliente": cliente['status']
        }
    
    @staticmethod
    def criar_emprestimo(cliente_id: int, valor: float, taxa_anual: float, parcelas: int) -> Dict:
        """Cria novo empréstimo e gera cronograma"""
        
        # Análise de risco
        risco = FinanceiroDB.analisar_risco(cliente_id)
        if "erro" in risco:
            return risco
        
        # Simular
        simulacao = FinanceiroDB.simular_emprestimo(valor, taxa_anual, parcelas)
        if "erro" in simulacao:
            return simulacao
        
        # Salvar no banco
        db = Database()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                data_vencimento = datetime.now() + timedelta(days=30*parcelas)
                p = db.placeholder()
                cursor.execute(f"""
                    INSERT INTO emprestimos 
                    (cliente_id, valor_solicitado, taxa_juros_anual, numero_parcelas, status)
                    VALUES ({p}, {p}, {p}, {p}, 'aprovado')
                    {"RETURNING id" if db.is_postgres else ""}
                """, (cliente_id, valor, taxa_anual, parcelas))
                
                if db.is_postgres:
                    emprestimo_id = cursor.fetchone()['id']
                else:
                    emprestimo_id = cursor.lastrowid
                
                # Criar parcelas
                for parc in simulacao['cronograma']:
                    cursor.execute(f"""
                        INSERT INTO parcelas 
                        (emprestimo_id, numero_parcela, valor_parcela, valor_juros, data_vencimento)
                        VALUES ({p}, {p}, {p}, {p}, {p})
                    """, (
                        emprestimo_id,
                        parc['parcela'],
                        parc['valor_parcela'],
                        parc['juros'],
                        parc['data_vencimento']
                    ))
                
                conn.commit()
                
                return {
                    "sucesso": True,
                    "emprestimo_id": emprestimo_id,
                    "cliente_id": cliente_id,
                    "categoria_risco": risco['categoria_risco'],
                    "valor": valor,
                    "parcelas": parcelas,
                    "valor_parcela": simulacao['simulacao']['valor_parcela']
                }
        
        except Exception as e:
            return {"erro": f"Erro ao criar empréstimo: {str(e)}"}
    
    @staticmethod
    def obter_kpis() -> Dict:
        """KPIs financeiros gerais"""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total emprestado
            cursor.execute(f"""
                SELECT COALESCE(SUM(valor_solicitado), 0) as total
                FROM emprestimos WHERE status = 'aprovado' AND ativo = {db.bool_def(True)}
            """)
            total_emp = cursor.fetchone()['total']
            
            # Total de juros arrecadado
            cursor.execute(f"""
                SELECT COALESCE(SUM(valor_juros), 0) as total
                FROM parcelas WHERE status = 'paga' AND ativo = {db.bool_def(True)}
            """)
            total_juros = cursor.fetchone()['total']
            
            # Empréstimos ativos
            cursor.execute(f"""
                SELECT COUNT(*) as total FROM emprestimos WHERE status = 'aprovado' AND ativo = {db.bool_def(True)}
            """)
            emp_ativos = cursor.fetchone()['total']
            
            # Parcelas atrasadas
            data_agora = "CURRENT_TIMESTAMP" if db.is_postgres else "datetime('now')"
            cursor.execute(f"""
                SELECT COUNT(*) as total FROM parcelas 
                WHERE status = 'pendente' AND data_vencimento < {data_agora} AND ativo = {db.bool_def(True)}
            """)
            atrasadas = cursor.fetchone()['total']
        
        return {
            "total_emprestimos": float(total_emp),
            "total_juros": float(total_juros),
            "emprestimos_ativos": emp_ativos,
            "parcelas_atrasadas": atrasadas,
            "taxa_inadimplencia": round((atrasadas / (emp_ativos * 60)) * 100, 2) if emp_ativos else 0
        }


# Inicializar tabelas
FinanceiroDB.criar_tabelas()
