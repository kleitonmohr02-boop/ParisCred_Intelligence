#!/usr/bin/env python3
"""Script de teste completo do banco de dados"""

import sqlite3
import sys

def test_database():
    """Testa o banco de dados"""
    try:
        # Conectar ao banco
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("=" * 60)
        print("✅ TESTE DO BANCO DE DADOS")
        print("=" * 60)
        print(f"\n📊 Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Contar usuários
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count_usuarios = cursor.fetchone()[0]
        print(f"\n👤 Usuários: {count_usuarios}")
        
        # Listar usuários
        cursor.execute("SELECT email, nome, role FROM usuarios")
        usuarios = cursor.fetchall()
        for user in usuarios:
            print(f"   ✓ {user[0]} ({user[1]}) - Role: {user[2]}")
        
        # Contar campanhas
        cursor.execute("SELECT COUNT(*) FROM campanhas")
        count_campanhas = cursor.fetchone()[0]
        print(f"\n📢 Campanhas: {count_campanhas}")
        
        # Contar histórico
        cursor.execute("SELECT COUNT(*) FROM historico")
        count_historico = cursor.fetchone()[0]
        print(f"📋 Histórico: {count_historico}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ BANCO DE DADOS OK!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
