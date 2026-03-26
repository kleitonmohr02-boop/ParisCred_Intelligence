"""
Validação de dados - ParisCred Intelligence
Versão sem dependências externas (sem Pydantic)
"""

import re
from typing import Optional, List, Dict, Any


class ValidationError(Exception):
    """Erro de validação personalizado"""
    pass


def validar_email(email: str) -> bool:
    """Valida formato de email"""
    if not email or len(email) < 3:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validar_telefone(numero: str) -> bool:
    """Valida número de telefone (mínimo 10 dígitos)"""
    numeros = ''.join(filter(str.isdigit, numero or ''))
    return len(numeros) >= 10


def validar_cpf(cpf: str) -> bool:
    """Valida CPF brasileiro"""
    if not cpf:
        return True  # CPF é opcional
    
    numeros = ''.join(filter(str.isdigit, cpf))
    
    if len(numeros) != 11:
        return False
    
    # Validação simples (não é o algoritmo completo)
    return True


def validar_len(valor: str, min_len: int = 1, max_len: int = 100) -> bool:
    """Valida comprimento de string"""
    if valor is None:
        return False
    return min_len <= len(str(valor)) <= max_len


# ============================================================
# Validadores de entrada
# ============================================================

class UsuarioLogin:
    def __init__(self, email: str, senha: str):
        if not validar_email(email):
            raise ValidationError('Email inválido')
        if not validar_len(senha, 6, 100):
            raise ValidationError('Senha deve ter entre 6 e 100 caracteres')
        
        self.email = email.lower()
        self.senha = senha


class UsuarioCreate:
    def __init__(self, email: str, nome: str, senha: str, role: str = 'vendedor'):
        if not validar_email(email):
            raise ValidationError('Email inválido')
        if not validar_len(nome, 2, 100):
            raise ValidationError('Nome deve ter entre 2 e 100 caracteres')
        if not validar_len(senha, 6, 100):
            raise ValidationError('Senha deve ter entre 6 e 100 caracteres')
        if role not in ['admin', 'vendedor', 'gestor']:
            raise ValidationError('Role deve ser admin, vendedor ou gestor')
        
        self.email = email.lower()
        self.nome = nome
        self.senha = senha
        self.role = role


class Beneficiario:
    def __init__(self, nome: str, numero: str, cpf: Optional[str] = None):
        if not validar_len(nome, 1, 100):
            raise ValidationError('Nome do beneficiário inválido')
        if not validar_telefone(numero):
            raise ValidationError('Número de telefone inválido')
        if cpf and not validar_cpf(cpf):
            raise ValidationError('CPF inválido')
        
        self.nome = nome
        self.numero = ''.join(filter(str.isdigit, numero))
        self.cpf = cpf
    
    def to_dict(self) -> Dict:
        return {
            'nome': self.nome,
            'numero': self.numero,
            'cpf': self.cpf
        }


class Botao:
    def __init__(self, id: str, text: str):
        if not validar_len(id, 1, 50):
            raise ValidationError('ID do botão inválido')
        if not validar_len(text, 1, 100):
            raise ValidationError('Texto do botão inválido')
        
        self.id = id
        self.text = text
    
    def to_dict(self) -> Dict:
        return {'id': self.id, 'text': self.text}


class CampanhaCreate:
    def __init__(
        self,
        nome: str,
        mensagem: str,
        descricao: Optional[str] = None,
        beneficiarios: Optional[List[Dict]] = None,
        botoes: Optional[List[Dict]] = None,
        instancias: Optional[List[str]] = None
    ):
        if not validar_len(nome, 2, 100):
            raise ValidationError('Nome da campanha deve ter entre 2 e 100 caracteres')
        if not validar_len(mensagem, 1, 4000):
            raise ValidationError('Mensagem deve ter entre 1 e 4000 caracteres')
        
        self.nome = nome
        self.descricao = descricao or ''
        self.mensagem = mensagem
        self.beneficiarios = beneficiarios or []
        self.botoes = botoes or []
        self.instancias = instancias or ['Paris_01']
        
        # Validar beneficiários
        for b in self.beneficiarios:
            Beneficiario(
                nome=b.get('nome', ''),
                numero=b.get('numero', ''),
                cpf=b.get('cpf')
            )


class UsuarioUpdate:
    def __init__(self, nome: Optional[str] = None, role: Optional[str] = None):
        if nome is not None and not validar_len(nome, 2, 100):
            raise ValidationError('Nome deve ter entre 2 e 100 caracteres')
        if role is not None and role not in ['admin', 'vendedor', 'gestor']:
            raise ValidationError('Role deve ser admin, vendedor ou gestor')
        
        self.nome = nome
        self.role = role