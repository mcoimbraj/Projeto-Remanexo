from datetime import datetime

# encapsulamento aqui — ninguém mexe direto nos atributos privados
class Conta:
    def __init__(self, id, numero_conta, usuario_id, saldo_inicial=0):
        self.id = id
        self.numero_conta = numero_conta
        self.usuario_id = usuario_id

        # atributos privados — só acessar via property
        self._saldo = saldo_inicial
        self._status_assinatura = 'ativa'
        self._data_criacao = datetime.now()
        self._historico_saldo = [saldo_inicial]

    # getter do saldo — ninguém mexe direto nesse atributo
    @property
    def saldo(self):
        return self._saldo

    # setter com validação — cada reais da conta é sagrado
    @saldo.setter
    def saldo(self, novo_saldo):
        if novo_saldo < 0:
            raise ValueError("saldo não pode ser negativo")
        self._saldo = novo_saldo
        self._historico_saldo.append(novo_saldo)

    # status da assinatura também é encapsulado
    @property
    def status_assinatura(self):
        return self._status_assinatura

    @status_assinatura.setter
    def status_assinatura(self, novo_status):
        if novo_status not in ['ativa', 'inativa', 'suspensa']:
            raise ValueError(f"status deve ser 'ativa', 'inativa' ou 'suspensa'")
        self._status_assinatura = novo_status

    # aqui é onde o polimorfismo trabalha — recalcula saldo usando o método abstrato das transações
    def recalcular_saldo(self, transacoes):
        """
        recalcula o saldo usando calcular_impacto_saldo de cada transação.
        cada subclasse (receita, despesa) sabe como impactar o saldo — polimorfismo em ação
        """
        saldo_temporario = 0

        for transacao in transacoes:
            # aqui o polimorfismo trabalha — cada tipo de transação calcula seu impacto
            impacto = transacao.calcular_impacto_saldo()
            saldo_temporario += impacto

        self.saldo = max(0, saldo_temporario)  # nunca deixa negativo
        return self.saldo

    # retorna histórico de saldos
    @property
    def historico_saldo(self):
        return self._historico_saldo

    def __repr__(self):
        return f"<Conta {self.numero_conta}: R$ {self.saldo:.2f} ({self.status_assinatura})>"
