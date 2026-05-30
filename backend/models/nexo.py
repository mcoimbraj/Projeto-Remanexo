from abc import ABC, abstractmethod
from datetime import datetime

# padrão state em ação: cada estado sabe como se comportar
class EstadoNexo(ABC):
    """classe abstrata dos estados — cada estado delegado tem responsabilidade única"""

    @abstractmethod
    def sincronizar(self, fila):
        pass


# nexo ativo — tudo flui normalmente
class NexoAtivo(EstadoNexo):
    def sincronizar(self, fila):
        """
        quando ativo, processa a fila inteira sem medo.
        simula integração normal com open finance
        """
        resultado = []
        while fila:
            transacao = fila.pop(0)
            resultado.append({
                'transacao': transacao,
                'status': 'processada',
                'timestamp': datetime.now()
            })
        return resultado


# nexo instável — segura o estado local pra não travar a tela
class NexoInstavel(EstadoNexo):
    def sincronizar(self, fila):
        """
        se o nexo tiver instável, a gente segura o estado local pra não travar a tela.
        previne bug de carregamento infinito — é como aquele app que fica bugado mas você segue usando
        """
        return {
            'status': 'retido_localmente',
            'fila_pendente': len(fila),
            'mensagem': 'nexo instável — dados no cache local, sincronizar depois'
        }


# nexo com erro — log e desiste
class NexoErro(EstadoNexo):
    def __init__(self, mensagem_erro=''):
        self.mensagem_erro = mensagem_erro

    def sincronizar(self, fila):
        """
        erro detectado — loga e não processa nada pra não piorar a situação
        """
        print(f"[ERRO NEXO] {self.mensagem_erro}")
        return {
            'status': 'erro',
            'mensagem': self.mensagem_erro,
            'fila_intacta': len(fila)
        }


# padrão state em ação: o nexo delega pra quem sabe lidar
class Nexo:
    """
    o nexo simula open finance — mantém estado e delega sincronização.
    é basicamente a integração financeira da plataforma.
    """

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id
        self._estado = NexoAtivo()  # começa ativo
        self._fila_sincronizacao = []
        self._ultimo_sync = None

    # aqui delegamos — state pattern se desenrolando
    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, novo_estado):
        """muda o estado — o comportamento muda automaticamente"""
        if isinstance(novo_estado, EstadoNexo):
            self._estado = novo_estado
        else:
            raise TypeError("novo_estado deve herdar de EstadoNexo")

    def adicionar_fila(self, transacao):
        """enfileira transação pra sincronizar depois"""
        self._fila_sincronizacao.append(transacao)

    def sincronizar(self):
        """
        delega pra o estado atual — polimorfismo em ação.
        cada estado faz sua coisa de forma diferente
        """
        resultado = self._estado.sincronizar(self._fila_sincronizacao)
        self._ultimo_sync = datetime.now()
        return resultado

    def simular_falha(self, mensagem='erro desconhecido'):
        """simula uma falha — muda pra estado de erro"""
        self._estado = NexoErro(mensagem)

    def recuperar(self):
        """recupera do erro — volta pra ativo"""
        self._estado = NexoAtivo()
        self._fila_sincronizacao = []

    def pausar(self):
        """coloca em estado instável — de propósito"""
        self._estado = NexoInstavel()

    def status(self):
        """retorna status do nexo"""
        estado_nome = self._estado.__class__.__name__
        return {
            'estado': estado_nome,
            'fila_pendente': len(self._fila_sincronizacao),
            'ultimo_sync': self._ultimo_sync
        }

    def __repr__(self):
        return f"<Nexo usuario={self.usuario_id} estado={self._estado.__class__.__name__}>"
