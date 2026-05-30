from abc import ABC, abstractmethod
from datetime import datetime

# classe abstrata — todo mundo herda daqui
class Transacao(ABC):
    def __init__(self, id, descricao, valor, data, categoria, status='ativa'):
        self.id = id
        self.descricao = descricao
        self.valor = valor
        self.data = data
        self.categoria = categoria
        self.status = status  # 'ativa' ou 'descartada'

    # método abstrato — quem herdar tem que implementar isso
    @abstractmethod
    def calcular_impacto_saldo(self):
        pass

    # categorização automática por palavras-chave
    def categorizar(self):
        palavras_chave = {
            'transporte': ['uber', 'taxi', 'ônibus', 'metrô', 'gasolina', 'carro'],
            'alimentação': ['supermercado', 'restaurante', 'delivery', 'ifood', 'pizza'],
            'saúde': ['farmácia', 'médico', 'dentista', 'hospital', 'remédio'],
            'lazer': ['cinema', 'teatro', 'show', 'bar', 'diversão'],
            'trabalho': ['projeto', 'freelance', 'cliente', 'salário'],
            'educação': ['curso', 'livro', 'escola', 'faculdade', 'educação'],
        }

        descricao_lower = self.descricao.lower()
        for cat, palavras in palavras_chave.items():
            if any(palavra in descricao_lower for palavra in palavras):
                self.categoria = cat
                return

        self.categoria = 'geral'

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.descricao}: R$ {self.valor:.2f}>"


# aqui é onde o polimorfismo salva a pátria — receita soma, despesa subtrai
class Receita(Transacao):
    def calcular_impacto_saldo(self):
        # receita soma
        if self.status == 'ativa':
            return self.valor
        return 0

    def categorizar(self):
        palavras_chave = {
            'salário': ['salário', 'remuneração', 'pagamento'],
            'freelance': ['freelance', 'projeto', 'consultoria'],
            'investimentos': ['dividendo', 'juros', 'investimento'],
            'outros': ['bônus', 'prêmio', 'presente'],
        }

        descricao_lower = self.descricao.lower()
        for cat, palavras in palavras_chave.items():
            if any(palavra in descricao_lower for palavra in palavras):
                self.categoria = cat
                return

        self.categoria = 'outras receitas'


# despesa subtrai do saldo
class Despesa(Transacao):
    def calcular_impacto_saldo(self):
        # despesa subtrai
        if self.status == 'ativa':
            return -self.valor
        return 0

    def categorizar(self):
        # categorização padrão já vem da classe pai
        super().categorizar()
