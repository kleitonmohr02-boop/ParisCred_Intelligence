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
            
            cursor.execute(f"SELECT COUNT(*) as total FROM clientes WHERE ativo = {db.bool_def(True)}")
            row = cursor.fetchone()
            total_clientes = row['total'] if row else 0
            
            p = db.placeholder()
            cursor.execute(f"""
                SELECT COUNT(*) as total FROM clientes 
                WHERE data_criacao >= {p} AND ativo = {db.bool_def(True)}
            """, (data_inicio,))
            row_novos = cursor.fetchone()
            clientes_novos = row_novos['total'] if row_novos else 0
            
            cursor.execute(f"""
                SELECT SUM(valor_solicitado) as total 
                FROM emprestimos WHERE data_solicitacao >= {p}
            """, (data_inicio,))
            row_emp = cursor.fetchone()
            total_emp = float(row_emp['total']) if row_emp and row_emp['total'] else 0
            
            cursor.execute(f"""
                SELECT COALESCE(SUM(valor_juros), 0) as total
                FROM parcelas WHERE status = 'paga' AND ativo = {db.bool_def(True)}
            """)
            row = cursor.fetchone()
            juros_total = float(row['total']) if row and row['total'] else 0
            
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total, 
                    SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) as aprovadas
                FROM emprestimos WHERE data_solicitacao >= {p}
            """, (data_inicio,))
            row_perf = cursor.fetchone()
            total_propostas = row_perf['total'] or 0
            aprovadas = row_perf['aprovadas'] or 0
            
            taxa_aprovacao = (aprovadas / total_propostas * 100) if total_propostas > 0 else 0
            
            data_agora = "CURRENT_TIMESTAMP" if db.is_postgres else "datetime('now')"
            cursor.execute(f"""
                SELECT COUNT(*) as total FROM parcelas 
                WHERE status = 'pendente' AND data_vencimento < {data_agora} AND ativo = {db.bool_def(True)}
            """)
            row = cursor.fetchone()
            atrasadas = row['total'] if row else 0
            
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
            ativo_val = db.bool_def(True)
            cursor.execute(f"""
                SELECT status, COUNT(*) as total, 
                       COALESCE(SUM(margem_consignavel), 0) as margem_total
                FROM clientes WHERE ativo = {ativo_val}
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
        ativo_val = db.bool_def(True)
        p = db.placeholder()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT id, nome, email, phone, renda, margem_consignavel, status
                FROM clientes WHERE ativo = {ativo_val} AND renda IS NOT NULL
                ORDER BY renda DESC
                LIMIT {p}
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
            
            row_lucro = cursor.fetchone()
            
            if row_lucro:
                total_emp = row_lucro['total_emprestimos'] or 0
                valor_total = float(row_lucro['valor_total'] or 0)
                juros_total = float(row_lucro['juros_total'] or 0)
                
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
            p = db.placeholder()
            cursor.execute(f"""
                SELECT * FROM clientes 
                WHERE ativo = {db.bool_def(True)}
                ORDER BY data_criacao DESC 
                LIMIT {p}
            """, (limite,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def relatorio_por_periodo(data_inicio: str, data_fim: str) -> Dict:
        """Relatório completo de um período"""
        
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total do período
            p = db.placeholder()
            cursor.execute(f"""
                SELECT data_solicitacao, valor_solicitado 
                FROM emprestimos 
                WHERE data_solicitacao BETWEEN {p} AND {p} AND ativo = {db.bool_def(True)}
            """, (data_inicio, data_fim))
            
            resumo_row = cursor.fetchone()
            
            if not resumo_row:
                return {"erro": "Sem dados"}

            return {
                "periodo": {
                    "inicio": data_inicio,
                    "fim": data_fim
                },
                "resumo": {
                    "propostas": resumo_row.get('propostas', 0),
                    "aprovadas": resumo_row.get('aprovadas', 0),
                    "valor_total": float(resumo_row.get('valor_total', 0)),
                    "juros_total": float(resumo_row.get('juros_total', 0)),
                    "taxa_aprovacao_%": round((resumo_row.get('aprovadas', 0) / resumo_row.get('propostas', 1) * 100), 2)
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
            data_agora = "CURRENT_TIMESTAMP" if db.is_postgres else "datetime('now')"
            cursor.execute(f"""
                SELECT COUNT(*) as total FROM parcelas 
                WHERE status = 'pendente' AND data_vencimento < {data_agora}
            """)
            row_atrasadas = cursor.fetchone()
            atrasadas = row_atrasadas['total'] if row_atrasadas else 0
            
            if atrasadas > 10:
                alertas.append({
                    "tipo": "ALERTA",
                    "severidade": "alta",
                    "mensagem": f"{atrasadas} parcelas atrasadas",
                    "acao": "Cobrar atrasados"
                })
            
            # 2. Pouco movimento
            query_recentes = "SELECT COUNT(*) as total FROM emprestimos WHERE data_solicitacao >= CURRENT_TIMESTAMP - INTERVAL '7 days'" if db.is_postgres else "SELECT COUNT(*) as total FROM emprestimos WHERE data_solicitacao >= datetime('now', '-7 days')"
            cursor.execute(query_recentes)
            row_recentes = cursor.fetchone()
            recentes = row_recentes['total'] if row_recentes else 0
            
            if recentes < 5:
                alertas.append({
                    "tipo": "AVISO",
                    "severidade": "media",
                    "mensagem": f"Apenas {recentes} empréstimos nos últimos 7 dias",
                    "acao": "Ativar campanhas de vendas"
                })
            
            # 3. Clientes sem movimento
            data_30dias = "CURRENT_TIMESTAMP - INTERVAL '30 days'" if db.is_postgres else "datetime('now', '-30 days')"
            cursor.execute(f"""
                SELECT COUNT(*) as total FROM clientes 
                WHERE status = 'lead' AND 
                data_criacao < {data_30dias}
            """)
            row_leads = cursor.fetchone()
            leads_antigos = row_leads['total'] if row_leads else 0
            
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
