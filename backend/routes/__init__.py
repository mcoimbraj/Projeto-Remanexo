from flask import Blueprint

from .api.dashboard import bp as dashboard_bp
from .api.transacoes import bp as transacoes_bp
from .api.metas import bp as metas_bp
from .api.nexo import bp as nexo_bp
from .api.categorias import bp as categorias_bp
from .api.parcelamentos import bp as parcelamentos_bp


def register_blueprints(app):
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transacoes_bp)
    app.register_blueprint(metas_bp)
    app.register_blueprint(nexo_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(parcelamentos_bp)
