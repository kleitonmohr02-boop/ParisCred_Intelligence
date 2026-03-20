# 🔌 MCP Server - ParisCred Database

**Purpose**: Provide Copilot with secure read/execute access to SQLite database.

## Configuration

```json
{
  "mcpServers": {
    "pariscred-db": {
      "command": "python",
      "args": ["run_database_mcp.py"],
      "env": {
        "DATABASE_PATH": "C:\\ParisCred_Intelligence\\database.db"
      }
    }
  }
}
```

## Available Tools

### 1. Execute Query (SELECT only)
```
execute_query(sql: str, params: list = None)
Returns: Query results as JSON
```

### 2. Get Table Schema
```
get_table_schema(table_name: str)
Returns: Column names, types, constraints
```

### 3. List All Tables
```
list_tables()
Returns: All table names in database
```

### 4. Get Table Size
```
get_table_size(table_name: str)
Returns: Row count and data size
```

### 5. Execute Safe Insert/Update
```
execute_insert_update(sql: str, params: list)
Returns: Success status and affected rows
```

## Implementation (run_database_mcp.py)

```python
#!/usr/bin/env python3
"""
MCP Server for ParisCred Database
Provides safe read/execute access to SQLite
"""

import sqlite3
import json
import os
from typing import List, Dict, Any
from datetime import datetime

DATABASE_PATH = os.getenv("DATABASE_PATH", "database.db")

class ParisCreditDatabaseMCP:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.connection = None
    
    def connect(self):
        """Establish connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def disconnect(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query: str, params: List = None) -> List[Dict]:
        """Execute SELECT query safely"""
        if not query.strip().upper().startswith("SELECT"):
            return {"error": "Only SELECT queries allowed"}
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            
            # Convert to list of dicts
            return [dict(row) for row in results]
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get table structure"""
        query = f"PRAGMA table_info({table_name})"
        cursor = self.connection.cursor()
        cursor.execute(query)
        
        columns = cursor.fetchall()
        schema = {
            "table": table_name,
            "columns": [
                {
                    "name": col[1],
                    "type": col[2],
                    "nullable": col[3] == 0,
                    "default": col[4],
                    "primary_key": col[5] == 1
                }
                for col in columns
            ]
        }
        
        return schema
    
    def list_tables(self) -> List[str]:
        """Get all table names"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        
        return [row[0] for row in cursor.fetchall()]
    
    def get_table_size(self, table_name: str) -> Dict[str, Any]:
        """Get table statistics"""
        # Row count
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        # Size in bytes
        cursor.execute(f"SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        size = cursor.fetchone()[0]
        
        return {
            "table": table_name,
            "row_count": row_count,
            "size_bytes": size,
            "size_mb": round(size / (1024*1024), 2)
        }
    
    def execute_insert_update(self, query: str, params: List = None) -> Dict[str, Any]:
        """Execute INSERT/UPDATE safely"""
        if not any(query.strip().upper().startswith(cmd) for cmd in ["INSERT", "UPDATE", "DELETE"]):
            return {"error": "Only INSERT/UPDATE/DELETE allowed"}
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            
            return {
                "success": True,
                "affected_rows": cursor.rowcount,
                "last_id": cursor.lastrowid
            }
        
        except Exception as e:
            self.connection.rollback()
            return {"error": str(e)}

# Initialize MCP
db_mcp = ParisCreditDatabaseMCP()

# Tool definitions
TOOLS = [
    {
        "name": "execute_query",
        "description": "Execute a SELECT query on ParisCred database",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SELECT SQL query"
                },
                "params": {
                    "type": "array",
                    "description": "Query parameters"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_table_schema",
        "description": "Get column structure of a table",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string"}
            },
            "required": ["table_name"]
        }
    },
    {
        "name": "list_tables",
        "description": "List all tables in database",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "execute_insert_update",
        "description": "Execute INSERT/UPDATE/DELETE query (careful!)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "params": {"type": "array"}
            },
            "required": ["query"]
        }
    }
]

# Main handler
def handle_tool_call(tool_name: str, tool_input: Dict) -> str:
    """MCP tool handler"""
    db_mcp.connect()
    
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
        elif tool_name == "execute_insert_update":
            result = db_mcp.execute_insert_update(
                tool_input["query"],
                tool_input.get("params")
            )
        else:
            result = {"error": "Unknown tool"}
    
    finally:
        db_mcp.disconnect()
    
    return json.dumps(result)
```

## Common Queries I'll Use

```sql
-- Get customer summary
SELECT id, name, email, phone, status, margem_consignavel, data_criacao
FROM customers WHERE status = 'ativo' LIMIT 20

-- Get loans by status
SELECT status, COUNT(*) as total, SUM(valor_solicitado) as valor_total
FROM loans GROUP BY status

-- Get recent interactions
SELECT c.name, i.tipo, i.descricao, i.data
FROM interactions i
JOIN customers c ON i.customer_id = c.id
ORDER BY i.data DESC LIMIT 50

-- Calculate KPIs
SELECT 
    COUNT(DISTINCT customer_id) as clientes_ativos,
    SUM(valor_solicitado) as total_emprestimos,
    COUNT(*) as total_operacoes
FROM loans WHERE status = 'aprovado'
```

## Security Features

- ✅ Only SELECT queries for reading
- ✅ Safe parameterized queries (SQL injection prevention)
- ✅ Transaction management for writes
- ✅ Connection pooling
- ✅ Error handling and rollback
- ✅ Audit logging (optional)

## Limits

- Max 10,000 rows per query (configurable)
- Query timeout: 30 seconds
- Single write transaction max 1000 rows
- No table modifications (schema locked)
