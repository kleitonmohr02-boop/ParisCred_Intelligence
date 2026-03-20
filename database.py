import sqlite3
import json
import bcrypt
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, Dict, List, Any, Tuple

DATABASE_PATH = "app.db"


class Database:
    """Gerenciador de banco de dados SQLite com suporte a transações e soft delete."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões de banco de dados."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Inicializa o banco de dados com schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de usuários
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    email TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    senha_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ativo BOOLEAN DEFAULT 1
                )
            """)
            
            # Tabela de campanhas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campanhas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    status TEXT NOT NULL DEFAULT 'rascunho',
                    criador TEXT NOT NULL,
                    beneficiarios_json TEXT,
                    mensagem TEXT NOT NULL,
                    botoes_json TEXT,
                    instancias_json TEXT,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    disparado_em TIMESTAMP,
                    total_enviados INTEGER DEFAULT 0,
                    ativo BOOLEAN DEFAULT 1,
                    FOREIGN KEY (criador) REFERENCES usuarios(email)
                )
            """)
            
            # Tabela de histórico
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campanha_id INTEGER NOT NULL,
                    usuario TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_beneficiarios INTEGER,
                    resultados_json TEXT,
                    ativo BOOLEAN DEFAULT 1,
                    FOREIGN KEY (campanha_id) REFERENCES campanhas(id),
                    FOREIGN KEY (usuario) REFERENCES usuarios(email)
                )
            """)
            
            conn.commit()


# ============================================================================
# FUNÇÕES DE USUÁRIOS
# ============================================================================

class UsuariosDB:
    
    @staticmethod
    def criar(email: str, nome: str, senha: str, role: str = "user") -> bool:
        """Cria novo usuário com hash de senha."""
        try:
            senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
            db = Database()
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO usuarios (email, nome, senha_hash, role)
                    VALUES (?, ?, ?, ?)
                """, (email, nome, senha_hash, role))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    def obter(email: str) -> Optional[Dict]:
        """Obtém usuário ativo por email."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM usuarios WHERE email = ? AND ativo = 1
            """, (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def listar_todos() -> List[Dict]:
        """Lista todos os usuários ativos."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE ativo = 1")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def verificar_senha(email: str, senha: str) -> bool:
        """Verifica se a senha está correta para o usuário."""
        usuario = UsuariosDB.obter(email)
        if not usuario:
            return False
        
        try:
            return bcrypt.checkpw(senha.encode(), usuario['senha_hash'].encode())
        except Exception:
            return False
    
    @staticmethod
    def atualizar(email: str, **kwargs) -> bool:
        """Atualiza dados do usuário (exceto senha)."""
        db = Database()
        campos = []
        valores = []
        
        for campo in ['nome', 'role']:
            if campo in kwargs:
                campos.append(f"{campo} = ?")
                valores.append(kwargs[campo])
        
        if not campos:
            return False
        
        valores.append(email)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE usuarios SET {', '.join(campos)} WHERE email = ? AND ativo = 1"
            cursor.execute(query, tuple(valores))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def deletar(email: str) -> bool:
        """Soft delete de usuário."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET ativo = 0 WHERE email = ?", (email,))
            conn.commit()
            return cursor.rowcount > 0


# ============================================================================
# FUNÇÕES DE CAMPANHAS
# ============================================================================

class CampanhasDB:
    
    @staticmethod
    def criar(nome: str, descricao: str, criador: str, mensagem: str, 
              beneficiarios: List[str] = None, botoes: List[Dict] = None,
              instancias: List[str] = None) -> Optional[int]:
        """Cria nova campanha."""
        db = Database()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO campanhas (
                    nome, descricao, criador, mensagem, 
                    beneficiarios_json, botoes_json, instancias_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                nome, descricao, criador, mensagem,
                json.dumps(beneficiarios or []),
                json.dumps(botoes or []),
                json.dumps(instancias or [])
            ))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def obter(campanha_id: int) -> Optional[Dict]:
        """Obtém campanha ativa por ID."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM campanhas WHERE id = ? AND ativo = 1
            """, (campanha_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            campanha = dict(row)
            # Parse JSON fields
            campanha['beneficiarios_json'] = json.loads(campanha['beneficiarios_json'] or '[]')
            campanha['botoes_json'] = json.loads(campanha['botoes_json'] or '[]')
            campanha['instancias_json'] = json.loads(campanha['instancias_json'] or '[]')
            
            return campanha
    
    @staticmethod
    def listar_todas() -> List[Dict]:
        """Lista todas as campanhas ativas."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM campanhas WHERE ativo = 1 ORDER BY criado_em DESC")
            campanhas = []
            
            for row in cursor.fetchall():
                campanha = dict(row)
                campanha['beneficiarios_json'] = json.loads(campanha['beneficiarios_json'] or '[]')
                campanha['botoes_json'] = json.loads(campanha['botoes_json'] or '[]')
                campanha['instancias_json'] = json.loads(campanha['instancias_json'] or '[]')
                campanhas.append(campanha)
            
            return campanhas
    
    @staticmethod
    def listar_por_criador(email: str) -> List[Dict]:
        """Lista campanhas do criador."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM campanhas 
                WHERE criador = ? AND ativo = 1 
                ORDER BY criado_em DESC
            """, (email,))
            campanhas = []
            
            for row in cursor.fetchall():
                campanha = dict(row)
                campanha['beneficiarios_json'] = json.loads(campanha['beneficiarios_json'] or '[]')
                campanha['botoes_json'] = json.loads(campanha['botoes_json'] or '[]')
                campanha['instancias_json'] = json.loads(campanha['instancias_json'] or '[]')
                campanhas.append(campanha)
            
            return campanhas
    
    @staticmethod
    def atualizar(campanha_id: int, **kwargs) -> bool:
        """Atualiza campanha (com transação)."""
        db = Database()
        campos_permitidos = {
            'nome', 'descricao', 'status', 'mensagem',
            'beneficiarios_json', 'botoes_json', 'instancias_json',
            'disparado_em', 'total_enviados'
        }
        
        campos = []
        valores = []
        
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                if campo.endswith('_json') and isinstance(valor, (list, dict)):
                    valor = json.dumps(valor)
                campos.append(f"{campo} = ?")
                valores.append(valor)
        
        if not campos:
            return False
        
        valores.append(campanha_id)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE campanhas SET {', '.join(campos)} WHERE id = ? AND ativo = 1"
            cursor.execute(query, tuple(valores))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def deletar(campanha_id: int) -> bool:
        """Soft delete de campanha."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE campanhas SET ativo = 0 WHERE id = ?", (campanha_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def incrementar_enviados(campanha_id: int, quantidade: int = 1) -> bool:
        """Incrementa contador de envios."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE campanhas 
                SET total_enviados = total_enviados + ? 
                WHERE id = ? AND ativo = 1
            """, (quantidade, campanha_id))
            conn.commit()
            return cursor.rowcount > 0


# ============================================================================
# FUNÇÕES DE HISTÓRICO
# ============================================================================

class HistoricoDB:
    
    @staticmethod
    def registrar(campanha_id: int, usuario: str, total_beneficiarios: int,
                  resultados: Dict = None) -> Optional[int]:
        """Registra execução de campanha no histórico."""
        db = Database()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO historico (
                    campanha_id, usuario, total_beneficiarios, resultados_json
                ) VALUES (?, ?, ?, ?)
            """, (
                campanha_id, usuario, total_beneficiarios,
                json.dumps(resultados or {})
            ))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def obter(historico_id: int) -> Optional[Dict]:
        """Obtém registro de histórico ativo."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM historico WHERE id = ? AND ativo = 1
            """, (historico_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            historico = dict(row)
            historico['resultados_json'] = json.loads(historico['resultados_json'] or '{}')
            
            return historico
    
    @staticmethod
    def listar_por_campanha(campanha_id: int) -> List[Dict]:
        """Lista histórico de execuções da campanha."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM historico 
                WHERE campanha_id = ? AND ativo = 1
                ORDER BY timestamp DESC
            """, (campanha_id,))
            
            historicos = []
            for row in cursor.fetchall():
                historico = dict(row)
                historico['resultados_json'] = json.loads(historico['resultados_json'] or '{}')
                historicos.append(historico)
            
            return historicos
    
    @staticmethod
    def listar_por_usuario(email: str) -> List[Dict]:
        """Lista histórico do usuário."""
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM historico 
                WHERE usuario = ? AND ativo = 1
                ORDER BY timestamp DESC
            """, (email,))
            
            historicos = []
            for row in cursor.fetchall():
                historico = dict(row)
                historico['resultados_json'] = json.loads(historico['resultados_json'] or '{}')
                historicos.append(historico)
            
            return historicos
