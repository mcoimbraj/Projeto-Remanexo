@echo off
REM ╔═══════════════════════════════════════════════════════════════╗
REM ║           Troca moedas - INICIAR SERVIDOR                         ║
REM ║    Sistema Financeiro com POO em Flask e SQLite              ║
REM ╚═══════════════════════════════════════════════════════════════╝

cls
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                   Troca moedas - INICIANDO                        ║
echo  ║                                                               ║
echo  ║  Acesse: http://localhost:5000                               ║
echo  ║                                                               ║
echo  ║  Demo:                                                        ║
echo  ║  • Email: demo@Troca moedas.com                                   ║
echo  ║  • Senha: 123456                                              ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Cria venv se não existir
if not exist venv (
    echo [*] Criando ambiente virtual...
    python -m venv venv
)

REM Ativa venv
call venv\Scripts\activate.bat

REM Instala/atualiza dependências
echo [*] Verificando dependências...
pip install -r requirements.txt > nul 2>&1

REM Roda a aplicação
echo [*] Iniciando servidor Flask...
python run.py

pause
