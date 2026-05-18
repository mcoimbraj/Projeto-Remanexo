#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════╗
# ║           Troca moedas - INICIAR SERVIDOR                         ║
# ║    Sistema Financeiro com POO em Flask e SQLite              ║
# ╚═══════════════════════════════════════════════════════════════╝

clear

echo ""
echo "  ╔═══════════════════════════════════════════════════════════════╗"
echo "  ║                   Troca moedas - INICIANDO                        ║"
echo "  ║                                                               ║"
echo "  ║  Acesse: http://localhost:5000                               ║"
echo "  ║                                                               ║"
echo "  ║  Demo:                                                        ║"
echo "  ║  • Email: demo@Troca moedas.com                                   ║"
echo "  ║  • Senha: 123456                                              ║"
echo "  ║                                                               ║"
echo "  ╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Cria venv se não existir
if [ ! -d "venv" ]; then
    echo "[*] Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa venv
source venv/bin/activate

# Instala/atualiza dependências
echo "[*] Verificando dependências..."
pip install -q -r requirements.txt

# Roda a aplicação
echo "[*] Iniciando servidor Flask..."
python run.py
