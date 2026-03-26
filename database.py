import os
import sqlite3
import json
import bcrypt
import logging
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, Dict, List, Any, Tuple
import urllib.parse as urlparse

# Carregar variáveis de ambiente se não estiverem
from dotenv import load_dotenv
load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "app.db")
DATABASE_URL = os.getenv("DATABASE_URL")

logger = logging.getLogger(__name__)

class Database:
    """Gerenciador de banco de dados híbrido (SQLite/PostgreSQL)."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.is_postgres = DATABASE_URL and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://"))
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões de banco de dados."""
        if self.is_postgres:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # Ajuste para URLs do Heroku/Vercel (postgres:// -> postgresql://)
            url = DATABASE_URL.replace("postgres://", "postgresql://")
            
            conn = psycopg2.connect(url)
            try:
                # Usar cursor que retorna dicionários no Postgres para manter compatibilidade
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Erro no Postgres: {e}")
                raise
            finally:
                conn.close()
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Erro no SQLite: {e}")
                raise
            finally:
                conn.close()
    
    def _init_db(self):
        """Inicializa o banco de dados com schema adaptativo."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # SINTAXE ADAPTATIVA
            serial_type = "SERIAL" if self.is_postgres else "INTEGER"
            autoincrement = "" if self.is_postgres else "AUTOINCREMENT"
            primary_key = "PRIMARY KEY" if self.is_postgres else "PRIMARY KEY AUTOINCREMENT"
            
            # Tabela de usuários
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS usuarios (
                    email TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    senha_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ativo BOOLEAN DEFAULT { 'TRUE' if self.is_postgres else '1' }
                )
            """)
            
            # Tabela de campanhas
            if self.is_postgres:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS campanhas (
                        id SERIAL PRIMARY KEY,
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
                        ativo BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (criador) REFERENCES usuarios(email)
                    )
                """)
            else:
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
            if self.is_postgres:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS historico (
                        id SERIAL PRIMARY KEY,
                        campanha_id INTEGER NOT NULL,
                        usuario TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_beneficiarios INTEGER,
                        resultados_json TEXT,
                        ativo BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (campanha_id) REFERENCES campanhas(id),
                        FOREIGN KEY (usuario) REFERENCES usuarios(email)
                    )
                """)
            else:
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
# CLASSES DE ACESSO (MANTIDAS PARA COMPATIBILIDADE)
# ============================================================================

class UsuariosDB:
    @staticmethod
    def criar(email: str, nome: str, senha: str, role: str = "user") -> bool:
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
        db = Database()
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO usuarios (email, nome, senha_hash, role)
                    VALUES (%s, %s, %s, %s)
                """ if db.is_postgres else """
                    INSERT INTO usuarios (email, nome, senha_hash, role)
                    VALUES (?, ?, ?, ?)
                """, (email, nome, senha_hash, role))
            return True
        except Exception:
            return False

    @staticmethod
    def obter(email: str) -> Optional[Dict]:
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM usuarios WHERE email = {'%s' if db.is_postgres else '?'} AND ativo = {'TRUE' if db.is_postgres else '1'}", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def listar_todos() -> List[Dict]:
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM usuarios WHERE ativo = {'TRUE' if db.is_postgres else '1'}")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def verificar_senha(email: str, senha: str) -> bool:
        usuario = UsuariosDB.obter(email)
        if not usuario: return False
        try:
            return bcrypt.checkpw(senha.encode(), (usuario['senha_hash'] if isinstance(usuario['senha_hash'], str) else usuario['senha_hash'].tobytes()).encode() if isinstance(usuario['senha_hash'], bytes) else usuario['senha_hash'].encode())
        except Exception:
            return False

    @staticmethod
    def atualizar(email: str, **kwargs) -> bool:
        db = Database()
        campos = []
        valores = []
        for campo in ['nome', 'role']:
            if campo in kwargs:
                campos.append(f"{campo} = {'%s' if db.is_postgres else '?'}")
                valores.append(kwargs[campo])
        if not campos: return False
        valores.append(email)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE usuarios SET {', '.join(campos)} WHERE email = {'%s' if db.is_postgres else '?'} AND ativo = {'TRUE' if db.is_postgres else '1'}"
            cursor.execute(query, tuple(valores))
            return True

    @staticmethod
    def deletar(email: str) -> bool:
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE usuarios SET ativo = {'FALSE' if db.is_postgres else '0'} WHERE email = {'%s' if db.is_postgres else '?'}", (email,))
            return True

class CampanhasDB:
    @staticmethod
    def criar(nome: str, descricao: str, criador: str, mensagem: str, 
              beneficiarios: List[Dict] = None, botoes: List[Dict] = None,
              instancias: List[str] = None) -> Optional[int]:
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            placeholder = "%s" if db.is_postgres else "?"
            cursor.execute(f"""
                INSERT INTO campanhas (
                    nome, descricao, criador, mensagem, 
                    beneficiarios_json, botoes_json, instancias_json
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                {"RETURNING id" if db.is_postgres else ""}
            """, (
                nome, descricao, criador, mensagem,
                json.dumps(beneficiarios or []),
                json.dumps(botoes or []),
                json.dumps(instancias or [])
            ))
            if db.is_postgres:
                return cursor.fetchone()['id']
            return cursor.lastrowid

    @staticmethod
    def obter(campanha_id: int) -> Optional[Dict]:
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM campanhas WHERE id = {'%s' if db.is_postgres else '?'} AND ativo = {'TRUE' if db.is_postgres else '1'}", (campanha_id,))
            row = cursor.fetchone()
            if not row: return None
            campanha = dict(row)
            for k in ['beneficiarios_json', 'botoes_json', 'instancias_json']:
                campanha[k] = json.loads(campanha[k] or '[]')
            return campanha

    @staticmethod
    def listar_todas() -> List[Dict]:
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM campanhas WHERE ativo = {'TRUE' if db.is_postgres else '1'} ORDER BY criado_em DESC")
            results = []
            for row in cursor.fetchall():
                campanha = dict(row)
                for k in ['beneficiarios_json', 'botoes_json', 'instancias_json']:
                    campanha[k] = json.loads(campanha[k] or '[]')
                results.append(campanha)
            return results

    @staticmethod
    def listar_por_criador(email: str) -> List[Dict]:
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM campanhas WHERE criador = {'%s' if db.is_postgres else '?'} AND ativo = {'TRUE' if db.is_postgres else '1'} ORDER BY criado_em DESC", (email,))
            results = []
            for row in cursor.fetchall():
                campanha = dict(row)
                for k in ['beneficiarios_json', 'botoes_json', 'instancias_json']:
                    campanha[k] = json.loads(campanha[k] or '[]')
                results.append(campanha)
            return results

    @staticmethod
    def atualizar(campanha_id: int, **kwargs) -> bool:
        db = Database()
        campos_permitidos = {'nome', 'descricao', 'status', 'mensagem', 'beneficiarios_json', 'botoes_json', 'instancias_json', 'disparado_em', 'total_enviados'}
        campos = []
        valores = []
        placeholder = "%s" if db.is_postgres else "?"
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                if campo.endswith('_json') and isinstance(valor, (list, dict)):
                    valor = json.dumps(valor)
                campos.append(f"{campo} = {placeholder}")
                valores.append(valor)
        if not campos: return False
        valores.append(campanha_id)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE campanhas SET {', '.join(campos)} WHERE id = {placeholder} AND ativo = {'TRUE' if db.is_postgres else '1'}"
            cursor.execute(query, tuple(valores))
            return True

    @staticmethod
    def deletar(campanha_id: int) -> bool:
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE campanhas SET ativo = {'FALSE' if db.is_postgres else '0'} WHERE id = {'%s' if db.is_postgres else '?'}", (campanha_id,))
            return True

class HistoricoDB:
    @staticmethod
    def registrar(campanha_id: int, usuario: str, total_beneficiarios: int, resultados: Dict = None) -> Optional[int]:
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            placeholder = "%s" if db.is_postgres else "?"
            cursor.execute(f"""
                INSERT INTO historico (campanha_id, usuario, total_beneficiarios, resultados_json)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                {"RETURNING id" if db.is_postgres else ""}
            """, (campanha_id, usuario, total_beneficiarios, json.dumps(resultados or {})))
            if db.is_postgres:
                return cursor.fetchone()['id']
            return cursor.lastrowid
