"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🎯 REMANEXO - SISTEMA FINANCEIRO COM POO              ║
║                                                               ║
║  Desenvolvido com Flask e SQLite usando os 4 pilares da POO: ║
║  ✓ ABSTRAÇÃO (classe abstrata Transacao)                     ║
║  ✓ HERANÇA (Receita e Despesa herdam de Transacao)           ║
║  ✓ ENCAPSULAMENTO (atributos privados em Conta)              ║
║  ✓ POLIMORFISMO (EstadoNexo e padrão State)                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

from flask import Flask, render_template
from flask_session import Session
from datetime import timedelta
from .database import db, init_db
from .routes import register_blueprints

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÃO DA APLICAÇÃO
# ═══════════════════════════════════════════════════════

def create_app():
    """factory function — cria e configura a app flask"""

    app = Flask(__name__, template_folder='templates', static_folder='static')

    # ═ CONFIGURAÇÕES BÁSICAS ═
    app.config['SECRET_KEY'] = 'remanexo-secret-key-2026'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///remanexo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    # ═ INICIALIZAR EXTENSÕES ═
    db.init_app(app)
    Session(app)

    # ═ REGISTRAR BLUEPRINTS (ROTAS) ═
    register_blueprints(app)

    # ═ CRIAR TABELAS NO STARTUP ═
    with app.app_context():
        db.create_all()
        # cria usuário demo se não existir
        criar_usuario_demo()
        # cria categorias padrão se não existirem
        criar_categorias_padrao()

    # ═ TRATAMENTO DE ERROS ═
    @app.errorhandler(404)
    def pagina_nao_encontrada(erro):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def erro_interno(erro):
        return render_template('500.html'), 500

    return app


# ═══════════════════════════════════════════════════════
# CRIAR USUÁRIO DEMO
# ═══════════════════════════════════════════════════════

def criar_usuario_demo():
    """cria usuário demo pra testes (se não existir)"""
    from .database import UsuarioModel, ContaModel, AssinaturaModel, NexoModel

    usuario_demo = UsuarioModel.query.filter_by(email='demo@remanexo.com').first()

    if not usuario_demo:
        usuario_demo = UsuarioModel(
            nome='Usuário Demo',
            email='demo@remanexo.com'
        )
        usuario_demo.definir_senha('123456')

        db.session.add(usuario_demo)
        db.session.commit()

        # cria conta demo
        conta_demo = ContaModel(
            numero_conta=f"RMX{usuario_demo.id:06d}",
            usuario_id=usuario_demo.id,
            saldo=5000.00
        )

        # cria assinatura demo
        assinatura_demo = AssinaturaModel(
            usuario_id=usuario_demo.id,
            tipo='premium'
        )

        # cria nexo demo
        nexo_demo = NexoModel(
            usuario_id=usuario_demo.id,
            estado='ativo'
        )

        db.session.add(conta_demo)
        db.session.add(assinatura_demo)
        db.session.add(nexo_demo)
        db.session.commit()

        print("✓ usuário demo criado com sucesso")
    else:
        print("✓ usuário demo já existe")


# ═══════════════════════════════════════════════════════
# CRIAR CATEGORIAS PADRÃO
# ═══════════════════════════════════════════════════════

def criar_categorias_padrao():
    """cria 10 categorias padrão com palavras-chave if não existirem"""
    from .database import CategoriaModel, PalavraChaveModel

    # lista de categorias padrão com cores e palavras-chave
    categorias_padrao = {
        'alimentação': {
            'cor': '#ef4444',  # red
            'palavras': ['comida', 'mercado', 'restaurante', 'café', 'lanchonete', 'padaria']
        },
        'transporte': {
            'cor': '#f97316',  # orange
            'palavras': ['uber', 'táxi', 'ônibus', 'gasolina', 'combustível', 'estacionamento']
        },
        'moradia': {
            'cor': '#eab308',  # yellow
            'palavras': ['aluguel', 'condomínio', 'água', 'luz', 'gás', 'internet']
        },
        'saúde': {
            'cor': '#22c55e',  # green
            'palavras': ['farmácia', 'médico', 'dentista', 'hospital', 'academia', 'saúde']
        },
        'lazer': {
            'cor': '#06b6d4',  # cyan
            'palavras': ['cinema', 'show', 'jogo', 'viagem', 'passeio', 'diversão']
        },
        'educação': {
            'cor': '#3b82f6',  # blue
            'palavras': ['escola', 'curso', 'livro', 'aula', 'treinamento', 'faculdade']
        },
        'salário': {
            'cor': '#8b5cf6',  # purple
            'palavras': ['salário', 'recebimento', 'pagamento', 'renda', 'vencimento']
        },
        'freelance': {
            'cor': '#ec4899',  # pink
            'palavras': ['freelance', 'projeto', 'consultoria', 'serviço', 'trabalho']
        },
        'investimento': {
            'cor': '#06b6d4',  # teal
            'palavras': ['investimento', 'ações', 'cripto', 'fundo', 'taxa', 'bolsa']
        },
        'outros': {
            'cor': '#6b7280',  # gray
            'palavras': ['outro', 'diversos', 'miscellaneous']
        }
    }

    for nome, config in categorias_padrao.items():
        # verifica se categoria já existe
        if not CategoriaModel.query.filter_by(nome=nome).first():
            categoria = CategoriaModel(
                nome=nome,
                cor=config['cor']
            )
            db.session.add(categoria)
            db.session.commit()

            # adiciona palavras-chave à categoria
            for palavra in config['palavras']:
                palavra_chave = PalavraChaveModel(
                    palavra=palavra,
                    categoria_id=categoria.id
                )
                db.session.add(palavra_chave)

            db.session.commit()

    print("✓ categorias padrão carregadas")


# ═══════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ═══════════════════════════════════════════════════════

if __name__ == '__main__':
    app = create_app()

    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                   🚀 REMANEXO INICIANDO                       ║
    ║                                                               ║
    ║  Acesse: http://localhost:5000                               ║
    ║                                                               ║
    ║  Demo:                                                        ║
    ║  • Email: demo@remanexo.com                                   ║
    ║  • Senha: 123456                                              ║
    ║                                                               ║
    ║  Conceitos POO Demonstrados:                                  ║
    ║  ✓ Classe Abstrata (Transacao)                               ║
    ║  ✓ Herança (Receita + Despesa → Transacao)                  ║
    ║  ✓ Encapsulamento (Conta com getters/setters)               ║
    ║  ✓ Polimorfismo (Padrão State - Nexo)                       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    # roda o servidor
    app.run(debug=True, host='localhost', port=5000)
