from datetime import datetime, timedelta

class Assinatura:
    """controla a assinatura do usuário — pode ser básica ou premium"""

    TIPOS_ASSINATURA = ['gratuita', 'basica', 'premium']

    def __init__(self, id, usuario_id, tipo='gratuita', data_inicio=None, data_renovacao=None):
        self.id = id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.data_inicio = data_inicio or datetime.now()

        # define data de renovação automática (30 dias depois)
        if data_renovacao:
            self.data_renovacao = data_renovacao
        else:
            self.data_renovacao = self.data_inicio + timedelta(days=30)

        self.ativa = True

    # verifica se assinatura está vencida
    @property
    def vencida(self):
        if self.tipo == 'gratuita':
            return False  # gratuita nunca vence
        return datetime.now() > self.data_renovacao

    # tempo até vencer (em dias)
    @property
    def dias_vencimento(self):
        if self.tipo == 'gratuita':
            return None
        diferenca = self.data_renovacao - datetime.now()
        return diferenca.days

    def renovar(self):
        """renova a assinatura por mais 30 dias"""
        if self.tipo != 'gratuita':
            self.data_renovacao = datetime.now() + timedelta(days=30)

    def downgrade_para_gratuita(self):
        """faz downgrade pra gratuita"""
        self.tipo = 'gratuita'
        self.data_renovacao = None

    def upgrade(self, novo_tipo):
        """faz upgrade pra plano premium"""
        if novo_tipo not in self.TIPOS_ASSINATURA:
            raise ValueError(f"tipo deve estar em {self.TIPOS_ASSINATURA}")
        self.tipo = novo_tipo
        self.data_renovacao = datetime.now() + timedelta(days=30)

    def __repr__(self):
        return f"<Assinatura {self.tipo} (usuario={self.usuario_id}) {'[VENCIDA]' if self.vencida else ''}>"
