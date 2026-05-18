from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from datetime import datetime
from ..database import db, NexoModel, ReceitaModel, DespesaModel, ContaModel

bp = Blueprint('nexo', __name__, url_prefix='/nexo')

# ═══════════════════════════════════════════════════════
# DASHBOARD DO NEXO (RF02)
# ═══════════════════════════════════════════════════════

@bp.route('/', methods=['GET'])
def dashboard_nexo():
    """
    rf02: open finance simulado via nexo com os 3 estados (ativo, instável, erro).
    padrão state em ação — cada estado sabe como se comportar
    """
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()

    if not nexo:
        return redirect(url_for('dashboard.dashboard'))

    # determina cor do indicador visual baseado no estado
    cores_estado = {
        'ativo': 'green',      # badge verde
        'instavel': 'yellow',  # badge amarelo
        'erro': 'red'          # badge vermelho
    }

    contexto = {
        'nexo': nexo,
        'cor_estado': cores_estado.get(nexo.estado, 'gray'),
        'descricao_estado': descrever_estado(nexo.estado)
    }

    return render_template('nexo.html', **contexto)


# ═══════════════════════════════════════════════════════
# MUDAR ESTADO DO NEXO (SIMULAÇÃO)
# ═══════════════════════════════════════════════════════

@bp.route('/mudar-estado/<novo_estado>', methods=['POST'])
def mudar_estado(novo_estado):
    """
    muda o estado do nexo — simula comportamentos diferentes (rf02).
    estados válidos: ativo, instavel, erro
    """
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()

    if nexo:
        estados_validos = ['ativo', 'instavel', 'erro']

        if novo_estado in estados_validos:
            nexo.estado = novo_estado

            # se mudou pra erro, registra mensagem
            if novo_estado == 'erro':
                nexo.mensagem_erro = f"erro simulado em {datetime.now().strftime('%H:%M:%S')}"

            # se voltou pra ativo, limpa erro
            if novo_estado == 'ativo':
                nexo.mensagem_erro = None

            db.session.commit()

    return redirect(url_for('nexo.dashboard_nexo'))


# ═══════════════════════════════════════════════════════
# SINCRONIZAR FILA (RF02)
# ═══════════════════════════════════════════════════════

@bp.route('/sincronizar', methods=['POST'])
def sincronizar():
    """
    simula sincronização do nexo — comportamento depende do estado.
    padrão STATE: cada estado (ativo, instável, erro) tem seu próprio comportamento.
    compare com polimorfismo: state muda comportamento da MESMA classe (nexo),
    polimorfismo chama DIFERENTES classes (receita/despesa) com MESMO método
    """
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()

    if nexo:
        # simula processamento baseado no estado
        if nexo.estado == 'ativo':
            # estado ativo: processa normalmentente
            resultado = f"nexo ativo — fila processada com sucesso ({nexo.fila_pendente} itens)"
            nexo.fila_pendente = 0
        elif nexo.estado == 'instavel':
            # estado instável: segura a fila localmente (previne trava)
            resultado = f"nexo instável — fila retida localmente ({nexo.fila_pendente} itens em cache)"
        else:  # erro
            # estado erro: não processa nada
            resultado = f"nexo em erro — sincronização bloqueada. erro: {nexo.mensagem_erro}"

        nexo.ultimo_sync = datetime.now()
        db.session.commit()

    return redirect(url_for('nexo.dashboard_nexo'))


# ═══════════════════════════════════════════════════════
# RECUPERAR DE ERRO (RF02)
# ═══════════════════════════════════════════════════════

@bp.route('/recuperar', methods=['POST'])
def recuperar_erro():
    """
    recupera o nexo de um erro — limpa fila e volta pra ativo (rf02)
    """
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()

    if nexo:
        nexo.estado = 'ativo'
        nexo.fila_pendente = 0
        nexo.mensagem_erro = None
        db.session.commit()

    return redirect(url_for('nexo.dashboard_nexo'))


# ═══════════════════════════════════════════════════════
# STATUS DO NEXO (JSON)
# ═══════════════════════════════════════════════════════

@bp.route('/status', methods=['GET'])
def status_json():
    """retorna status do nexo em JSON — útil pra frontend"""
    if 'usuario_id' not in session:
        return jsonify({'erro': 'não autenticado'}, 401)

    usuario_id = session['usuario_id']
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()

    if nexo:
        return jsonify({
            'estado': nexo.estado,
            'fila_pendente': nexo.fila_pendente,
            'ultimo_sync': nexo.ultimo_sync.isoformat() if nexo.ultimo_sync else None,
            'mensagem_erro': nexo.mensagem_erro
        })

    return jsonify({'erro': 'nexo não encontrado'}, 404)


# ═══════════════════════════════════════════════════════
# FUNÇÃO AUXILIAR
# ═══════════════════════════════════════════════════════

def descrever_estado(estado):
    """retorna descrição amigável do estado do nexo (rf02)"""
    descricoes = {
        'ativo': 'nexo ativo — tudo sincronizando normalmente',
        'instavel': 'nexo instável — dados no cache local, sincronizando depois',
        'erro': 'nexo em erro — sincronização bloqueada, aguardando recuperação'
    }
    return descricoes.get(estado, 'estado desconhecido')


# ═══════════════════════════════════════════════════════
# SINCRONIZAR COM CSV (RFC - REFATORADO)
# ═══════════════════════════════════════════════════════

@bp.route('/sincronizar-csv', methods=['POST'])
def sincronizar_csv():
    """
    importa transações via CSV com suporte a saldo_inicial, status descartada e comportamento por estado.
    formato esperado: descricao,valor,tipo,data,categoria,banco,status
    tipos: receita, despesa, saldo_inicial
    status: ativa, descartada
    
    ⚠️ POLIMORFISMO ESTÁ AQUI: processa ReceitaModel e DespesaModel — o dashboard
    depois chama calcular_impacto_saldo() em cada uma sem saber o tipo (polimorfismo)
    """
    if 'usuario_id' not in session:
        return redirect(url_for('dashboard.login'))

    usuario_id = session['usuario_id']
    nexo = NexoModel.query.filter_by(usuario_id=usuario_id).first()
    conta = ContaModel.query.filter_by(usuario_id=usuario_id).first()
    banco = request.form.get('banco', 'desconhecido')

    if not nexo or not conta:
        return redirect(url_for('nexo.dashboard_nexo'))

    # verifica se arquivo foi enviado
    if 'arquivo' not in request.files:
        return redirect(url_for('nexo.dashboard_nexo'))

    arquivo = request.files['arquivo']
    if arquivo.filename == '' or not arquivo.filename.endswith('.csv'):
        return redirect(url_for('nexo.dashboard_nexo'))

    try:
        # lê arquivo CSV
        conteudo = arquivo.read().decode('utf-8')
        linhas = conteudo.strip().split('\n')

        if len(linhas) < 2:
            return redirect(url_for('nexo.dashboard_nexo'))

        # separa linhas de saldo_inicial das demais
        linhas_saldo_inicial = []
        linhas_transacoes = []

        for linha in linhas[1:]:  # pula header
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

        # contadores pra resultado
        saldo_inicial_processado = False
        transacoes_importadas = 0
        transacoes_retidas = 0
        erros = 0

        # ════════════════════════════════════════════════════
        # 1º PASSO: processa saldo_inicial PRIMEIRO
        # ════════════════════════════════════════════════════

        for linha in linhas_saldo_inicial:
            try:
                partes = linha.split(',')
                valor = float(partes[1].strip())

                # saldo_inicial é especial — ele seta direto no atributo privado via setter
                conta.saldo = valor
                saldo_inicial_processado = True

            except Exception as e:
                erros += 1
                continue

        # ════════════════════════════════════════════════════
        # 2º PASSO: comportamento depende do estado do nexo
        # ════════════════════════════════════════════════════

        if nexo.estado == 'ativo':
            # estado ativo: processa tudo normalmente
            # ordena por data antes de processar — garante consistência
            linhas_transacoes_ordenadas = _ordenar_por_data(linhas_transacoes)

            for linha in linhas_transacoes_ordenadas:
                try:
                    partes = linha.split(',')
                    descricao = partes[0].strip()
                    valor = float(partes[1].strip())
                    tipo = partes[2].strip().lower()
                    data_str = partes[3].strip()
                    categoria = partes[4].strip() if len(partes) > 4 else 'importado'
                    status = partes[6].strip().lower() if len(partes) > 6 else 'ativa'

                    # parse data
                    data = datetime.strptime(data_str, '%Y-%m-%d')

                    # valida dados
                    if valor < 0 or tipo not in ['receita', 'despesa']:
                        erros += 1
                        continue

                    # valida status
                    if status not in ['ativa', 'descartada']:
                        status = 'ativa'

                    # ╭─────────────────────────────────────────────────────╮
                    # │ POLIMORFISMO EM AÇÃO: cria ReceitaModel ou         │
                    # │ DespesaModel baseado no tipo. ambas são subclasses │
                    # │ de TransacaoModel e implementam                    │
                    # │ calcular_impacto_saldo() diferente:                │
                    # │                                                     │
                    # │ - ReceitaModel.calcular_impacto_saldo() → +valor   │
                    # │ - DespesaModel.calcular_impacto_saldo() → -valor   │
                    # │                                                     │
                    # │ quando o dashboard faz:                            │
                    # │   for tx in transacoes:                            │
                    # │       saldo += tx.calcular_impacto_saldo()         │
                    # │                                                     │
                    # │ não há if/else — python automaticamente chama o    │
                    # │ método correto de cada objeto (polimorfismo)       │
                    # ╰─────────────────────────────────────────────────────╯

                    if tipo == 'receita':
                        tx = ReceitaModel(
                            descricao=f"{descricao} (importado de {banco})",
                            valor=valor,
                            conta_id=conta.id,
                            data=data,
                            categoria=categoria,
                            status=status
                        )
                    else:  # despesa
                        tx = DespesaModel(
                            descricao=f"{descricao} (importado de {banco})",
                            valor=valor,
                            conta_id=conta.id,
                            data=data,
                            categoria=categoria,
                            status=status
                        )

                    db.session.add(tx)
                    transacoes_importadas += 1

                except Exception as e:
                    erros += 1
                    continue

        elif nexo.estado == 'instavel':
            # nexo instável? segura as transações e só aplica o saldo inicial por ora
            # o resto fica na fila pra sincronizar depois
            transacoes_retidas = len(linhas_transacoes)
            nexo.fila_pendente += transacoes_retidas

        elif nexo.estado == 'erro':
            # estado erro: não processa nada (nem as transações)
            nexo.mensagem_erro = f"importação csv rejeitada — estado erro ativo desde {datetime.now().strftime('%H:%M:%S')}"
            transacoes_retidas = len(linhas_transacoes)
            saldo_inicial_processado = False  # desfaz saldo inicial se tiver erro

        # atualiza timestamp
        nexo.ultimo_sync = datetime.now()
        db.session.commit()

        return redirect(url_for('nexo.dashboard_nexo'))

    except Exception as e:
        return redirect(url_for('nexo.dashboard_nexo'))


# ════════════════════════════════════════════════════════
# FUNÇÃO AUXILIAR: ORDENAR POR DATA
# ════════════════════════════════════════════════════════

def _ordenar_por_data(linhas):
    """ordena linhas do csv por data — garante ordem de processamento consistente"""
    linhas_com_data = []

    for linha in linhas:
        try:
            partes = linha.split(',')
            data_str = partes[3].strip()
            data = datetime.strptime(data_str, '%Y-%m-%d')
            linhas_com_data.append((data, linha))
        except:
            linhas_com_data.append((datetime.now(), linha))

    # ordena por data e retorna só as linhas
    linhas_com_data.sort(key=lambda x: x[0])
    return [linha for data, linha in linhas_com_data]
