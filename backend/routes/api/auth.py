from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from ...database import UsuarioModel

bp = Blueprint("api_auth", __name__)


@bp.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "erro": "JSON inválido"
        }), 400

    email = data.get("email")
    senha = data.get("senha")

    if not email or not senha:
        return jsonify({
            "erro": "Email e senha são obrigatórios"
        }), 400

    usuario = UsuarioModel.query.filter_by(email=email).first()

    if not usuario:
        return jsonify({
            "erro": "Usuário não encontrado"
        }), 401

    if not check_password_hash(usuario.senha_hash, senha):
        return jsonify({
            "erro": "Senha inválida"
        }), 401

    return jsonify({
        "sucesso": True,
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email
        }
    }), 200