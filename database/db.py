"""
Módulos de Banco de Dados - ParisCred AI
"""

import sqlite3
import json
import bcrypt
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, Dict, List, Any
import os

DATABASE_PATH = os.getenv("DATABASE_PATH", "pariscred.db")

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
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
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    nome TEXT NOT NULL,
                    senha_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'vendedor',
                    equipe TEXT,
                    meta_faturamento REAL DEFAULT 0,
                    ativo INTEGER DEFAULT 1,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TIMESTAMP
                )
            """)
            
            # Leads table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf TEXT UNIQUE,
                    telefone TEXT NOT NULL,
                    email TEXT,
                    data_nascimento TEXT,
                    nome_mae TEXT,
                    banco_beneficio TEXT,
                    numero_beneficio TEXT,
                    valor_beneficio REAL,
                    margem_disponivel REAL,
                    banco_atual TEXT,
                    valor_divida REAL,
                    valor_solicitado REAL,
                    etapa TEXT DEFAULT 'lead_novo',
                    score INTEGER DEFAULT 0,
                    tags TEXT,
                    observacoes TEXT,
                    historico_interacoes TEXT,
                    vendedor_id INTEGER,
                    ipiranga_id INTEGER,
                   Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TIMESTAMP,
                    FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
                )
            """)
            
            # Pipeline movements
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_movimentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER NOT NULL,
                    de_etapa TEXT,
                    para_etapa TEXT,
                    vendedor_id INTEGER,
                    observacao TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads(id),
                    FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
                )
            """)
            
            # Follow-ups
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS follow_ups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER NOT NULL,
                    data_agendada TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    observacao TEXT,
                    concluído INTEGER DEFAULT 0,
                    criado_por INTEGER,
                   Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads(id),
                    FOREIGN KEY (criado_por) REFERENCES usuarios(id)
                )
            """)
            
            # Extratos analisados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extratos_analisados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER,
                    contratos_json TEXT,
                    oportunidades_json TEXT,
                    analise_completa TEXT,
                   Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads(id)
                )
            """)
            
            # Mensagens WhatsApp
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensagens_whatsapp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER,
                    numero TEXT NOT NULL,
                    mensagem TEXT NOT NULL,
                    tipo TEXT DEFAULT 'enviada',
                    status TEXT,
                   INSTANCE_NAME TEXT,
                   Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads(id)
                )
            """)
            
            # Campanhas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campanhas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    mensagem TEXT NOT NULL,
                    botoes_json TEXT,
                    status TEXT DEFAULT 'rascunho',
                    criador_id INTEGER,
                    total_enviados INTEGER DEFAULT 0,
                   Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    Disparado_em TIMESTAMP,
                    FOREIGN KEY (criador_id) REFERENCES usuarios(id)
                )
            """)
            
            # Academy
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS academy_modulos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descricao TEXT,
                    conteudo TEXT,
                    ordem INTEGER,
                    ativo INTEGER DEFAULT 1
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS academy_progresso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    modulo_id INTEGER NOT NULL,
                    completo INTEGER DEFAULT 0,
                    nota REAL,
                   Completed_at TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                    FOREIGN KEY (modulo_id) REFERENCES academy_modulos(id)
                )
            """)
            
            # Métricas diárias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metricas_diarias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    vendedor_id INTEGER,
                    total_leads INTEGER DEFAULT 0,
                    leads_ganhos INTEGER DEFAULT 0,
                    leads_perdidos INTEGER DEFAULT 0,
                    mensagens_enviadas INTEGER DEFAULT 0,
                    conversao_pct REAL DEFAULT 0,
                    faturamento REAL DEFAULT 0,
                    FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
                )
            """)
            
            # Configurações
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracoes (
                    chave TEXT PRIMARY KEY,
                    valor TEXT
                )
            """)
            
            conn.commit()
            
            # Create admin user if not exists
            cursor.execute("SELECT id FROM usuarios WHERE email = 'admin@pariscred.com'")
            if not cursor.fetchone():
                senha_hash = bcrypt.hashpw('Admin@2025'.encode(), bcrypt.gensalt()).decode()
                cursor.execute("""
                    INSERT INTO usuarios (email, nome, senha_hash, role, ativo)
                    VALUES (?, ?, ?, ?, ?)
                """, ('admin@pariscred.com', 'Administrador', senha_hash, 'admin', 1))
                conn.commit()
                logger.info("Admin user created")

db = Database()

class UsuariosDB:
    @staticmethod
    def criar(email: str, nome: str, senha: str, role: str = 'vendedor', equipe: str = None) -> Optional[int]:
        try:
            senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO usuarios (email, nome, senha_hash, role, equipe)
                    VALUES (?, ?, ?, ?, ?)
                """, (email, nome, senha_hash, role, equipe))
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    @staticmethod
    def autenticar(email: str, senha: str) -> Optional[Dict]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE email = ? AND ativo = 1", (email,))
            row = cursor.fetchone()
            if row and bcrypt.checkpw(senha.encode(), row['senha_hash'].encode()):
                return dict(row)
        return None
    
    @staticmethod
    def listar_todos(role: str = None) -> List[Dict]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if role:
                cursor.execute("SELECT * FROM usuarios WHERE role = ? AND ativo = 1", (role,))
            else:
                cursor.execute("SELECT * FROM usuarios WHERE ativo = 1")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def obter(user_id: int) -> Optional[Dict]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def atualizar(user_id: int, **kwargs) -> bool:
        campos = []
        valores = []
        for k, v in kwargs.items():
            campos.append(f"{k} = ?")
            valores.append(v)
        valores.append(user_id)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE usuarios SET {', '.join(campos)}, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?", valores)
            return cursor.rowcount > 0

class LeadsDB:
    @staticmethod
    def criar(**dados) -> int:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO leads (nome, cpf, telefone, email, data_nascimento, nome_mae,
                    banco_beneficio, numero_beneficio, valor_beneficio, margem_disponivel,
                    banco_atual, valor_divida, valor_solicitado, etapa, score, tags, observacoes, vendedor_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados.get('nome'), dados.get('cpf'), dados.get('telefone'), dados.get('email'),
                dados.get('data_nascimento'), dados.get('nome_mae'), dados.get('banco_beneficio'),
                dados.get('numero_beneficio'), dados.get('valor_beneficio'), dados.get('margem_disponivel'),
                dados.get('banco_atual'), dados.get('valor_divida'), dados.get('valor_solicitado'),
                dados.get('etapa', 'lead_novo'), dados.get('score', 0), dados.get('tags'),
                dados.get('observacoes'), dados.get('vendedor_id')
            ))
            return cursor.lastrowid
    
    @staticmethod
    def listar(vendedor_id: int = None, etapa: str = None, limit: int = 100) -> List[Dict]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if vendedor_id and etapa:
                cursor.execute("SELECT * FROM leads WHERE vendedor_id = ? AND etapa = ? ORDER BY atualizado_em DESC LIMIT ?", (vendedor_id, etapa, limit))
            elif vendedor_id:
                cursor.execute("SELECT * FROM leads WHERE vendedor_id = ? ORDER BY atualizado_em DESC LIMIT ?", (vendedor_id, limit))
            elif etapa:
                cursor.execute("SELECT * FROM leads WHERE etapa = ? ORDER BY atualizado_em DESC LIMIT ?", (etapa, limit))
            else:
                cursor.execute(f"SELECT * FROM leads ORDER BY atualizado_em DESC LIMIT {limit}")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def obter(lead_id: int) -> Optional[Dict]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def atualizar(lead_id: int, **dados) -> bool:
        campos = []
        valores = []
        for k, v in dados.items():
            campos.append(f"{k} = ?")
            valores.append(v)
        valores.append(lead_id)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE leads SET {', '.join(campos)}, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?", valores)
            return cursor.rowcount > 0
    
    @staticmethod
    def mover_pipeline(lead_id: int, nova_etapa: str, vendedor_id: int, observacao: str = None) -> bool:
        lead = LeadsDB.obter(lead_id)
        if not lead:
            return False
        
        etapa_antiga = lead['etapa']
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE leads SET etapa = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?", (nova_etapa, lead_id))
            cursor.execute("""
                INSERT INTO pipeline_movimentos (lead_id, de_etapa, para_etapa, vendedor_id, observacao)
                VALUES (?, ?, ?, ?, ?)
            """, (lead_id, etapa_antiga, nova_etapa, vendedor_id, observacao))
        return True
    
    @staticmethod
    def contar_por_etapa(vendedor_id: int = None) -> Dict:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if vendedor_id:
                cursor.execute("""
                    SELECT etapa, COUNT(*) as total FROM leads 
                    WHERE vendedor_id = ? GROUP BY etapa
                """, (vendedor_id,))
            else:
                cursor.execute("SELECT etapa, COUNT(*) as total FROM leads GROUP BY etapa")
            return {row['etapa']: row['total'] for row in cursor.fetchall()}

class FollowUpsDB:
    @staticmethod
    def criar(lead_id: int, data_agendada: str, tipo: str, observacao: str = None, criado_por: int = None) -> int:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO follow_ups (lead_id, data_agendada, tipo, observacao, criado_por)
                VALUES (?, ?, ?, ?, ?)
            """, (lead_id, data_agendada, tipo, observacao, criado_por))
            return cursor.lastrowid
    
    @staticmethod
    def listar_pendentes(vendedor_id: int = None, limit: int = 50) -> List[Dict]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if vendedor_id:
                cursor.execute("""
                    SELECT f.*, l.nome as lead_nome, l.telefone 
                    FROM follow_ups f
                    JOIN leads l ON f.lead_id = l.id
                    WHERE f.concluido = 0 AND l.vendedor_id = ?
                    AND f.data_agendada <= datetime('now')
                    ORDER BY f.data_agendada LIMIT ?
                """, (vendedor_id, limit))
            else:
                cursor.execute("""
                    SELECT f.*, l.nome as lead_nome, l.telefone 
                    FROM follow_ups f
                    JOIN leads l ON f.lead_id = l.id
                    WHERE f.concluido = 0 AND f.data_agendada <= datetime('now')
                    ORDER BY f.data_agendada LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

class ExtratosDB:
    @staticmethod
    def salvar(lead_id: int, contratos: dict, oportunidades: dict, analise: str) -> int:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO extratos_analisados (lead_id, contratos_json, oportunidades_json, analise_completa)
                VALUES (?, ?, ?, ?)
            """, (lead_id, json.dumps(contratos), json.dumps(oportunidades), analise))
            return cursor.lastrowid

class CampanhasDB:
    @staticmethod
    def criar(nome: str, mensagem: str, descricao: str = None, criador_id: int = None) -> int:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO campanhas (nome, mensagem, descricao, criador_id)
                VALUES (?, ?, ?, ?)
            """, (nome, mensagem, descricao, criador_id))
            return cursor.lastrowid
    
    @staticmethod
    def listar(criador_id: int = None) -> List[Dict]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if criador_id:
                cursor.execute("SELECT * FROM campanhas WHERE criador_id = ? ORDER BY criado_em DESC", (criador_id,))
            else:
                cursor.execute("SELECT * FROM campanhas ORDER BY criado_em DESC")
            return [dict(row) for row in cursor.fetchall()]

class AcademyDB:
    @staticmethod
    def inicializar_modulos():
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM academy_modulos")
            if cursor.fetchone()[0] == 0:
                modulos = [
                    ("Fundamentos do Consignado", "Aprenda as bases do crédito consignado, tipos de benefício, e como calcular margem.", " basics_consignado", 1),
                    ("Portabilidade Master", "Domine a portabilidade e como transferir contratos para bancos com melhores taxas.", " portabilidade", 2),
                    ("Objeções e Fechamento", "Aprenda a lidar com objeções comuns e técnicas de fechamento.", " objeções_fechamento", 3),
                    ("Análise de Extrato", "Como analisar extratos de consignado e identificar oportunidades.", " analise_extrato", 4)
                ]
                cursor.executemany("INSERT INTO academy_modulos (titulo, descricao, conteudo, ordem) VALUES (?, ?, ?, ?)", modulos)
                conn.commit()

class ConfigDB:
    @staticmethod
    def get(chave: str, default: str = None) -> str:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
            row = cursor.fetchone()
            return row['valor'] if row else default
    
    @staticmethod
    def set(chave: str, valor: str):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?, ?)", (chave, valor))

# Initialize
logger = logging.getLogger(__name__)
logger.info("Database initialized")