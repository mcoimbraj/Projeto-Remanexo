from datetime import datetime

class Meta:
    """
    meta de economia — usuário define um valor alvo e acompanha o progresso com barra visual.
    rf05: metas com valor_alvo, valor_acumulado e barra de progresso (%)
    """

    def __init__(self, id, usuario_id, descricao, valor_alvo, valor_acumulado=0, 
                 data_criacao=None, data_prazo=None):
        self.id = id
        self.usuario_id = usuario_id
        self.descricao = descricao
        self.valor_alvo = valor_alvo
        self.valor_acumulado = valor_acumulado
        self.data_criacao = data_criacao or datetime.now()
        self.data_prazo = data_prazo
        self.ativa = True

    # calcula o percentual de progresso
    @property
    def percentual_progresso(self):
        if self.valor_alvo == 0:
            return 0
        percentual = (self.valor_acumulado / self.valor_alvo) * 100
        return min(percentual, 100)  # nunca passar de 100%

    # verifica se atingiu a meta
    @property
    def atingida(self):
        return self.valor_acumulado >= self.valor_alvo

    # retorna quanto falta pra bater a meta
    @property
    def valor_restante(self):
        return max(0, self.valor_alvo - self.valor_acumulado)

    def atualizar_acumulado(self, novo_valor):
        """atualiza quanto já acumulou pra meta"""
        self.valor_acumulado = novo_valor

    def adicionar_acumulado(self, valor):
        """incrementa o acumulado (ex: no final do mês)"""
        self.valor_acumulado += valor

    def __repr__(self):
        return f"<Meta {self.descricao}: R$ {self.valor_acumulado:.2f} / R$ {self.valor_alvo:.2f} ({self.percentual_progresso:.1f}%)>"
