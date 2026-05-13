# init routes
from flask import Blueprint
from .dashboard import bp as dashboard_bp
from .transacoes import bp as transacoes_bp
from .metas import bp as metas_bp
from .nexo import bp as nexo_bp
from .categorias import bp as categorias_bp
from .parcelamentos import bp as parcelamentos_bp

def register_blueprints(app):
    """registra todos os blueprints da aplicação"""
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transacoes_bp)
    app.register_blueprint(metas_bp)
    app.register_blueprint(nexo_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(parcelamentos_bp)
