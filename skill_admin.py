"""
Skill: Admin Reports
Dashboards, KPIs, relatórios, analytics
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database import Database


class AdminReportsDB:
    """Gera relatórios e análises para admin"""
    
    @staticmethod
    def kpis_gerais(dias: int = 30) -> Dict:
        """Retorna KPIs gerais do período"""
        
        db = Database()
        data_inicio = (datetime.now() - timedelta(days=dias)).isoformat()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Volume de clientes
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE ativo = 1")
            total_clientes = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM clientes 
                WHERE data_criacao >= ? AND ativo = 1
            """, (data_inicio,))
            clientes_novos = cursor.fetchone()[0]
            
            # Volume financeiro
            cursor.execute("""
                SELECT COALESCE(SUM(valor_solicitado), 0)
                FROM emprestimos WHERE status = 'aprovado' AND ativo = 1
            """)
            total_emp = cursor.fetchone()[0]
            
            # Juros arrecadado
            cursor.execute("""
                SELECT COALESCE(SUM(valor_juros), 0)
                FROM parcelas WHERE status = 'paga' AND ativo = 1
            """)
            juros_total = cursor.fetchone()[0]
            
            # Performance
            cursor.execute("""
                SELECT COUNT(*), SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END)
                FROM emprestimos WHERE data_solicitacao >= ?
            """, (data_inicio,))
            row = cursor.fetchone()
            total_propostas = row[0] or 0
            aprovadas = row[1] or 0
            
            taxa_aprovacao = (aprovadas / total_propostas * 100) if total_propostas > 0 else 0
            
            # Risco
            cursor.execute("""
                SELECT COUNT(*) FROM parcelas 
                WHERE status = 'pendente' AND data_vencimento < datetime('now') AND ativo = 1
            """)
            atrasadas = cursor.fetchone()[0]
            
            return {
                "periodo": f"Últimos {dias} dias",
                "volume": {
                    "total_clientes": total_clientes,
                    "clientes_novos": clientes_novos,
                    "taxa_crescimento_%": round((clientes_novos / total_clientes * 100) if total_clientes > 0 else 0, 2)
                },
                "financeiro": {
                    "total_emprestado": float(total_emp),
                    "juros_arrecadado": float(juros_total),
                    "ticket_medio": float(total_emp / aprovadas) if aprovadas > 0 else 0
                },
                "performance": {
                    "propostas_enviadas": total_propostas,
                    "aprovadas": aprovadas,
                    "taxa_aprovacao_%": round(taxa_aprovacao, 2)
                },
                "risco": {
                    "parcelas_atrasadas": atrasadas,
                    "taxa_inadimplencia_%": round((atrasadas / (aprovadas * 60)) * 100 if aprovadas else 0, 2)
                }
            }
    
    @staticmethod
    def relatorio_clientes_por_status() -> Dict:
        """Relatório de distribuição de clientes"""
        
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, COUNT(*) as total, 
                       COALESCE(SUM(margem_consignavel), 0) as margem_total
                FROM clientes WHERE ativo = 1
                GROUP BY status
                ORDER BY total DESC
            """)
            
            resultado = {
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }
            
            for row in cursor.fetchall():
                resultado["data"][row['status']] = {
                    "total": row['total'],
                    "margem_total": float(row['margem_total'])
                }
            
            return resultado
    
    @staticmethod
    def ranking_maiores_clientes(limite: int = 10) -> List[Dict]:
        """Top clientes por renda"""
        
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome, email, phone, renda, margem_consignavel, status
                FROM clientes WHERE ativo = 1 AND renda IS NOT NULL
                ORDER BY renda DESC
                LIMIT ?
            """, (limite,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def analise_lucratividade() -> Dict:
        """Análise de lucratividade por produto/cliente"""
        
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Juros vs Custos
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_emprestimos,
                    COALESCE(SUM(valor_solicitado), 0) as valor_total,
                    COALESCE(SUM(
                        (SELECT COALESCE(SUM(valor_juros), 0) FROM parcelas 
                         WHERE emprestimos.id = parcelas.emprestimo_id AND status = 'paga')
                    ), 0) as juros_total
                FROM emprestimos WHERE status = 'pago'
            """)
            
            row = cursor.fetchone()
            
            if row:
                total_emp = row[0] or 0
                valor_total = float(row[1] or 0)
                juros_total = float(row[2] or 0)
                
                lucro_bruto = juros_total
                margem_bruta = (lucro_bruto / valor_total * 100) if valor_total > 0 else 0
                
                return {
                    "total_emprestimos": total_emp,
                    "valor_total": valor_total,
                    "juros_arrecadado": juros_total,
                    "lucro_bruto": lucro_bruto,
                    "margem_bruta_%": round(margem_bruta, 2)
                }
            
            return {"erro": "Sem dados"}
    
    @staticmethod
    def ultimas_transacoes(limite: int = 20) -> List[Dict]:
        """Últimas operações do sistema"""
        
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    e.id,
                    c.nome,
                    e.valor_solicitado,
                    e.status,
                    e.data_solicitacao
                FROM emprestimos e
                JOIN clientes c ON e.cliente_id = c.id
                WHERE e.ativo = 1
                ORDER BY e.data_solicitacao DESC
                LIMIT ?
            """, (limite,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def relatorio_por_periodo(data_inicio: str, data_fim: str) -> Dict:
        """Relatório completo de um período"""
        
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total do período
            cursor.execute("""
                SELECT 
                    COUNT(*) as propostas,
                    SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) as aprovadas,
                    COALESCE(SUM(valor_solicitado), 0) as valor_total,
                    COALESCE(SUM(
                        (SELECT COALESCE(SUM(valor_juros), 0) FROM parcelas 
                         WHERE emprestimos.id = parcelas.emprestimo_id)
                    ), 0) as juros
                FROM emprestimos 
                WHERE data_solicitacao BETWEEN ? AND ? AND ativo = 1
            """, (data_inicio, data_fim))
            
            row = cursor.fetchone()
            
            return {
                "periodo": {
                    "inicio": data_inicio,
                    "fim": data_fim
                },
                "resumo": {
                    "propostas": row[0] or 0,
                    "aprovadas": row[1] or 0,
                    "valor_total": float(row[2] or 0),
                    "juros_total": float(row[3] or 0),
                    "taxa_aprovacao_%": round((row[1] / row[0] * 100) if row[0] else 0, 2)
                }
            }
    
    @staticmethod
    def alertas_sistema() -> List[Dict]:
        """Alertas para admin"""
        
        alertas = []
        db = Database()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Taxa de inadimplência alta
            cursor.execute("""
                SELECT COUNT(*) FROM parcelas 
                WHERE status = 'pendente' AND data_vencimento < datetime('now')
            """)
            atrasadas = cursor.fetchone()[0]
            
            if atrasadas > 10:
                alertas.append({
                    "tipo": "ALERTA",
                    "severidade": "alta",
                    "mensagem": f"{atrasadas} parcelas atrasadas",
                    "acao": "Cobrar atrasados"
                })
            
            # 2. Pouco movimento
            cursor.execute("""
                SELECT COUNT(*) FROM emprestimos 
                WHERE data_solicitacao >= datetime('now', '-7 days')
            """)
            recentes = cursor.fetchone()[0]
            
            if recentes < 5:
                alertas.append({
                    "tipo": "AVISO",
                    "severidade": "media",
                    "mensagem": f"Apenas {recentes} empréstimos nos últimos 7 dias",
                    "acao": "Ativar campanhas de vendas"
                })
            
            # 3. Clientes sem movimento
            cursor.execute("""
                SELECT COUNT(*) FROM clientes 
                WHERE status = 'lead' AND 
                data_criacao < datetime('now', '-30 days')
            """)
            leads_antigos = cursor.fetchone()[0]
            
            if leads_antigos > 20:
                alertas.append({
                    "tipo": "AVISO",
                    "severidade": "baixa",
                    "mensagem": f"{leads_antigos} leads inativos há 30+ dias",
                    "acao": "Fazer follow-up"
                })
        
        return alertas
    
    @staticmethod
    def exportar_relatorio_completo() -> Dict:
        """Exporta relatório completo em JSON"""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "kpis": AdminReportsDB.kpis_gerais(30),
            "clientes": AdminReportsDB.relatorio_clientes_por_status(),
            "lucratividade": AdminReportsDB.analise_lucratividade(),
            "top_clientes": AdminReportsDB.ranking_maiores_clientes(10),
            "ultimas_transacoes": AdminReportsDB.ultimas_transacoes(20),
            "alertas": AdminReportsDB.alertas_sistema()
        }
