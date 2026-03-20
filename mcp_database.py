"""
MCP Server: ParisCred Database
Acesso seguro ao SQLite
"""

import sqlite3
import json
import os
from typing import Dict, Any, List, Optional


class ParisCreditDatabaseMCP:
    """MCP Server para banco de dados ParisCred"""
    
    def __init__(self):
        self.db_path = os.getenv("DATABASE_PATH", "app.db")
        self.connection = None
    
    def _get_connection(self):
        """Obtém conexão com banco"""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Fecha conexão"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: List = None) -> Dict[str, Any]:
        """Execute SELECT query segura"""
        
        # Validação: apenas SELECTs
        if not query.strip().upper().startswith("SELECT"):
            return {
                "sucesso": False,
                "erro": "Apenas queries SELECT são permitidas"
            }
        
        try:
            cursor = self._get_connection().cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            
            # Limitar a 10k resultados
            if len(results) > 10000:
                results = results[:10000]
                warning = "Resultados truncados em 10.000 linhas"
            else:
                warning = None
            
            return {
                "sucesso": True,
                "resultados": [dict(row) for row in results],
                "linhas": len(results),
                "aviso": warning
            }
        
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Obtém schema de uma tabela"""
        try:
            cursor = self._get_connection().cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            
            columns = cursor.fetchall()
            schema = {
                "tabela": table_name,
                "colunas": [
                    {
                        "nome": col[1],
                        "tipo": col[2],
                        "nullable": col[3] == 0,
                        "default": col[4],
                        "primary_key": col[5] == 1
                    }
                    for col in columns
                ]
            }
            
            return {"sucesso": True, "data": schema}
        
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def list_tables(self) -> Dict[str, Any]:
        """Lista todas as tabelas"""
        try:
            cursor = self._get_connection().cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            return {
                "sucesso": True,
                "tabelas": tables,
                "total": len(tables)
            }
        
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def get_table_size(self, table_name: str) -> Dict[str, Any]:
        """Retorna estatísticas da tabela"""
        try:
            cursor = self._get_connection().cursor()
            
            # Contar linhas
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Tamanho estimado
            size_bytes = row_count * 100  # Estimativa simplificada
            size_mb = size_bytes / (1024 * 1024)
            
            return {
                "sucesso": True,
                "tabela": table_name,
                "linhas": row_count,
                "tamanho_bytes": size_bytes,
                "tamanho_mb": round(size_mb, 2)
            }
        
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def execute_insert_update(self, query: str, params: List = None) -> Dict[str, Any]:
        """Execute INSERT/UPDATE/DELETE (cuidado!)"""
        
        # Validação: apenas INSERT/UPDATE/DELETE
        first_word = query.strip().upper().split()[0]
        
        if first_word not in ["INSERT", "UPDATE", "DELETE"]:
            return {
                "sucesso": False,
                "erro": "Apenas INSERT/UPDATE/DELETE são permitidas"
            }
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            
            return {
                "sucesso": True,
                "linhas_afetadas": cursor.rowcount,
                "ultimo_id": cursor.lastrowid if first_word == "INSERT" else None
            }
        
        except Exception as e:
            if conn:
                conn.rollback()
            
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def backup_database(self) -> Dict[str, Any]:
        """Faz backup do banco"""
        try:
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/app_{timestamp}.db"
            
            # Criar pasta backups se não existir
            os.makedirs("backups", exist_ok=True)
            
            # Copiar arquivo
            shutil.copy(self.db_path, backup_path)
            
            return {
                "sucesso": True,
                "arquivo": backup_path,
                "timestamp": timestamp
            }
        
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def get_database_info(self) -> Dict[str, Any]:
        """Info geral do banco"""
        try:
            # Tamanho do arquivo
            file_size = os.path.getsize(self.db_path)
            
            # Número de tabelas
            cursor = self._get_connection().cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            num_tables = cursor.fetchone()[0]
            
            return {
                "sucesso": True,
                "arquivo": self.db_path,
                "tamanho_bytes": file_size,
                "tamanho_mb": round(file_size / (1024*1024), 2),
                "tabelas": num_tables,
                "tipo": "SQLite 3"
            }
        
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}


# Instância global
db_mcp = ParisCreditDatabaseMCP()


# Definições de ferramentas MCP
MCP_TOOLS = [
    {
        "name": "execute_query",
        "description": "Executar query SELECT no banco de dados",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Query SQL SELECT"},
                "params": {
                    "type": "array",
                    "description": "Parâmetros da query (opcional)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_table_schema",
        "description": "Obter estrutura de uma tabela",
        "input_schema": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string"}
            },
            "required": ["table_name"]
        }
    },
    {
        "name": "list_tables",
        "description": "Listar todas as tabelas do banco",
        "input_schema": {"type": "object"}
    },
    {
        "name": "get_table_size",
        "description": "Estatísticas de uma tabela",
        "input_schema": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string"}
            },
            "required": ["table_name"]
        }
    },
    {
        "name": "execute_insert_update",
        "description": "Executar INSERT/UPDATE/DELETE (cuidado!)",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "params": {"type": "array"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "backup_database",
        "description": "Fazer backup do banco de dados",
        "input_schema": {"type": "object"}
    },
    {
        "name": "get_database_info",
        "description": "Informações geral do banco",
        "input_schema": {"type": "object"}
    }
]


def handle_tool_call(tool_name: str, tool_input: Dict) -> str:
    """Handler para chamadas de ferramentas MCP"""
    
    try:
        if tool_name == "execute_query":
            result = db_mcp.execute_query(
                tool_input["query"],
                tool_input.get("params")
            )
        
        elif tool_name == "get_table_schema":
            result = db_mcp.get_table_schema(tool_input["table_name"])
        
        elif tool_name == "list_tables":
            result = db_mcp.list_tables()
        
        elif tool_name == "get_table_size":
            result = db_mcp.get_table_size(tool_input["table_name"])
        
        elif tool_name == "execute_insert_update":
            result = db_mcp.execute_insert_update(
                tool_input["query"],
                tool_input.get("params")
            )
        
        elif tool_name == "backup_database":
            result = db_mcp.backup_database()
        
        elif tool_name == "get_database_info":
            result = db_mcp.get_database_info()
        
        else:
            result = {"erro": f"Ferramenta desconhecida: {tool_name}"}
    
    finally:
        db_mcp.close()
    
    return json.dumps(result, ensure_ascii=False)
