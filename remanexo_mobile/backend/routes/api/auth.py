from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from backend.database import UsuarioModel

bp = Blueprint("api_auth", __name__)

@bp.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    senha = data.get("senha")

    usuario = UsuarioModel.query.filter_by(email=email).first()

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 401

    if not check_password_hash(usuario.senha_hash, senha):
        return jsonify({"erro": "Senha inválida"}), 401

    return jsonify({
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email
    })