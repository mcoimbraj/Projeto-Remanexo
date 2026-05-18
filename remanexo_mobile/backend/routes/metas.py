from flask import Blueprint, render_template, session, redirect, url_for, request
from datetime import datetime
from ..database import db, UsuarioModel, MetaModel

bp = Blueprint('metas', __name__, url_prefix='/metas')

# ═══════════════════════════════════════════════════════
# LISTAR METAS (RF05)
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def listar_metas():
    """
    rf05: lista metas com valor_alvo, valor_acumulado e barra de progresso.
    """
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    usuario = UsuarioModel.query.get(usuario_id)

    # busca metas ativas
    metas_ativas = MetaModel.query.filter_by(usuario_id=usuario_id, ativa=True).order_by(MetaModel.data_criacao.desc()).all()

    # busca metas concluídas
    metas_concluidas = MetaModel.query.filter_by(usuario_id=usuario_id, ativa=False).order_by(MetaModel.data_criacao.desc()).all()

    return render_template('metas.html', metas_ativas=metas_ativas, metas_concluidas=metas_concluidas, usuario=usuario)


# ═══════════════════════════════════════════════════════
# CRIAR META
# ═══════════════════════════════════════════════════════

@bp.route('/criar', methods=['POST'])
def criar_meta():
    """cria nova meta de economia"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']

    descricao = request.form.get('descricao', '').strip()
    valor_alvo = float(request.form.get('valor_alvo', 0))

    # validação basica
    if not descricao or valor_alvo <= 0:
        return redirect(url_for('metas.listar_metas'))

    data_prazo_str = request.form.get('data_prazo')
    data_prazo = None

    if data_prazo_str:
        try:
            data_prazo = datetime.strptime(data_prazo_str, '%Y-%m-%d')
        except ValueError:
            data_prazo = None

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


# ═══════════════════════════════════════════════════════
# ATUALIZAR PROGRESSO DA META
# ═══════════════════════════════════════════════════════

@bp.route('/atualizar/<int:id>', methods=['POST'])
def atualizar_meta(id):
    """
    atualiza o valor acumulado de uma meta.
    a barra de progresso recalcula automaticamente (rf05)
    """
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    meta = MetaModel.query.filter_by(id=id, usuario_id=usuario_id).first()

    if meta:
        novo_acumulado = float(request.form.get('valor_acumulado', meta.valor_acumulado))
        meta.valor_acumulado = min(novo_acumulado, meta.valor_alvo)

        # marca como concluída se atingiu meta
        if meta.valor_acumulado >= meta.valor_alvo:
            meta.ativa = False

        db.session.commit()

    return redirect(url_for('metas.listar_metas'))


# ═══════════════════════════════════════════════════════
# DELETAR META
# ═══════════════════════════════════════════════════════

@bp.route('/deletar/<int:id>', methods=['POST'])
def deletar_meta(id):
    """deleta uma meta"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    meta = MetaModel.query.filter_by(id=id, usuario_id=usuario_id).first()

    if meta:
        db.session.delete(meta)
        db.session.commit()

    return redirect(url_for('metas.listar_metas'))


# ═══════════════════════════════════════════════════════
# RESESTAR META (voltar a zero)
# ═══════════════════════════════════════════════════════

@bp.route('/resetar/<int:id>', methods=['POST'])
def resetar_meta(id):
    """reseta o valor acumulado de uma meta e a ativa novamente"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    meta = MetaModel.query.filter_by(id=id, usuario_id=usuario_id).first()

    if meta:
        meta.valor_acumulado = 0
        meta.ativa = True
        db.session.commit()

    return redirect(url_for('metas.listar_metas'))
