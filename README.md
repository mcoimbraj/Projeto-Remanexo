# 🎯 REMANEXO - Sistema Financeiro com POO

> **Sistema de gestão financeira com Open Finance Simulado** desenvolvido em **Python/Flask/SQLite**
>
> Demonstração prática dos **4 pilares da POO** em um ambiente funcional e real

---

## 🚀 Início Rápido

```bash
cd Projeto-Remanexo
python run.py
```

Acesse **http://localhost:5000**

### 🔐 Credenciais Demo
```
Email: demo@remanexo.com
Senha: 123456
```

---

## 🏛️ Arquitetura POO - Conceitos Centrais

### 1️⃣ ABSTRAÇÃO - Classe Base `Transacao`
**Arquivo**: `backend/database.py` (linhas 15-50)

```python
class Transacao(db.Model):
    """Classe abstrata — define contrato para todas as transações"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    valor = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='ativa')
    
    def calcular_impacto_saldo(self):
        """Método polimórfico — cada subclasse implementa diferente"""
        pass
```

**Propósito**: Define a interface comum que toda transação deve possuir, sem implementar comportamentos específicos.

---

### 2️⃣ HERANÇA - `ReceitaModel` e `DespesaModel`
**Arquivo**: `backend/database.py` (linhas 51-90)

```python
class ReceitaModel(Transacao):
    """Herda de Transacao — especializa para receitas"""
    __tablename__ = 'receitas'
    __mapper_args__ = {'polymorphic_identity': 'receita'}
    
    def calcular_impacto_saldo(self):
        return self.valor  # ➕ soma ao saldo

class DespesaModel(Transacao):
    """Herda de Transacao — especializa para despesas"""
    __tablename__ = 'despesas'
    __mapper_args__ = {'polymorphic_identity': 'despesa'}
    
    def calcular_impacto_saldo(self):
        return -self.valor  # ➖ subtrai do saldo
```

**Propósito**: Permite que Receita e Despesa herdem estrutura comum de Transacao, mas implementem `calcular_impacto_saldo()` diferentemente.

**Benefício**: Reutilização de código + comportamentos especializados.

---

### 3️⃣ ENCAPSULAMENTO - Atributos Privados em `Conta`
**Arquivo**: `backend/database.py` (linhas 130-180)

```python
class ContaModel(db.Model):
    __tablename__ = 'contas'
    
    id = db.Column(db.Integer, primary_key=True)
    _saldo = db.Column('saldo', db.Float, default=0.0)  # atributo privado
    numero_conta = db.Column(db.String(20), unique=True)
    
    @property
    def saldo(self):
        """Getter — acesso controlado"""
        return self._saldo
    
    @saldo.setter
    def saldo(self, novo_saldo):
        """Setter — validação antes de atualizar"""
        if novo_saldo < -1000:  # limite de crédito
            raise ValueError("Limite de crédito excedido")
        self._saldo = novo_saldo
```

**Propósito**: Protege dados críticos com validação automática.

**Invocado em**: `dashboard.py` (recalcula saldo com polimorfismo)

---

### 4️⃣ POLIMORFISMO - Dashboard Consolidado
**Arquivo**: `backend/routes/dashboard.py` (linhas 115-135)

```python
@bp.route('/dashboard')
def dashboard():
    # Query polimórfica — busca receitas E despesas como uma lista
    transacoes = db.session.query(TransacaoModel).filter(
        TransacaoModel.conta_id == conta.id,
        TransacaoModel.status == 'ativa'
    ).all()
    
    # Polimorfismo em ação — cada transação usa SUA implementação
    saldo = sum(tx.calcular_impacto_saldo() for tx in transacoes)
    receitas = sum(tx.valor for tx in transacoes if tx.tipo == 'receita')
    despesas = sum(tx.valor for tx in transacoes if tx.tipo == 'despesa')
```

**Por que**: Sem polimorfismo, precisaríamos fazer queries separadas e lógica condicional complexa. Com polimorfismo, cada objeto sabe como calcular seu impacto.

**Benefício**: Código limpo, extensível e alinhado com POO.

---

## 📋 Funcionalidades Atuais

| Feature | Status | Localização |
|---------|--------|-------------|
| **Autenticação** (email + senha com hash) | ✅ | `dashboard.py` |
| **Dashboard** (saldo consolidado tempo real) | ✅ | `dashboard.py` |
| **Transações** (adicionar, editar, descartar) | ✅ | `transacoes.py` |
| **Lixeira** (restaurar/deletar permanentemente) | ✅ | `transacoes.py` (aba) |
| **Parcelamentos** (receitas/despesas parceladas) | ✅ | `parcelamentos.py` |
| **Categorias** (gerenciar + palavras-chave) | ✅ | `categorias.py` |
| **Open Finance (Nexo)** (3 estados: ativo/instável/erro) | ✅ | `nexo.py` |
| **Metas** (criar, progresso visual) | ✅ | `metas.py` |
| **Categorização automática** (por palavras-chave) | ✅ | `transacoes.py` |
| **Import CSV** (via Nexo) | ✅ | `nexo.py` |

---

## 🎯 Detalhes de Implementação

### Transações (Herança + Polimorfismo)
- **Receita**: `+` saldo
- **Despesa**: `-` saldo
- **Parcelada**: Valor adicionado ao saldo apenas quando parcela é paga/recebida
- **Categorização**: Automática por palavras-chave ou manual
- **Lixeira**: Status `descartada` — não afeta saldo
- **Edição**: Modal inline com validação

### Open Finance (Padrão State + Polimorfismo)
- **Ativo**: Sincroniza imediatamente
- **Instável**: Segura fila em cache local
- **Erro**: Bloqueia sincronização, permite recuperação

### Parcelamentos (Herança POO)
- Recebe/Paga parcela → atualiza saldo incrementalmente
- Receita: botão "Receber" | Despesa: botão "Pagar"
- Status: Pendente → Paga/Descartada
- Vencimento com alerta visual

### Categorias (Persistência em BD)
- 10 categorias padrão criadas no startup
- Palavras-chave customizáveis em tempo real
- Categorização automática aplica-se à transação seguinte

---

## 📁 Estrutura

```
Projeto-Remanexo/
├── backend/
│   ├── database.py          # Models: Transacao + Herança
│   ├── app.py               # Factory Flask
│   ├── routes/
│   │   ├── dashboard.py     # Polimorfismo em ação
│   │   ├── transacoes.py    # Herança + Categorização
│   │   ├── parcelamentos.py # Parcelamentos
│   │   ├── categorias.py    # Categorias + Palavras-chave
│   │   ├── nexo.py          # Padrão State
│   │   └── metas.py
│   ├── templates/
│   │   ├── dashboard.html
│   │   ├── transacoes.html  # Abas: Ativas | Lixeira
│   │   ├── parcelamentos.html
│   │   ├── categorias.html
│   │   ├── nexo.html
│   │   └── base.html        # Menu principal
│   └── static/
├── run.py                   # Entrada
├── requirements.txt
└── README.md
```

---

## 🧪 Testando os Conceitos

### Herança em Ação
1. **Transações** → Adicione receita + despesa
2. **Dashboard** → Veja ambas impactarem saldo de formas diferentes

### Polimorfismo em Ação
1. **Dashboard** → Saldo = Σ(tx.calcular_impacto_saldo())
2. Cada tx chama SUA versão do método

### Encapsulamento em Ação
- Tente editar transação com valor negativo
- Validação protege integridade

### Parcelamentos (Herança + Lógica)
- Crie receita parcelada → valor inicial = 0 no saldo
- Clique "Receber" em parcela → saldo atualiza apenas daquela parcela

---

## 💻 Tech Stack

- **Backend**: Python 3.8+, Flask 2.3
- **BD**: SQLite + SQLAlchemy ORM (suporta polimorfismo)
- **Frontend**: HTML5 + Bootstrap 5 + Vanilla JS
- **Auth**: Werkzeug (hash seguro)
- **Sessões**: Flask-Session

---

## 🔮 Roadmap

- [ ] Relatório PDF
- [ ] Notificações gastos excessivos
- [ ] Gráficos avançados
- [ ] Integração real Open Finance
- [ ] App Mobile

---

**Remanexo** © 2026 | Desenvolvido com POO e muito café ☕
