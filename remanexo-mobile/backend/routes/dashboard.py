from flask import Blueprint, render_template, session, redirect, url_for, request
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from ..database import db, UsuarioModel, ContaModel, ReceitaModel, DespesaModel, TransacaoModel, AssinaturaModel, NexoModel, NotificacaoModel

bp = Blueprint('dashboard', __name__, url_prefix='/')

# ═══════════════════════════════════════════════════════
# LOGIN / CADASTRO / LOGOUT (RF01)
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def index():
    """página inicial — se logado vai pra dashboard, senão login"""
    if 'usuario_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('dashboard.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """login com email + senha (rf01)"""
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
    """cadastro de novo usuário"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        # verifica se email já existe
        if UsuarioModel.query.filter_by(email=email).first():
            return render_template('cadastro.html', erro='email já cadastrado')

        # cria novo usuário com hash da senha (rf01)
        novo_usuario = UsuarioModel(nome=nome, email=email)
        novo_usuario.definir_senha(senha)

        db.session.add(novo_usuario)
        db.session.commit()

        # cria conta padrão
        conta = ContaModel(
            numero_conta=f"RMX{novo_usuario.id:06d}",
            usuario_id=novo_usuario.id,
            saldo=0
        )

        # cria assinatura gratuita padrão
        assinatura = AssinaturaModel(
            usuario_id=novo_usuario.id,
            tipo='gratuita'
        )

        # cria nexo
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
    """faz logout"""
    session.clear()
    return redirect(url_for('dashboard.login'))


# ═══════════════════════════════════════════════════════
# DASHBOARD PRINCIPAL (RF03)
# ═══════════════════════════════════════════════════════

@bp.route('/dashboard', methods=['GET'])
def dashboard():
    """
    dashboard com saldo consolidado em tempo real.
    recalcula saldo usando polimorfismo das transações (rf03)
    """
    # verifica autenticação
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    usuario = UsuarioModel.query.get(usuario_id)
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    if not conta:
        return redirect(url_for('dashboard.login'))

    # busca todas as transações (polimorfismo: receita/despesa automaticamente resolvidas)
    todas_transacoes = db.session.query(TransacaoModel).filter(
        TransacaoModel.conta_id == conta.id
    ).all()

    # recalcula saldo usando polimorfismo (cada transação sabe seu impacto)
    saldo_total = 0
    for tx in todas_transacoes:
        if tx.status == 'ativa':
            saldo_total += tx.calcular_impacto_saldo()

    conta.saldo = saldo_total

    # calcula receitas e despesas do mês
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

    # verifica alerta de gasto excessivo (rf09)
    percentual_gasto = (despesas_mes / receitas_mes * 100) if receitas_mes > 0 else 0
    alerta_gasto = percentual_gasto > 80

    # busca assinatura
    assinatura = AssinaturaModel.query.filter_by(usuario_id=usuario_id).first()

    # busca nexo (rf02)
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()

    # busca notificações
    notificacoes = NotificacaoModel.query.filter_by(usuario_id=usuario_id, lida=False).all()

    # contexto do template
    contexto = {
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
    }

    return render_template('dashboard.html', **contexto)


# ═══════════════════════════════════════════════════════
# MINHA CONTA
# ═══════════════════════════════════════════════════════

@bp.route('/conta', methods=['GET'])
def minha_conta():
    """página de perfil e configurações da conta"""
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('dashboard.login'))

    usuario = UsuarioModel.query.get(usuario_id)
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    assinatura = AssinaturaModel.query.filter_by(usuario_id=usuario_id).first()
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()

    # estatísticas simples
    total_transacoes = ReceitaModel.query.filter_by(conta_id=conta.id).count() + \
                       DespesaModel.query.filter_by(conta_id=conta.id).count()

    # para futura implementação de metas
    total_metas = 0
    metas_concluidas = 0

    contexto = {
        'usuario': usuario,
        'conta': conta,
        'assinatura': assinatura,
        'nexo': nexo,
        'total_transacoes': total_transacoes,
        'total_metas': total_metas,
        'metas_concluidas': metas_concluidas,
        'now': datetime.now(),
    }

    return render_template('conta.html', **contexto)


@bp.route('/conta/atualizar', methods=['POST'])
def atualizar_conta():
    """atualiza informações da conta"""
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('dashboard.login'))

    usuario = UsuarioModel.query.get(usuario_id)
    nome = request.form.get('nome')

    if not nome or len(nome.strip()) < 3:
        return redirect(url_for('dashboard.minha_conta', sucesso='nome muito curto')), 302

    usuario.nome = nome
    session['nome_usuario'] = nome
    db.session.commit()

    return redirect(url_for('dashboard.minha_conta'))


@bp.route('/conta/senha', methods=['POST'])
def alterar_senha():
    """altera senha do usuário"""
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
    """faz upgrade para premium"""
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('dashboard.login'))

    assinatura = AssinaturaModel.query.filter_by(usuario_id=usuario_id).first()
    if assinatura:
        assinatura.tipo = 'premium'
        db.session.commit()

    return redirect(url_for('dashboard.minha_conta'))
