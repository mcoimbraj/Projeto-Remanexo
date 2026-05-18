# Guia de Importação CSV Refatorado - Nexo

## 📋 Novo Formato

Com o refatoramento de 29/04/2026, o formato CSV do Nexo foi completamente redesenhado para suportar **saldo inicial**, **categorias customizadas** e **transações descartadas**.

### Estrutura de Coluna

```
descricao,valor,tipo,data,categoria,banco,status
```

| Campo | Tipo | Exemplo | Notas |
|-------|------|---------|-------|
| `descricao` | string | "Salário" | Tipo de transação |
| `valor` | float | 5000.00 | Sempre positivo |
| `tipo` | string | "receita" | receita \| despesa \| saldo_inicial |
| `data` | date | 2026-04-29 | Formato YYYY-MM-DD |
| `categoria` | string | "salário" | Pode ser vazio |
| `banco` | string | "itau" | Identificação do banco |
| `status` | string | "ativa" | ativa \| descartada |

---

## 🔄 Tipos de Transação

### 1. **receita** — Aumenta saldo
```csv
Salário,5000.00,receita,2026-04-01,salário,itau,ativa
```
- Cria objeto `ReceitaModel()`
- Impacto: `+valor` no saldo (se `status="ativa"`)

### 2. **despesa** — Diminui saldo
```csv
Aluguel,1200.00,despesa,2026-04-05,moradia,itau,ativa
```
- Cria objeto `DespesaModel()`
- Impacto: `-valor` no saldo (se `status="ativa"`)

### 3. **saldo_inicial** — Seta saldo direto
```csv
Saldo Inicial,5000.00,saldo_inicial,2026-01-01,saldo,itau,ativa
```
- **NÃO cria transação**
- Chama `conta.saldo = 5000.00` via setter
- **Processado SEMPRE PRIMEIRO**, independente de ordem no arquivo
- Nunca é descartado

---

## 🏷️ Campos de Status

### `status="ativa"`
```csv
Compra Online,299.99,despesa,2026-04-27,shopping,itau,ativa
```
- Transação normal
- Afeta saldo
- Aparece em "Transações Ativas"

### `status="descartada"`
```csv
Compra Cancelada,150.00,despesa,2026-04-20,brinquedos,itau,descartada
```
- Importa direto para **Lixeira**
- **Não afeta saldo**
- Aparece em "Transações > Lixeira"

---

## 🎯 Comportamento por Estado do Nexo

### Estado: **NexoAtivo** ✓
```
CSV Recebido
    ↓
[1] Processa saldo_inicial
    ↓
[2] Ordena demais por data
    ↓
[3] Importa tudo (ativa e descartada)
```

**Resultado:** Todas as transações importadas

---

### Estado: **NexoInstavel** 🔄
```
CSV Recebido
    ↓
[1] Processa saldo_inicial ✓
    ↓
[2] Retém outras transações na fila
    ↓
    (Aguardando volta à ativo)
```

**Resultado:** Só saldo_inicial aplicado, resto em cache local

---

### Estado: **NexoErro** ✗
```
CSV Recebido
    ↓
[1] Rejeita importação
    ↓
    (Nada é processado, nem saldo_inicial)
    ↓
    (Tente recuperar antes → /nexo/recuperar)
```

**Resultado:** Nenhuma transação importada

---

## 📝 Arquivo CSV Completo - Exemplo

```csv
descricao,valor,tipo,data,categoria,banco,status
Saldo Inicial,5000.00,saldo_inicial,2026-01-01,saldo,itau,ativa
Salário,5000.00,receita,2026-04-01,salário,itau,ativa
Aluguel,1200.00,despesa,2026-04-05,moradia,itau,ativa
Supermercado,350.50,despesa,2026-04-10,alimentação,itau,ativa
Freelance,800.00,receita,2026-04-15,freelance,nubank,ativa
Energia,150.00,despesa,2026-04-18,utilidades,itau,ativa
Compra Cancelada,200.00,despesa,2026-04-22,brinquedos,itau,descartada
```

**Fluxo de Processamento:**

1. **Lê arquivo** → 7 linhas
2. **Separa tipos:**
   - `saldo_inicial` → 1 linha
   - Demais → 6 linhas
3. **Processa saldo_inicial:** `conta.saldo = 5000.00`
4. **Ordena por data:**
   - 01-04, 05-04, 10-04, 15-04, 18-04, 22-04
5. **Importa 6 transações:**
   - 5 ativas (somam saldo)
   - 1 descartada (vai pra lixeira)

---

## 🛡️ Encapsulamento

O código respira **encapsulamento POO**:

```python
# ✅ CORRETO - usa setter
conta.saldo = 5000.00

# ❌ NUNCA FAÇA - viola encapsulamento
conta._saldo = 5000.00
```

O setter em `ContaModel` garante que toda mudança de saldo passa por lógica centralizada.

---

## 🚀 Como Usar no Sistema

1. Prepare arquivo CSV seguindo formato
2. Acesse **Nexo > Teste de Sincronização com CSV**
3. Selecione arquivo + banco
4. Clique **"Sincronizar via Open Finance"**
5. Resultado depende do estado atual do Nexo

---

## ✅ Checklist de Validação

Antes de importar, verifique:

- [ ] Todas as linhas têm 7 campos separados por vírgula
- [ ] `valor` são números positivos (ex: 150.50)
- [ ] `tipo` é um de: receita, despesa, saldo_inicial
- [ ] `data` está em formato YYYY-MM-DD
- [ ] `status` é um de: ativa, descartada
- [ ] Arquivo está em UTF-8
- [ ] Não há linhas vazias entre dados
- [ ] Primeira linha é **header** (descricao,valor,...)

---

**Última atualização:** 29/04/2026 | **Versão:** 2.0 Refatorada
