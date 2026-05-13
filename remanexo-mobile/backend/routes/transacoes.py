from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from datetime import datetime
from ..database import db, ContaModel, ReceitaModel, DespesaModel, PalavraChaveModel

bp = Blueprint('transacoes', __name__, url_prefix='/transacoes')

# ═══════════════════════════════════════════════════════
# LISTAR TRANSAÇÕES
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def listar_transacoes():
    """lista todas as transações da conta (com filtro de lixeira)"""
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    if not conta:
        return redirect(url_for('dashboard.dashboard'))

    # filtra por status (ativa ou lixeira)
    filtro_status = request.args.get('status', 'ativa')

    # busca receitas e despesas
    receitas = ReceitaModel.query.filter_by(conta_id=conta.id, status=filtro_status).order_by(ReceitaModel.data.desc()).all()
    despesas = DespesaModel.query.filter_by(conta_id=conta.id, status=filtro_status).order_by(DespesaModel.data.desc()).all()

    # combina e ordena por data
    transacoes = sorted(receitas + despesas, key=lambda t: t.data, reverse=True)

    return render_template('transacoes.html', transacoes=transacoes, status_filtro=filtro_status, conta=conta)


# ═══════════════════════════════════════════════════════
# ADICIONAR RECEITA / DESPESA
# ═══════════════════════════════════════════════════════

@bp.route('/adicionar/<tipo>', methods=['POST'])
def adicionar_transacao(tipo):
    """
    adiciona receita ou despesa.
    rf06: categorização automática por palavras-chave (polimorfismo em ação)
    """
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    descricao = request.form.get('descricao')
    valor = float(request.form.get('valor', 0))
    categoria = request.form.get('categoria', 'geral')

    if tipo == 'receita':
        transacao = ReceitaModel(
            tipo='receita',
            descricao=descricao,
            valor=valor,
            categoria=categoria,
            conta_id=conta.id
        )
        # categorização automática (rf06)
        transacao.categoria = categorizar_transacao(descricao, 'receita')
    elif tipo == 'despesa':
        transacao = DespesaModel(
            tipo='despesa',
            descricao=descricao,
            valor=valor,
            categoria=categoria,
            conta_id=conta.id
        )
        # categorização automática (rf06)
        transacao.categoria = categorizar_transacao(descricao, 'despesa')
    else:
        return redirect(url_for('transacoes.listar_transacoes'))

    db.session.add(transacao)
    db.session.commit()

    return redirect(url_for('transacoes.listar_transacoes'))


# ═══════════════════════════════════════════════════════
# MOVER PARA LIXEIRA / RESTAURAR (RF04)
# ═══════════════════════════════════════════════════════

@bp.route('/lixeira/<int:id>/<acao>', methods=['POST'])
def gerenciar_lixeira(id, acao):
    """
    move transação pra lixeira, restaura ou deleta permanentemente (rf04).
    transações na lixeira não somam no saldo
    """
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    # busca a transação (pode ser receita ou despesa)
    transacao = ReceitaModel.query.filter_by(id=id, conta_id=conta.id).first()
    if not transacao:
        transacao = DespesaModel.query.filter_by(id=id, conta_id=conta.id).first()

    if transacao:
        if acao == 'descartar':
            # move pra lixeira
            transacao.status = 'descartada'
            db.session.commit()
            return redirect(url_for('transacoes.listar_transacoes', status='ativa'))
        
        elif acao == 'restaurar':
            # volta pra ativa
            transacao.status = 'ativa'
            db.session.commit()
            return redirect(url_for('transacoes.listar_transacoes', status='descartada'))
        
        elif acao == 'deletar':
            # deleta de vez — sem volta
            db.session.delete(transacao)
            db.session.commit()
            return redirect(url_for('transacoes.listar_transacoes', status='descartada'))

    return redirect(url_for('transacoes.listar_transacoes'))



# ═══════════════════════════════════════════════════════
# EDIÇÃO / CONCILIAÇÃO MANUAL (RF10)
# ═══════════════════════════════════════════════════════

@bp.route('/editar/<int:id>', methods=['POST'])
def editar_transacao(id):
    """
    rf10: conciliação manual — usuário pode editar valor de transações
    sem integração API (polimorfismo também trabalha aqui)
    """
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    # busca a transação
    transacao = ReceitaModel.query.filter_by(id=id, conta_id=conta.id).first()
    if not transacao:
        transacao = DespesaModel.query.filter_by(id=id, conta_id=conta.id).first()

    if transacao:
        novo_valor = float(request.form.get('valor', transacao.valor))
        nova_descricao = request.form.get('descricao', transacao.descricao)
        nova_categoria = request.form.get('categoria', '')

        transacao.valor = novo_valor
        transacao.descricao = nova_descricao
        # recategoriza após editar descricao, ou usa categoria manual se fornecida
        transacao.categoria = nova_categoria if nova_categoria else categorizar_transacao(nova_descricao, transacao.tipo)

        db.session.commit()

    return redirect(url_for('transacoes.listar_transacoes'))


# ═══════════════════════════════════════════════════════
# FUNÇÃO AUXILIAR: CATEGORIZAÇÃO AUTOMÁTICA (RF06)
# ═══════════════════════════════════════════════════════

def categorizar_transacao(descricao, tipo):
    """
    rf06: categorização automática por palavras-chave — agora busca do banco.
    # agora busca do banco — qualquer palavra nova cadastrada na tela já vale
    # na próxima transação, sem mexer no código
    """
    desc_lower = descricao.lower()
    
    # busca todas as palavras-chave do banco
    palavras = PalavraChaveModel.query.all()
    
    for p in palavras:
        if p.palavra in desc_lower:
            return p.categoria.nome
    
    # fallback: retorna 'outros' se nenhuma palavra bater
    return 'outros'
