# backend/routes/api/nexo.py

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from datetime import datetime
from ...database import db, NexoModel, ContaModel, ReceitaModel, DespesaModel

# ─────────────────────────────────────────────────────────
# blueprint WEB — prefixo /nexo
# ─────────────────────────────────────────────────────────
bp = Blueprint('nexo', __name__, url_prefix='/nexo')


# ═══════════════════════════════════════════════════════
# ROTAS WEB
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def dashboard_nexo():
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()
    if not nexo:
        return redirect(url_for('dashboard.dashboard'))

    cores_estado = {'ativo': 'green', 'instavel': 'yellow', 'erro': 'red'}
    return render_template('nexo.html', **{
        'nexo': nexo,
        'cor_estado': cores_estado.get(nexo.estado, 'gray'),
        'descricao_estado': _descrever_estado(nexo.estado),
    })


@bp.route('/mudar-estado/<novo_estado>', methods=['POST'])
def mudar_estado(novo_estado):
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    nexo = NexoModel.query.filter_by(usuario_id=session['usuario_id']).first()
    if nexo and novo_estado in ['ativo', 'instavel', 'erro']:
        nexo.estado = novo_estado
        if novo_estado == 'erro':
            nexo.mensagem_erro = f"erro simulado em {datetime.now().strftime('%H:%M:%S')}"
        if novo_estado == 'ativo':
            nexo.mensagem_erro = None
        db.session.commit()

    return redirect(url_for('nexo.dashboard_nexo'))


@bp.route('/sincronizar', methods=['POST'])
def sincronizar():
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()

    if nexo:
        if nexo.estado == 'ativo':
            resultado = f"nexo ativo — fila processada com sucesso ({nexo.fila_pendente} itens)"
            nexo.fila_pendente = 0
        elif nexo.estado == 'instavel':
            resultado = f"nexo instável — fila retida localmente ({nexo.fila_pendente} itens em cache)"
        else:
            resultado = f"nexo em erro — sincronização bloqueada. erro: {nexo.mensagem_erro}"

        nexo.ultimo_sync = datetime.now()
        db.session.commit()

    return redirect(url_for('nexo.dashboard_nexo'))


@bp.route('/recuperar', methods=['POST'])
def recuperar_erro():
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    nexo = NexoModel.query.filter_by(usuario_id=session['usuario_id']).first()
    if nexo:
        nexo.estado = 'ativo'
        nexo.fila_pendente = 0
        nexo.mensagem_erro = None
        db.session.commit()

    return redirect(url_for('nexo.dashboard_nexo'))


@bp.route('/status', methods=['GET'])
def status_json():
    if 'usuario_id' not in session:
        return jsonify({'erro': 'não autenticado'}), 401

    usuario_id = session['usuario_id']
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()

    if nexo:
        return jsonify({
            'estado': nexo.estado,
            'fila_pendente': nexo.fila_pendente,
            'ultimo_sync': nexo.ultimo_sync.isoformat() if nexo.ultimo_sync else None,
            'mensagem_erro': nexo.mensagem_erro,
        })

    return jsonify({'erro': 'nexo não encontrado'}), 404


@bp.route('/sincronizar-csv', methods=['POST'])
def sincronizar_csv():
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    banco = request.form.get('banco', 'desconhecido')

    if not nexo or not conta:
        return redirect(url_for('nexo.dashboard_nexo'))

    if 'arquivo' not in request.files:
        return redirect(url_for('nexo.dashboard_nexo'))

    arquivo = request.files['arquivo']
    if arquivo.filename == '' or not arquivo.filename.endswith('.csv'):
        return redirect(url_for('nexo.dashboard_nexo'))

    try:
        conteudo = arquivo.read().decode('utf-8')
        linhas = conteudo.strip().split('\n')

        if len(linhas) < 2:
            return redirect(url_for('nexo.dashboard_nexo'))

        linhas_saldo_inicial = []
        linhas_transacoes = []

        for linha in linhas[1:]:
            if not linha.strip():
                continue
            try:
                partes = linha.split(',')
                tipo = partes[2].strip().lower() if len(partes) > 2 else 'receita'
                if tipo == 'saldo_inicial':
                    linhas_saldo_inicial.append(linha)
                else:
                    linhas_transacoes.append(linha)
            except:
                continue

        transacoes_importadas = 0
        transacoes_retidas = 0
        erros = 0

        # processa saldo_inicial primeiro
        for linha in linhas_saldo_inicial:
            try:
                partes = linha.split(',')
                valor = float(partes[1].strip())
                conta.saldo = valor
            except:
                erros += 1

        if nexo.estado == 'ativo':
            linhas_ordenadas = _ordenar_por_data(linhas_transacoes)
            for linha in linhas_ordenadas:
                try:
                    partes = linha.split(',')
                    descricao = partes[0].strip()
                    valor = float(partes[1].strip())
                    tipo = partes[2].strip().lower()
                    data_str = partes[3].strip()
                    categoria = partes[4].strip() if len(partes) > 4 else 'importado'
                    status = partes[6].strip().lower() if len(partes) > 6 else 'ativa'

                    data = datetime.strptime(data_str, '%Y-%m-%d')

                    if valor < 0 or tipo not in ['receita', 'despesa']:
                        erros += 1
                        continue

                    if status not in ['ativa', 'descartada']:
                        status = 'ativa'

                    if tipo == 'receita':
                        tx = ReceitaModel(
                            descricao=f"{descricao} (importado de {banco})",
                            valor=valor, conta_id=conta.id,
                            data=data, categoria=categoria, status=status
                        )
                    else:
                        tx = DespesaModel(
                            descricao=f"{descricao} (importado de {banco})",
                            valor=valor, conta_id=conta.id,
                            data=data, categoria=categoria, status=status
                        )

                    db.session.add(tx)
                    transacoes_importadas += 1

                except:
                    erros += 1

        elif nexo.estado == 'instavel':
            transacoes_retidas = len(linhas_transacoes)
            nexo.fila_pendente += transacoes_retidas

        elif nexo.estado == 'erro':
            nexo.mensagem_erro = f"importação csv rejeitada — estado erro ativo desde {datetime.now().strftime('%H:%M:%S')}"

        nexo.ultimo_sync = datetime.now()
        db.session.commit()

    except:
        pass

    return redirect(url_for('nexo.dashboard_nexo'))


def _descrever_estado(estado):
    return {
        'ativo': 'nexo ativo — tudo sincronizando normalmente',
        'instavel': 'nexo instável — dados no cache local, sincronizando depois',
        'erro': 'nexo em erro — sincronização bloqueada, aguardando recuperação',
    }.get(estado, 'estado desconhecido')


def _ordenar_por_data(linhas):
    linhas_com_data = []
    for linha in linhas:
        try:
            partes = linha.split(',')
            data = datetime.strptime(partes[3].strip(), '%Y-%m-%d')
            linhas_com_data.append((data, linha))
        except:
            linhas_com_data.append((datetime.now(), linha))
    linhas_com_data.sort(key=lambda x: x[0])
    return [linha for _, linha in linhas_com_data]


# ─────────────────────────────────────────────────────────
# blueprint API — sem prefixo, rotas em /api/nexo
# ─────────────────────────────────────────────────────────
bp_api = Blueprint('api_nexo', __name__)


@bp_api.route('/api/nexo', methods=['GET'])
def api_status_nexo():
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()
    if not nexo:
        return jsonify({'erro': 'nexo não encontrado'}), 404

    return jsonify({
        'estado': nexo.estado,
        'fila_pendente': nexo.fila_pendente,
        'ultimo_sync': nexo.ultimo_sync.isoformat() if nexo.ultimo_sync else None,
        'mensagem_erro': nexo.mensagem_erro,
    })


@bp_api.route('/api/nexo/mudar-estado', methods=['POST'])
def api_mudar_estado():
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'erro': 'JSON inválido'}), 400

    novo_estado = data.get('estado')
    if novo_estado not in ['ativo', 'instavel', 'erro']:
        return jsonify({'erro': 'estado inválido'}), 400

    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()
    if not nexo:
        return jsonify({'erro': 'nexo não encontrado'}), 404

    nexo.estado = novo_estado
    if novo_estado == 'erro':
        nexo.mensagem_erro = f"erro definido em {datetime.now().strftime('%H:%M:%S')}"
    if novo_estado == 'ativo':
        nexo.mensagem_erro = None

    db.session.commit()
    return jsonify({'sucesso': True, 'estado': nexo.estado})


@bp_api.route('/api/nexo/sincronizar', methods=['POST'])
def api_sincronizar():
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()
    if not nexo:
        return jsonify({'erro': 'nexo não encontrado'}), 404

    if nexo.estado == 'ativo':
        nexo.fila_pendente = 0
        resultado = 'fila processada com sucesso'
    elif nexo.estado == 'instavel':
        resultado = 'fila retida localmente'
    else:
        resultado = f'sincronização bloqueada: {nexo.mensagem_erro}'

    nexo.ultimo_sync = datetime.now()
    db.session.commit()
    return jsonify({'sucesso': True, 'resultado': resultado, 'estado': nexo.estado})


@bp_api.route('/api/nexo/recuperar', methods=['POST'])
def api_recuperar():
    usuario_id = request.headers.get('X-Usuario-ID')
    if not usuario_id:
        return jsonify({'erro': 'não autenticado'}), 401

    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()
    if not nexo:
        return jsonify({'erro': 'nexo não encontrado'}), 404

    nexo.estado = 'ativo'
    nexo.fila_pendente = 0
    nexo.mensagem_erro = None
    db.session.commit()
    return jsonify({'sucesso': True, 'estado': nexo.estado})