# backend/routes/api/dashboard.py

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime
from ...database import (
    db,
    UsuarioModel,
    ContaModel,
    ReceitaModel,
    DespesaModel,
    TransacaoModel,
    AssinaturaModel,
    NexoModel,
    NotificacaoModel
)

bp = Blueprint('dashboard', __name__, url_prefix='/')


# ═══════════════════════════════════════════════════════
# LOGIN / CADASTRO / LOGOUT (RF01)
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('dashboard.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        usuario = UsuarioModel.query.filter_by(email=email).first()

        if usuario and usuario.verificar_senha(senha):
            session['usuario_id'] = usuario.id
            session['nome_usuario'] = usuario.nome
            return redirect(url_for('dashboard.dashboard'))
        else:
            return render_template('login.html', erro='email ou senha inválidos')

    return render_template('login.html')


@bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if UsuarioModel.query.filter_by(email=email).first():
            return render_template('cadastro.html', erro='email já cadastrado')

        novo_usuario = UsuarioModel(nome=nome, email=email)
        novo_usuario.definir_senha(senha)
        db.session.add(novo_usuario)
        db.session.commit()

        conta = ContaModel(
            numero_conta=f"RMX{novo_usuario.id:06d}",
            usuario_id=novo_usuario.id,
            saldo=0
        )
        assinatura = AssinaturaModel(usuario_id=novo_usuario.id, tipo='gratuita')
        nexo = NexoModel(usuario_id=novo_usuario.id, estado='ativo')

        db.session.add(conta)
        db.session.add(assinatura)
        db.session.add(nexo)
        db.session.commit()

        session['usuario_id'] = novo_usuario.id
        session['nome_usuario'] = novo_usuario.nome
        return redirect(url_for('dashboard.dashboard'))

    return render_template('cadastro.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard.login'))


# ═══════════════════════════════════════════════════════
# DASHBOARD PRINCIPAL (RF03)
# ═══════════════════════════════════════════════════════

@bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    usuario = UsuarioModel.query.get(usuario_id)
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    if not conta:
        return redirect(url_for('dashboard.login'))

    todas_transacoes = db.session.query(TransacaoModel).filter(
        TransacaoModel.conta_id == conta.id
    ).all()

    saldo_total = 0
    for tx in todas_transacoes:
        if tx.status == 'ativa':
            saldo_total += tx.calcular_impacto_saldo()

    conta.saldo = saldo_total

    agora = datetime.now()
    inicio_mes = datetime(agora.year, agora.month, 1)
    fim_mes = datetime(agora.year, agora.month + 1, 1) if agora.month < 12 else datetime(agora.year + 1, 1, 1)

    receitas_mes = db.session.query(db.func.sum(ReceitaModel.valor)).filter(
        ReceitaModel.conta_id == conta.id,
        ReceitaModel.status == 'ativa',
        ReceitaModel.data >= inicio_mes,
        ReceitaModel.data < fim_mes
    ).scalar() or 0

    despesas_mes = db.session.query(db.func.sum(DespesaModel.valor)).filter(
        DespesaModel.conta_id == conta.id,
        DespesaModel.status == 'ativa',
        DespesaModel.data >= inicio_mes,
        DespesaModel.data < fim_mes
    ).scalar() or 0

    percentual_gasto = (despesas_mes / receitas_mes * 100) if receitas_mes > 0 else 0
    alerta_gasto = percentual_gasto > 80
    assinatura = AssinaturaModel.query.filter_by(usuario_id=usuario_id).first()
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()
    notificacoes = NotificacaoModel.query.filter_by(usuario_id=usuario_id, lida=False).all()

    return render_template('dashboard.html', **{
        'usuario': usuario,
        'conta': conta,
        'saldo_total': saldo_total,
        'receitas_mes': receitas_mes,
        'despesas_mes': despesas_mes,
        'percentual_gasto': percentual_gasto,
        'alerta_gasto': alerta_gasto,
        'assinatura': assinatura,
        'nexo': nexo,
        'notificacoes': notificacoes,
    })


# ═══════════════════════════════════════════════════════
# MINHA CONTA
# ═══════════════════════════════════════════════════════

@bp.route('/conta', methods=['GET'])
def minha_conta():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('dashboard.login'))

    usuario = UsuarioModel.query.get(usuario_id)
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    assinatura = AssinaturaModel.query.filter_by(usuario_id=usuario_id).first()
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()

    total_transacoes = (
        ReceitaModel.query.filter_by(conta_id=conta.id).count() +
        DespesaModel.query.filter_by(conta_id=conta.id).count()
    )

    return render_template('conta.html', **{
        'usuario': usuario,
        'conta': conta,
        'assinatura': assinatura,
        'nexo': nexo,
        'total_transacoes': total_transacoes,
        'total_metas': 0,
        'metas_concluidas': 0,
        'now': datetime.now(),
    })


@bp.route('/conta/atualizar', methods=['POST'])
def atualizar_conta():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('dashboard.login'))

    usuario = UsuarioModel.query.get(usuario_id)
    nome = request.form.get('nome')

    if not nome or len(nome.strip()) < 3:
        return redirect(url_for('dashboard.minha_conta')), 302

    usuario.nome = nome
    session['nome_usuario'] = nome
    db.session.commit()
    return redirect(url_for('dashboard.minha_conta'))


@bp.route('/conta/senha', methods=['POST'])
def alterar_senha():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('dashboard.login'))

    usuario = UsuarioModel.query.get(usuario_id)
    senha_atual = request.form.get('senha_atual')
    senha_nova = request.form.get('senha_nova')
    senha_confirma = request.form.get('senha_confirma')

    if not usuario.verificar_senha(senha_atual):
        return redirect(url_for('dashboard.minha_conta')), 302
    if senha_nova != senha_confirma:
        return redirect(url_for('dashboard.minha_conta')), 302
    if len(senha_nova) < 6:
        return redirect(url_for('dashboard.minha_conta')), 302

    usuario.definir_senha(senha_nova)
    db.session.commit()
    return redirect(url_for('dashboard.minha_conta'))


@bp.route('/upgrade-premium', methods=['POST'])
def upgrade_premium():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('dashboard.login'))

    assinatura = AssinaturaModel.query.filter_by(usuario_id=usuario_id).first()
    if assinatura:
        assinatura.tipo = 'premium'
        db.session.commit()
    return redirect(url_for('dashboard.minha_conta'))


# ═══════════════════════════════════════════════════════
# API MOBILE — DASHBOARD (RF03)
# ═══════════════════════════════════════════════════════

@bp.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    usuario = UsuarioModel.query.get(int(usuario_id))
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    if not usuario or not conta:
        return jsonify({'erro': 'usuário não encontrado'}), 404

    todas_transacoes = TransacaoModel.query.filter_by(conta_id=conta.id).all()
    saldo_total = sum(tx.calcular_impacto_saldo() for tx in todas_transacoes)

    agora = datetime.now()
    inicio_mes = datetime(agora.year, agora.month, 1)
    fim_mes = (
        datetime(agora.year, agora.month + 1, 1)
        if agora.month < 12
        else datetime(agora.year + 1, 1, 1)
    )

    receitas_mes = db.session.query(db.func.sum(ReceitaModel.valor)).filter(
        ReceitaModel.conta_id == conta.id,
        ReceitaModel.status == 'ativa',
        ReceitaModel.data >= inicio_mes,
        ReceitaModel.data < fim_mes
    ).scalar() or 0

    despesas_mes = db.session.query(db.func.sum(DespesaModel.valor)).filter(
        DespesaModel.conta_id == conta.id,
        DespesaModel.status == 'ativa',
        DespesaModel.data >= inicio_mes,
        DespesaModel.data < fim_mes
    ).scalar() or 0

    percentual_gasto = (despesas_mes / receitas_mes * 100) if receitas_mes > 0 else 0
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()
    assinatura = AssinaturaModel.query.filter_by(usuario_id=usuario_id).first()
    notificacoes = NotificacaoModel.query.filter_by(
        usuario_id=usuario_id, lida=False
    ).count()

    return jsonify({
        'usuario': {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
        },
        'conta': {
            'numero_conta': conta.numero_conta,
            'saldo': conta.saldo,
        },
        'saldo_total': saldo_total,
        'receitas_mes': float(receitas_mes),
        'despesas_mes': float(despesas_mes),
        'percentual_gasto': round(percentual_gasto, 1),
        'alerta_gasto': percentual_gasto > 80,
        'nexo': {
            'estado': nexo.estado if nexo else 'erro',
            'fila_pendente': nexo.fila_pendente if nexo else 0,
        },
        'assinatura': {
            'tipo': assinatura.tipo if assinatura else 'gratuita',
        },
        'notificacoes_nao_lidas': notificacoes,
    })
    
 # ═══════════════════════════════════════════════════════
# API MOBILE — PERFIL
# ═══════════════════════════════════════════════════════

@bp.route('/api/perfil/nome', methods=['POST'])
def api_atualizar_nome():
    usuario_id = request.headers.get('X-Usuario-ID')

    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    data = request.get_json()

    if not data:
        return jsonify({'erro': 'dados inválidos'}), 400

    nome = data.get('nome', '').strip()

    if not nome or len(nome) < 3:
        return jsonify({'erro': 'nome deve ter pelo menos 3 caracteres'}), 400

    usuario = UsuarioModel.query.get(int(usuario_id))

    if not usuario:
        return jsonify({'erro': 'usuário não encontrado'}), 404

    usuario.nome = nome
    db.session.commit()

    return jsonify({
        'sucesso': True,
        'nome': usuario.nome
    })


@bp.route('/api/perfil/senha', methods=['POST'])
def api_alterar_senha():
    usuario_id = request.headers.get('X-Usuario-ID')

    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    data = request.get_json()

    if not data:
        return jsonify({'erro': 'dados inválidos'}), 400

    senha_atual = data.get('senha_atual')
    senha_nova = data.get('senha_nova')
    senha_confirma = data.get('senha_confirma')

    if not senha_atual or not senha_nova or not senha_confirma:
        return jsonify({'erro': 'preencha todos os campos'}), 400

    if senha_nova != senha_confirma:
        return jsonify({'erro': 'as senhas novas não coincidem'}), 400

    if len(senha_nova) < 6:
        return jsonify({'erro': 'senha deve ter pelo menos 6 caracteres'}), 400

    usuario = UsuarioModel.query.get(int(usuario_id))

    if not usuario:
        return jsonify({'erro': 'usuário não encontrado'}), 404

    if not usuario.verificar_senha(senha_atual):
        return jsonify({'erro': 'senha atual incorreta'}), 401

    usuario.definir_senha(senha_nova)
    db.session.commit()

    return jsonify({'sucesso': True})   
    