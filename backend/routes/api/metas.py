# backend/routes/api/metas.py

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from datetime import datetime
from ...database import db, UsuarioModel, MetaModel

# ─────────────────────────────────────────────────────────
# blueprint WEB — prefixo /metas
# ─────────────────────────────────────────────────────────
bp = Blueprint('metas', __name__, url_prefix='/metas')


# ═══════════════════════════════════════════════════════
# ROTAS WEB
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def listar_metas():
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    usuario = UsuarioModel.query.get(usuario_id)
    metas_ativas = MetaModel.query.filter_by(usuario_id=usuario_id, ativa=True).order_by(MetaModel.data_criacao.desc()).all()
    metas_concluidas = MetaModel.query.filter_by(usuario_id=usuario_id, ativa=False).order_by(MetaModel.data_criacao.desc()).all()

    return render_template('metas.html', metas_ativas=metas_ativas, metas_concluidas=metas_concluidas, usuario=usuario)


@bp.route('/criar', methods=['POST'])
def criar_meta():
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    descricao = request.form.get('descricao', '').strip()
    valor_alvo = float(request.form.get('valor_alvo', 0))

    if not descricao or valor_alvo <= 0:
        return redirect(url_for('metas.listar_metas'))

    data_prazo = None
    data_prazo_str = request.form.get('data_prazo')
    if data_prazo_str:
        try:
            data_prazo = datetime.strptime(data_prazo_str, '%Y-%m-%d')
        except ValueError:
            pass

    meta = MetaModel(
        usuario_id=usuario_id,
        descricao=descricao,
        valor_alvo=valor_alvo,
        valor_acumulado=0,
        data_prazo=data_prazo,
        ativa=True
    )
    db.session.add(meta)
    db.session.commit()
    return redirect(url_for('metas.listar_metas'))


@bp.route('/atualizar/<int:id>', methods=['POST'])
def atualizar_meta(id):
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    meta = MetaModel.query.filter_by(id=id, usuario_id=session['usuario_id']).first()
    if meta:
        novo_acumulado = float(request.form.get('valor_acumulado', meta.valor_acumulado))
        meta.valor_acumulado = min(novo_acumulado, meta.valor_alvo)
        if meta.valor_acumulado >= meta.valor_alvo:
            meta.ativa = False
        db.session.commit()

    return redirect(url_for('metas.listar_metas'))


@bp.route('/deletar/<int:id>', methods=['POST'])
def deletar_meta(id):
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    meta = MetaModel.query.filter_by(id=id, usuario_id=session['usuario_id']).first()
    if meta:
        db.session.delete(meta)
        db.session.commit()

    return redirect(url_for('metas.listar_metas'))


@bp.route('/resetar/<int:id>', methods=['POST'])
def resetar_meta(id):
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    meta = MetaModel.query.filter_by(id=id, usuario_id=session['usuario_id']).first()
    if meta:
        meta.valor_acumulado = 0
        meta.ativa = True
        db.session.commit()

    return redirect(url_for('metas.listar_metas'))


# ─────────────────────────────────────────────────────────
# blueprint API — sem prefixo, rotas em /api/metas
# ─────────────────────────────────────────────────────────
bp_api = Blueprint('api_metas', __name__)


@bp_api.route('/api/metas', methods=['GET'])
def api_listar_metas():
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    metas = MetaModel.query.filter_by(usuario_id=usuario_id).order_by(MetaModel.data_criacao.desc()).all()

    return jsonify({
        'metas': [
            {
                'id': m.id,
                'descricao': m.descricao,
                'valor_alvo': float(m.valor_alvo),
                'valor_acumulado': float(m.valor_acumulado),
                'valor_restante': float(m.valor_restante),
                'progresso': round(m.percentual_progresso, 1),
                'ativa': m.ativa,
                'data_prazo': m.data_prazo.strftime('%Y-%m-%d') if m.data_prazo else None,
                'data_criacao': m.data_criacao.strftime('%Y-%m-%d'),
            }
            for m in metas
        ]
    })


@bp_api.route('/api/metas', methods=['POST'])
def api_criar_meta():
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'erro': 'JSON inválido'}), 400

    descricao = data.get('descricao', '').strip()
    valor_alvo = float(data.get('valor_alvo', 0))

    if not descricao or valor_alvo <= 0:
        return jsonify({'erro': 'dados inválidos'}), 400

    data_prazo = None
    data_prazo_str = data.get('data_prazo')
    if data_prazo_str:
        try:
            data_prazo = datetime.strptime(data_prazo_str, '%Y-%m-%d')
        except ValueError:
            pass

    meta = MetaModel(
        usuario_id=int(usuario_id),
        descricao=descricao,
        valor_alvo=valor_alvo,
        valor_acumulado=0,
        data_prazo=data_prazo,
        ativa=True
    )
    db.session.add(meta)
    db.session.commit()
    return jsonify({'sucesso': True, 'id': meta.id}), 201


@bp_api.route('/api/metas/<int:id>/deletar', methods=['POST'])
def api_deletar_meta(id):
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    meta = MetaModel.query.filter_by(id=id, usuario_id=usuario_id).first()
    if not meta:
        return jsonify({'erro': 'meta não encontrada'}), 404

    db.session.delete(meta)
    db.session.commit()
    return jsonify({'sucesso': True})


@bp_api.route('/api/metas/<int:id>/atualizar', methods=['POST'])
def api_atualizar_meta(id):
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    meta = MetaModel.query.filter_by(id=id, usuario_id=usuario_id).first()
    if not meta:
        return jsonify({'erro': 'meta não encontrada'}), 404

    data = request.get_json()
    novo_acumulado = float(data.get('valor_acumulado', meta.valor_acumulado))
    meta.valor_acumulado = min(novo_acumulado, meta.valor_alvo)
    if meta.valor_acumulado >= meta.valor_alvo:
        meta.ativa = False

    db.session.commit()
    return jsonify({
        'sucesso': True,
        'progresso': round(meta.percentual_progresso, 1),
        'ativa': meta.ativa,
    })