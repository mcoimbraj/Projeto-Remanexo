# Defesa dos Padrões de Projeto

Este documento justifica a presença de três padrões de projeto (GoF) na arquitetura do sistema: **Prototype** (criacional), **Facade** (estrutural) e **Strategy** (comportamental). Cada seção indica onde o padrão aparece no código, qual problema ele resolve e por que a solução escolhida se encaixa na intenção formal do padrão.

---

## 1. Facade — `dashboard.py`

**Categoria:** Estrutural
**Onde:** rotas `dashboard()` e `api_dashboard()` em `dashboard.py`

O dashboard precisa apresentar, em uma única tela (ou em uma única resposta de API), informações que vêm de seis fontes diferentes: `UsuarioModel`, `ContaModel`, `TransacaoModel`, `AssinaturaModel`, `NexoModel` e `NotificacaoModel`. Sem um ponto de agregação, o cliente (web ou mobile) precisaria conhecer todos esses modelos, fazer múltiplas chamadas e calcular sozinho saldo, percentual de gasto e alertas.

A rota `/api/dashboard` resolve isso oferecendo uma **interface única e simplificada** sobre esse subsistema:

```python
@bp.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    usuario = UsuarioModel.query.get(...)
    conta = ContaModel.query.filter_by(...).first()
    todas_transacoes = TransacaoModel.query.filter_by(...).all()
    saldo_total = sum(tx.calcular_impacto_saldo() for tx in todas_transacoes)
    ...
    nexo = NexoModel.query.filter_by(...).first()
    assinatura = AssinaturaModel.query.filter_by(...).first()
    notificacoes = NotificacaoModel.query.filter_by(...).count()
    return jsonify({...})  # tudo consolidado em uma resposta
```

Isso é exatamente a intenção do Facade: **esconder a complexidade de um conjunto de subsistemas e expor um único ponto de acesso coerente**. O cliente não sabe — e não precisa saber — quantas tabelas ou consultas existem por trás; ele só consome um contrato simples (`GET /api/dashboard`).

> Nota de rigor: a implementação está como função de rota (Flask), não como uma classe `DashboardFacade` isolada. Funcionalmente, porém, ela cumpre o papel estrutural do padrão — centraliza e simplifica o acesso a múltiplos subsistemas em uma única interface.

---

## 2. Strategy — `transacao.py` + `conta.py`

**Categoria:** Comportamental
**Onde:** `Transacao.calcular_impacto_saldo()` (sobrescrito em `Receita` e `Despesa`), consumido por `Conta.recalcular_saldo()`

O sistema precisa calcular o impacto de uma transação no saldo, mas esse cálculo **varia conforme o tipo da transação**: receita soma, despesa subtrai. Em vez de centralizar essa regra em um `if/else` espalhado pelo código, cada algoritmo de cálculo fica encapsulado na própria classe que o representa:

```python
class Receita(Transacao):
    def calcular_impacto_saldo(self):
        return self.valor if self.status == 'ativa' else 0

class Despesa(Transacao):
    def calcular_impacto_saldo(self):
        return -self.valor if self.status == 'ativa' else 0
```

E quem consome esse algoritmo nem precisa saber qual variação está em jogo:

```python
def recalcular_saldo(self, transacoes):
    saldo_temporario = 0
    for transacao in transacoes:
        impacto = transacao.calcular_impacto_saldo()  # não importa se é Receita ou Despesa
        saldo_temporario += impacto
    self.saldo = max(0, saldo_temporario)
```

Esse é o núcleo da intenção do Strategy: **encapsular uma família de algoritmos intercambiáveis e permitir que o cliente os utilize sem conhecer os detalhes de cada um.** `Conta.recalcular_saldo` é o "contexto"; `calcular_impacto_saldo` é a "estratégia" que varia por tipo de transação. O mesmo raciocínio se repete em `categorizar()`, onde `Receita` e `Despesa` aplicam dicionários de palavras-chave diferentes para decidir a categoria.

> Nota de rigor: a variação de algoritmo aqui é resolvida por **herança e polimorfismo** (subclasses fixas), e não pela forma "canônica" do GoF, que injeta um objeto-estratégia em tempo de execução (composição). É uma variante simplificada do padrão — mantém a intenção (algoritmos intercambiáveis, sem `if/else` no cliente), trocando a flexibilidade de troca em runtime por simplicidade estrutural, já que no domínio do sistema o tipo da transação não muda depois de criada.

---

## 3. Prototype — `parcelamentos.py`

**Categoria:** Criacional
**Onde:** loop de geração de parcelas em `criar_parcelamento()` / `api_criar_parcelamento()`

Ao criar um parcelamento, o sistema não constrói cada parcela do zero com dados arbitrários: ele parte de um **molde comum** (mesmo valor por parcela, mesmo vínculo com a transação, mesmo status inicial) e gera N variações, alterando apenas o que de fato muda entre elas — número da parcela e data de vencimento:

```python
valor_parcela = valor_total / num_parcelas

for i in range(1, num_parcelas + 1):
    parcela = ParcelaModel(
        transacao_id=transacao.id,     # herdado do molde
        numero=i,                      # variação
        valor=valor_parcela,           # herdado do molde
        data_vencimento=data_primeira + timedelta(days=30 * (i - 1)),  # variação
        status='pendente'              # herdado do molde
    )
    db.session.add(parcela)
```

A intenção do Prototype é evitar reconstruir, repetidamente e do zero, objetos que compartilham a maior parte do estado, derivando novas instâncias a partir de um modelo-base e ajustando só o necessário. É exatamente o que ocorre aqui: cada parcela é uma derivação do mesmo "modelo" de parcela, com pequenos ajustes pontuais.

> Nota de rigor: a implementação atual instancia diretamente (`ParcelaModel(...)`) em vez de usar `copy.deepcopy()` sobre um objeto-protótipo explícito — não é Prototype na forma literal do GoF, mas reproduz sua intenção central (derivar instâncias semelhantes a partir de um molde comum, em vez de montagem independente). Uma evolução natural seria extrair um método `Parcela.criar_molde()` que retorna uma instância-base, clonada via `copy.deepcopy()` a cada iteração do loop.

---

## Resumo

| Padrão    | Categoria      | Localização                          | Fidelidade ao GoF |
|-----------|----------------|---------------------------------------|--------------------|
| Facade    | Estrutural     | `dashboard.py`                        | Alta (faltando classe dedicada) |
| Strategy  | Comportamental | `transacao.py` + `conta.py`           | Média (via herança, não composição) |
| Prototype | Criacional     | `parcelamentos.py`                    | Conceitual (sem `clone()` explícito) |

Cada padrão foi adotado para resolver um problema real do domínio — simplificar o acesso a múltiplos modelos, isolar variações de comportamento por tipo de transação e evitar reconstrução repetitiva de objetos semelhantes — ainda que, em alguns casos, a implementação tenha priorizado simplicidade sobre a forma estrutural canônica do livro de referência (Gamma et al., *Design Patterns*, 1994).
