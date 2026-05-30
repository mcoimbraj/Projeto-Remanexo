from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# ═══════════════════════════════════════════════════════
# MODELO: usuário — autenticação (rf01)
# ═══════════════════════════════════════════════════════
class UsuarioModel(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    # relacionamentos
    contas = db.relationship('ContaModel', backref='usuario', lazy=True, cascade='all, delete-orphan')
    metas = db.relationship('MetaModel', backref='usuario', lazy=True, cascade='all, delete-orphan')
    assinatura = db.relationship('AssinaturaModel', backref='usuario', uselist=False, cascade='all, delete-orphan')
    nexo = db.relationship('NexoModel', backref='usuario', uselist=False, cascade='all, delete-orphan')

    def definir_senha(self, senha):
        """hash da senha com werkzeug — nunca armazena em plain text (rf01)"""
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        """verifica se a senha bate com o hash (rf01)"""
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f"<Usuario {self.nome}>"


# ═══════════════════════════════════════════════════════
# MODELO: conta — saldo encapsulado (rf03)
# ═══════════════════════════════════════════════════════
class ContaModel(db.Model):
    __tablename__ = 'contas'

    id = db.Column(db.Integer, primary_key=True)
    numero_conta = db.Column(db.String(20), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    saldo = db.Column(db.Float, default=0)
    status_assinatura = db.Column(db.String(20), default='ativa')
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    # relacionamento
    transacoes = db.relationship('TransacaoModel', backref='conta', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Conta {self.numero_conta}: R$ {self.saldo:.2f}>"


# ═══════════════════════════════════════════════════════
# MODELO: transação — polimorfismo de receita/despesa
# ═══════════════════════════════════════════════════════
class TransacaoModel(db.Model):
    __tablename__ = 'transacoes'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'receita' ou 'despesa'
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)
    categoria = db.Column(db.String(50), default='geral')
    status = db.Column(db.String(20), default='ativa')  # 'ativa' ou 'descartada' (rf04)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=False)
    
    # parcelamento (rf08 — visualização futura)
    eh_parcelada = db.Column(db.Boolean, default=False)
    num_parcelas = db.Column(db.Integer, default=1)
    parcelas = db.relationship('ParcelaModel', backref='transacao', lazy=True, cascade='all, delete-orphan')

    # discriminador pra SQLAlchemy
    __mapper_args__ = {
        'polymorphic_identity': 'transacao',
        'polymorphic_on': tipo
    }

    def calcular_impacto_saldo(self):
        """polimorfismo — cada subclasse implementa seu jeito"""
        if self.status == 'descartada':
            return 0
        return 0  # base não faz nada, herança implementa

    def __repr__(self):
        return f"<Transacao {self.tipo}: {self.descricao} R$ {self.valor:.2f}>"


# ═══════════════════════════════════════════════════════
# MODELO: receita — polimorfismo (rf03)
# ═══════════════════════════════════════════════════════
class ReceitaModel(TransacaoModel):
    __mapper_args__ = {
        'polymorphic_identity': 'receita',
    }

    def calcular_impacto_saldo(self):
        """receita soma no saldo"""
        if self.status == 'ativa':
            return self.valor
        return 0


# ═══════════════════════════════════════════════════════
# MODELO: despesa — polimorfismo (rf03)
# ═══════════════════════════════════════════════════════
class DespesaModel(TransacaoModel):
    __mapper_args__ = {
        'polymorphic_identity': 'despesa',
    }

    def calcular_impacto_saldo(self):
        """despesa subtrai do saldo"""
        if self.status == 'ativa':
            return -self.valor
        return 0


# ═══════════════════════════════════════════════════════
# MODELO: parcela — parcelamento de transações (rf08)
# ═══════════════════════════════════════════════════════
class ParcelaModel(db.Model):
    __tablename__ = 'parcelas'

    id = db.Column(db.Integer, primary_key=True)
    transacao_id = db.Column(db.Integer, db.ForeignKey('transacoes.id'), nullable=False)
    numero = db.Column(db.Integer, nullable=False)  # ex: 1/12, 2/12, etc
    valor = db.Column(db.Float, nullable=False)
    data_vencimento = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # 'pendente', 'paga', 'descartada'
    data_pagamento = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Parcela {self.numero} R$ {self.valor:.2f} ({self.status})>"


# ═══════════════════════════════════════════════════════
# MODELO: meta — progresso com barra (rf05)
# ═══════════════════════════════════════════════════════
class MetaModel(db.Model):
    __tablename__ = 'metas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    valor_alvo = db.Column(db.Float, nullable=False)
    valor_acumulado = db.Column(db.Float, default=0)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    data_prazo = db.Column(db.DateTime)
    ativa = db.Column(db.Boolean, default=True)

    @property
    def percentual_progresso(self):
        """barra de progresso — rf05"""
        if self.valor_alvo == 0:
            return 0
        percentual = (self.valor_acumulado / self.valor_alvo) * 100
        return min(percentual, 100)

    @property
    def valor_restante(self):
        """quanto falta pra bater a meta"""
        return max(0, self.valor_alvo - self.valor_acumulado)

    def __repr__(self):
        return f"<Meta {self.descricao}: R$ {self.valor_acumulado:.2f} / {self.valor_alvo:.2f}>"


# ═══════════════════════════════════════════════════════
# MODELO: assinatura — controla plano do usuário
# ═══════════════════════════════════════════════════════
class AssinaturaModel(db.Model):
    __tablename__ = 'assinaturas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    tipo = db.Column(db.String(20), default='gratuita')  # 'gratuita', 'basica', 'premium'
    data_inicio = db.Column(db.DateTime, default=datetime.now)
    data_renovacao = db.Column(db.DateTime)
    ativa = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Assinatura {self.tipo} (usuario={self.usuario_id})>"


# ═══════════════════════════════════════════════════════
# MODELO: nexo — open finance simulado (rf02, padrão state)
# ═══════════════════════════════════════════════════════
class NexoModel(db.Model):
    __tablename__ = 'nexo'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    estado = db.Column(db.String(20), default='ativo')  # 'ativo', 'instavel', 'erro'
    fila_pendente = db.Column(db.Integer, default=0)
    ultimo_sync = db.Column(db.DateTime)
    mensagem_erro = db.Column(db.String(200))

    def __repr__(self):
        return f"<Nexo usuario={self.usuario_id} estado={self.estado}>"


# ═══════════════════════════════════════════════════════
# MODELO: notificação (rf09 — alerta de gasto excessivo)
# ═══════════════════════════════════════════════════════
class NotificacaoModel(db.Model):
    __tablename__ = 'notificacoes'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'alerta_gasto_excessivo', etc
    mensagem = db.Column(db.String(255), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Notificacao {self.tipo}: {self.mensagem[:30]}...>"


# ═══════════════════════════════════════════════════════
# MODELO: categoria — categorização automática (rf06)
# ═══════════════════════════════════════════════════════
class CategoriaModel(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    cor = db.Column(db.String(7), default='#6b7280')  # hex color
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    # relacionamento com palavras-chave — cascade deleta as palavras junto
    palavras_chave = db.relationship('PalavraChaveModel', backref='categoria', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Categoria {self.nome}>"


# ═══════════════════════════════════════════════════════
# MODELO: palavra-chave — match automático em transações
# ═══════════════════════════════════════════════════════
class PalavraChaveModel(db.Model):
    __tablename__ = 'palavras_chave'

    id = db.Column(db.Integer, primary_key=True)
    palavra = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

    def __repr__(self):
        return f"<Palavra {self.palavra} → {self.categoria.nome}>"


# função pra inicializar banco de dados
def init_db(app):
    """cria todas as tabelas automaticamente no startup"""
    with app.app_context():
        db.create_all()
        print("✓ banco de dados inicializado")
        
        # popula categorias padrão se o banco estiver vazio
        if CategoriaModel.query.first() is None:
            categorias_padrao = {
                'alimentacao': ['supermercado', 'ifood', 'restaurante', 'lanche', 'padaria'],
                'transporte': ['uber', '99', 'gasolina', 'posto', 'onibus'],
                'moradia': ['aluguel', 'condominio', 'luz', 'agua', 'internet', 'gas'],
                'saude': ['farmacia', 'medico', 'consulta', 'hospital', 'academia'],
                'lazer': ['netflix', 'spotify', 'cinema', 'show', 'hotel'],
                'educacao': ['udemy', 'curso', 'livro', 'faculdade', 'mensalidade'],
                'salario': ['salario', 'salário', 'pagamento mensal'],
                'freelance': ['freelance', 'freela', 'projeto'],
                'investimento': ['cdb', 'rendimento', 'dividendo', 'juros'],
                'outros': [],
            }
            
            cores_categoria = {
                'alimentacao': '#f59e0b', 'transporte': '#3b82f6', 'moradia': '#ef4444',
                'saude': '#10b981', 'lazer': '#8b5cf6', 'educacao': '#06b6d4',
                'salario': '#22c55e', 'freelance': '#ec4899', 'investimento': '#f97316', 'outros': '#6b7280'
            }
            
            for nome, palavras in categorias_padrao.items():
                # cria categoria
                categoria = CategoriaModel(
                    nome=nome,
                    cor=cores_categoria.get(nome, '#6b7280')
                )
                db.session.add(categoria)
                db.session.flush()  # garante que tem id
                
                # adiciona palavras-chave
                for palavra in palavras:
                    palavra_chave = PalavraChaveModel(
                        palavra=palavra.lower(),
                        categoria_id=categoria.id
                    )
                    db.session.add(palavra_chave)
            
            db.session.commit()
            print("✓ categorias padrão populadas")
