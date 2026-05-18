from datetime import datetime

class Usuario:
    """usuário do sistema — autenticação e dados básicos"""

    def __init__(self, id, nome, email, senha_hash, data_criacao=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.data_criacao = data_criacao or datetime.now()

    def __repr__(self):
        return f"<Usuario {self.nome} ({self.email})>"
