# backend/routes/api/parcelamentos.py

from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from datetime import datetime, timedelta
from ...database import db, ContaModel, TransacaoModel, ReceitaModel, DespesaModel, ParcelaModel

# ─────────────────────────────────────────────────────────
# blueprint WEB — prefixo /parcelamentos
# ─────────────────────────────────────────────────────────
bp = Blueprint('parcelamentos', __name__, url_prefix='/parcelamentos')


# ═══════════════════════════════════════════════════════
# ROTAS WEB
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def listar_parcelamentos():
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    if not conta:
        return redirect(url_for('dashboard.dashboard'))

    transacoes_parceladas = db.session.query(TransacaoModel).filter(
        TransacaoModel.conta_id == conta.id,
        TransacaoModel.eh_parcelada == True,
        TransacaoModel.status == 'ativa'
    ).order_by(TransacaoModel.data.desc()).all()

    return render_template(
        'parcelamentos.html',
        transacoes_parceladas=transacoes_parceladas,
        conta=conta,
        now=datetime.now()
    )


@bp.route('/criar', methods=['POST'])
def criar_parcelamento():
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    descricao = request.form.get('descricao')
    valor_total = float(request.form.get('valor_total', 0))
    tipo = request.form.get('tipo')
    num_parcelas = int(request.form.get('num_parcelas', 1))
    data_primeira = datetime.strptime(request.form.get('data_primeira'), '%Y-%m-%d')
    categoria = request.form.get('categoria', 'geral')

    if not descricao or valor_total <= 0 or num_parcelas < 1:
        flash('❌ preencha os campos corretamente', 'erro')
        return redirect(url_for('parcelamentos.listar_parcelamentos'))

    try:
        valor_parcela = valor_total / num_parcelas

        if tipo == 'receita':
            transacao = ReceitaModel(
                descricao=descricao, valor=0,
                categoria=categoria, conta_id=conta.id,
                eh_parcelada=True, num_parcelas=num_parcelas
            )
        else:
            transacao = DespesaModel(
                descricao=descricao, valor=0,
                categoria=categoria, conta_id=conta.id,
                eh_parcelada=True, num_parcelas=num_parcelas
            )

        db.session.add(transacao)
        db.session.flush()

        for i in range(1, num_parcelas + 1):
            parcela = ParcelaModel(
                transacao_id=transacao.id,
                numero=i,
                valor=valor_parcela,
                data_vencimento=data_primeira + timedelta(days=30 * (i - 1)),
                status='pendente'
            )
            db.session.add(parcela)

        db.session.commit()
        flash(f'✅ parcelamento criado: {num_parcelas}x', 'sucesso')

    except Exception as e:
        flash(f'❌ erro ao criar parcelamento: {str(e)}', 'erro')

    return redirect(url_for('parcelamentos.listar_parcelamentos'))


@bp.route('/parcela/<int:parcela_id>/pagar', methods=['POST'])
def pagar_parcela(parcela_id):
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    parcela = ParcelaModel.query.get(parcela_id)
    if not parcela:
        flash('❌ parcela não encontrada', 'erro')
        return redirect(url_for('parcelamentos.listar_parcelamentos'))

    transacao = parcela.transacao
    conta = ContaModel.query.filter_by(usuario_id=session['usuario_id']).first()

    if transacao and transacao.conta_id == conta.id:
        transacao.valor += parcela.valor
        parcela.status = 'paga'
        parcela.data_pagamento = datetime.now()
        db.session.commit()
        acao = 'recebida' if transacao.tipo == 'receita' else 'paga'
        flash(f'✅ parcela {parcela.numero} {acao}', 'sucesso')
    else:
        flash('❌ erro ao atualizar parcela', 'erro')

    return redirect(url_for('parcelamentos.listar_parcelamentos'))


@bp.route('/parcela/<int:parcela_id>/descartar', methods=['POST'])
def descartar_parcela(parcela_id):
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    parcela = ParcelaModel.query.get(parcela_id)
    if not parcela:
        flash('❌ parcela não encontrada', 'erro')
        return redirect(url_for('parcelamentos.listar_parcelamentos'))

    parcela.status = 'descartada'
    db.session.commit()
    flash(f'✅ parcela {parcela.numero} descartada', 'sucesso')
    return redirect(url_for('parcelamentos.listar_parcelamentos'))


@bp.route('/deletar/<int:transacao_id>', methods=['POST'])
def deletar_parcelamento(transacao_id):
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    conta = ContaModel.query.filter_by(usuario_id=session['usuario_id']).first()

    transacao = ReceitaModel.query.filter_by(id=transacao_id, conta_id=conta.id).first()
    if not transacao:
        transacao = DespesaModel.query.filter_by(id=transacao_id, conta_id=conta.id).first()

    if transacao and transacao.eh_parcelada:
        db.session.delete(transacao)
        db.session.commit()
        flash('✅ parcelamento deletado', 'sucesso')
    else:
        flash('❌ parcelamento não encontrado', 'erro')

    return redirect(url_for('parcelamentos.listar_parcelamentos'))


# ─────────────────────────────────────────────────────────
# blueprint API — sem prefixo, rotas em /api/parcelamentos
# ─────────────────────────────────────────────────────────
bp_api = Blueprint('api_parcelamentos', __name__)


@bp_api.route('/api/parcelamentos', methods=['GET'])
def api_listar_parcelamentos():
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    if not conta:
        return jsonify({'erro': 'conta não encontrada'}), 404

    transacoes = db.session.query(TransacaoModel).filter(
        TransacaoModel.conta_id == conta.id,
        TransacaoModel.eh_parcelada == True,
        TransacaoModel.status == 'ativa'
    ).order_by(TransacaoModel.data.desc()).all()

    return jsonify({
        'parcelamentos': [
            {
                'id': t.id,
                'tipo': t.tipo,
                'descricao': t.descricao,
                'num_parcelas': t.num_parcelas,
                'parcelas': [
                    {
                        'id': p.id,
                        'numero': p.numero,
                        'valor': float(p.valor),
                        'status': p.status,
                        'data_vencimento': p.data_vencimento.strftime('%Y-%m-%d'),
                        'data_pagamento': p.data_pagamento.strftime('%Y-%m-%d') if p.data_pagamento else None,
                    }
                    for p in t.parcelas
                ],
            }
            for t in transacoes
        ]
    })


@bp_api.route('/api/parcelamentos', methods=['POST'])
def api_criar_parcelamento():
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
    valor_total = float(data.get('valor_total', 0))
    tipo = data.get('tipo', 'despesa')
    num_parcelas = int(data.get('num_parcelas', 1))
    categoria = data.get('categoria', 'geral')
    data_primeira_str = data.get('data_primeira')

    if not descricao or valor_total <= 0 or num_parcelas < 1:
        return jsonify({'erro': 'dados inválidos'}), 400

    try:
        data_primeira = datetime.strptime(data_primeira_str, '%Y-%m-%d') if data_primeira_str else datetime.now()
        valor_parcela = valor_total / num_parcelas

        if tipo == 'receita':
            transacao = ReceitaModel(
                descricao=descricao, valor=0,
                categoria=categoria, conta_id=conta.id,
                eh_parcelada=True, num_parcelas=num_parcelas
            )
        else:
            transacao = DespesaModel(
                descricao=descricao, valor=0,
                categoria=categoria, conta_id=conta.id,
                eh_parcelada=True, num_parcelas=num_parcelas
            )

        db.session.add(transacao)
        db.session.flush()

        for i in range(1, num_parcelas + 1):
            parcela = ParcelaModel(
                transacao_id=transacao.id,
                numero=i,
                valor=valor_parcela,
                data_vencimento=data_primeira + timedelta(days=30 * (i - 1)),
                status='pendente'
            )
            db.session.add(parcela)

        db.session.commit()
        return jsonify({'sucesso': True, 'id': transacao.id}), 201

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@bp_api.route('/api/parcelamentos/parcela/<int:parcela_id>/pagar', methods=['POST'])
def api_pagar_parcela(parcela_id):
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    parcela = ParcelaModel.query.get(parcela_id)

    if not parcela or parcela.transacao.conta_id != conta.id:
        return jsonify({'erro': 'parcela não encontrada'}), 404

    if parcela.status == 'paga':
        return jsonify({'erro': 'parcela já foi paga'}), 400

    parcela.transacao.valor += parcela.valor
    parcela.status = 'paga'
    parcela.data_pagamento = datetime.now()
    db.session.commit()

    return jsonify({'sucesso': True, 'parcela': parcela.numero})


@bp_api.route('/api/parcelamentos/<int:transacao_id>', methods=['DELETE'])
def api_deletar_parcelamento(transacao_id):
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    transacao = ReceitaModel.query.filter_by(id=transacao_id, conta_id=conta.id).first()
    if not transacao:
        transacao = DespesaModel.query.filter_by(id=transacao_id, conta_id=conta.id).first()

    if not transacao or not transacao.eh_parcelada:
        return jsonify({'erro': 'parcelamento não encontrado'}), 404

    db.session.delete(transacao)
    db.session.commit()
    return jsonify({'sucesso': True})