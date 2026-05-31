# backend/routes/api/transacoes.py

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from ...database import db, ContaModel, ReceitaModel, DespesaModel, PalavraChaveModel

# ─────────────────────────────────────────────────────────
# blueprint WEB — mantém o prefixo /transacoes
# ─────────────────────────────────────────────────────────
bp = Blueprint('transacoes', __name__, url_prefix='/transacoes')


# ═══════════════════════════════════════════════════════
# FUNÇÃO AUXILIAR: CATEGORIZAÇÃO AUTOMÁTICA (RF06)
# ═══════════════════════════════════════════════════════

def categorizar_transacao(descricao, tipo=None):
    desc_lower = descricao.lower()
    palavras = PalavraChaveModel.query.all()
    for p in palavras:
        if p.palavra in desc_lower:
            return p.categoria.nome
    return 'outros'


# ═══════════════════════════════════════════════════════
# ROTAS WEB
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def listar_transacoes():
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    if not conta:
        return redirect(url_for('dashboard.dashboard'))

    filtro_status = request.args.get('status', 'ativa')
    receitas = ReceitaModel.query.filter_by(conta_id=conta.id, status=filtro_status).order_by(ReceitaModel.data.desc()).all()
    despesas = DespesaModel.query.filter_by(conta_id=conta.id, status=filtro_status).order_by(DespesaModel.data.desc()).all()
    transacoes = sorted(receitas + despesas, key=lambda t: t.data, reverse=True)

    return render_template('transacoes.html', transacoes=transacoes, status_filtro=filtro_status, conta=conta)


@bp.route('/adicionar/<tipo>', methods=['POST'])
def adicionar_transacao(tipo):
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    descricao = request.form.get('descricao')
    valor = float(request.form.get('valor', 0))

    if tipo == 'receita':
        transacao = ReceitaModel(
            descricao=descricao,
            valor=valor,
            categoria=categorizar_transacao(descricao),
            conta_id=conta.id
        )
    elif tipo == 'despesa':
        transacao = DespesaModel(
            descricao=descricao,
            valor=valor,
            categoria=categorizar_transacao(descricao),
            conta_id=conta.id
        )
    else:
        return redirect(url_for('transacoes.listar_transacoes'))

    db.session.add(transacao)
    db.session.commit()
    return redirect(url_for('transacoes.listar_transacoes'))


@bp.route('/lixeira/<int:id>/<acao>', methods=['POST'])
def gerenciar_lixeira(id, acao):
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    transacao = ReceitaModel.query.filter_by(id=id, conta_id=conta.id).first()
    if not transacao:
        transacao = DespesaModel.query.filter_by(id=id, conta_id=conta.id).first()

    if transacao:
        if acao == 'descartar':
            transacao.status = 'descartada'
            db.session.commit()
            return redirect(url_for('transacoes.listar_transacoes', status='ativa'))
        elif acao == 'restaurar':
            transacao.status = 'ativa'
            db.session.commit()
            return redirect(url_for('transacoes.listar_transacoes', status='descartada'))
        elif acao == 'deletar':
            db.session.delete(transacao)
            db.session.commit()
            return redirect(url_for('transacoes.listar_transacoes', status='descartada'))

    return redirect(url_for('transacoes.listar_transacoes'))


@bp.route('/editar/<int:id>', methods=['POST'])
def editar_transacao(id):
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    transacao = ReceitaModel.query.filter_by(id=id, conta_id=conta.id).first()
    if not transacao:
        transacao = DespesaModel.query.filter_by(id=id, conta_id=conta.id).first()

    if transacao:
        transacao.valor = float(request.form.get('valor', transacao.valor))
        transacao.descricao = request.form.get('descricao', transacao.descricao)
        nova_categoria = request.form.get('categoria', '')
        transacao.categoria = nova_categoria if nova_categoria else categorizar_transacao(transacao.descricao)
        db.session.commit()

    return redirect(url_for('transacoes.listar_transacoes'))


# ─────────────────────────────────────────────────────────
# blueprint API — sem prefixo, rotas em /api/transacoes
# ─────────────────────────────────────────────────────────
bp_api = Blueprint('api_transacoes', __name__)


@bp_api.route('/api/transacoes', methods=['GET'])
def api_listar_transacoes():
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    if not conta:
        return jsonify({'erro': 'conta não encontrada'}), 404

    status = request.args.get('status', 'ativa')
    receitas = ReceitaModel.query.filter_by(conta_id=conta.id, status=status).all()
    despesas = DespesaModel.query.filter_by(conta_id=conta.id, status=status).all()
    transacoes = sorted(receitas + despesas, key=lambda t: t.data, reverse=True)

    return jsonify({
        'transacoes': [
            {
                'id': t.id,
                'tipo': t.tipo,
                'descricao': t.descricao,
                'valor': float(t.valor),
                'categoria': t.categoria,
                'data': t.data.strftime('%Y-%m-%d'),
                'status': t.status,
                'eh_parcelada': t.eh_parcelada,
            }
            for t in transacoes
        ]
    })


@bp_api.route('/api/transacoes/<tipo>', methods=['POST'])
def api_adicionar_transacao(tipo):
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    if not conta:
        return jsonify({'erro': 'conta não encontrada'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'erro': 'JSON inválido'}), 400

    descricao = data.get('descricao', '').strip()
    valor = float(data.get('valor', 0))

    if not descricao or valor <= 0:
        return jsonify({'erro': 'descricao e valor são obrigatórios'}), 400

    categoria = categorizar_transacao(descricao)

    if tipo == 'receita':
        tx = ReceitaModel(descricao=descricao, valor=valor, categoria=categoria, conta_id=conta.id)
    elif tipo == 'despesa':
        tx = DespesaModel(descricao=descricao, valor=valor, categoria=categoria, conta_id=conta.id)
    else:
        return jsonify({'erro': 'tipo inválido — use receita ou despesa'}), 400

    db.session.add(tx)
    db.session.commit()
    return jsonify({'sucesso': True, 'id': tx.id, 'categoria': categoria}), 201


@bp_api.route('/api/transacoes/<int:id>/descartar', methods=['POST'])
def api_descartar_transacao(id):
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    tx = ReceitaModel.query.filter_by(id=id, conta_id=conta.id).first()
    if not tx:
        tx = DespesaModel.query.filter_by(id=id, conta_id=conta.id).first()
    if not tx:
        return jsonify({'erro': 'transação não encontrada'}), 404

    tx.status = 'descartada'
    db.session.commit()
    return jsonify({'sucesso': True})


@bp_api.route('/api/transacoes/<int:id>/restaurar', methods=['POST'])
def api_restaurar_transacao(id):
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    tx = ReceitaModel.query.filter_by(id=id, conta_id=conta.id).first()
    if not tx:
        tx = DespesaModel.query.filter_by(id=id, conta_id=conta.id).first()
    if not tx:
        return jsonify({'erro': 'transação não encontrada'}), 404

    tx.status = 'ativa'
    db.session.commit()
    return jsonify({'sucesso': True})