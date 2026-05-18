from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from datetime import datetime, timedelta
from ..database import db, ContaModel, TransacaoModel, ReceitaModel, DespesaModel, ParcelaModel

bp = Blueprint('parcelamentos', __name__, url_prefix='/parcelamentos')

# ═══════════════════════════════════════════════════════
# LISTAR PARCELAMENTOS
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def listar_parcelamentos():
    """lista todas as transações parceladas com suas parcelas (rf08)"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    if not conta:
        return redirect(url_for('dashboard.dashboard'))

    # busca todas as transações parceladas (ativas)
    transacoes_parceladas = db.session.query(TransacaoModel).filter(
        TransacaoModel.conta_id == conta.id,
        TransacaoModel.eh_parcelada == True,
        TransacaoModel.status == 'ativa'
    ).order_by(TransacaoModel.data.desc()).all()

    return render_template('parcelamentos.html', transacoes_parceladas=transacoes_parceladas, conta=conta, now=datetime.now())


# ═══════════════════════════════════════════════════════
# CRIAR PARCELAMENTO
# ═══════════════════════════════════════════════════════

@bp.route('/criar', methods=['POST'])
def criar_parcelamento():
    """cria uma transação parcelada (rf08)"""
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
        # calcula valor por parcela
        valor_parcela = valor_total / num_parcelas

        # cria a transação parcelada com valor=0 (será atualizado quando marcada como paga)
        if tipo == 'receita':
            transacao = ReceitaModel(
                descricao=descricao,
                valor=0,  # valor não afeta saldo até ser pago
                categoria=categoria,
                conta_id=conta.id,
                eh_parcelada=True,
                num_parcelas=num_parcelas
            )
        else:
            transacao = DespesaModel(
                descricao=descricao,
                valor=0,  # valor não afeta saldo até ser pago
                categoria=categoria,
                conta_id=conta.id,
                eh_parcelada=True,
                num_parcelas=num_parcelas
            )

        db.session.add(transacao)
        db.session.flush()  # garante que tem ID

        # cria as parcelas
        for i in range(1, num_parcelas + 1):
            data_vencimento = data_primeira + timedelta(days=30 * (i - 1))
            
            parcela = ParcelaModel(
                transacao_id=transacao.id,
                numero=i,
                valor=valor_parcela,
                data_vencimento=data_vencimento,
                status='pendente'
            )
            db.session.add(parcela)

        db.session.commit()
        flash(f'✅ parcelamento criado: {num_parcelas}x', 'sucesso')
        return redirect(url_for('parcelamentos.listar_parcelamentos'))

    except Exception as e:
        flash(f'❌ erro ao criar parcelamento: {str(e)}', 'erro')
        return redirect(url_for('parcelamentos.listar_parcelamentos'))


# ═══════════════════════════════════════════════════════
# MARCAR PARCELA COMO PAGA
# ═══════════════════════════════════════════════════════

@bp.route('/parcela/<int:parcela_id>/pagar', methods=['POST'])
def pagar_parcela(parcela_id):
    """marca uma parcela como paga e atualiza saldo (rf08)"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    parcela = ParcelaModel.query.get(parcela_id)
    if not parcela:
        flash('❌ parcela não encontrada', 'erro')
        return redirect(url_for('parcelamentos.listar_parcelamentos'))

    # atualiza transação com valor da parcela
    transacao = parcela.transacao
    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    if transacao and transacao.conta_id == conta.id:
        # adiciona valor da parcela à transação
        transacao.valor += parcela.valor

        # marca parcela como paga
        parcela.status = 'paga'
        parcela.data_pagamento = datetime.now()
        db.session.commit()

        acao = 'recebida' if transacao.tipo == 'receita' else 'paga'
        flash(f'✅ parcela {parcela.numero} {acao}', 'sucesso')
    else:
        flash('❌ erro ao atualizar parcela', 'erro')

    return redirect(url_for('parcelamentos.listar_parcelamentos'))


# ═══════════════════════════════════════════════════════
# MARCAR PARCELA COMO DESCARTADA
# ═══════════════════════════════════════════════════════

@bp.route('/parcela/<int:parcela_id>/descartar', methods=['POST'])
def descartar_parcela(parcela_id):
    """marca uma parcela como descartada (não será paga — rf08)"""
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


# ═══════════════════════════════════════════════════════
# DELETAR PARCELAMENTO INTEIRO
# ═══════════════════════════════════════════════════════

@bp.route('/deletar/<int:transacao_id>', methods=['POST'])
def deletar_parcelamento(transacao_id):
    """deleta um parcelamento inteiro (todas as parcelas)"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    transacao = ReceitaModel.query.filter_by(id=transacao_id, conta_id=conta.id).first()
    if not transacao:
        transacao = DespesaModel.query.filter_by(id=transacao_id, conta_id=conta.id).first()

    if transacao and transacao.eh_parcelada:
        db.session.delete(transacao)  # cascade deleta as parcelas
        db.session.commit()
        flash(f'✅ parcelamento deletado', 'sucesso')
    else:
        flash('❌ parcelamento não encontrado', 'erro')

    return redirect(url_for('parcelamentos.listar_parcelamentos'))
