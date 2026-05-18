#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🎯 REMANEXO - SISTEMA FINANCEIRO COM POO              ║
║                                                               ║
║  Sistema de gestão financeira com Open Finance simulado       ║
║  Desenvolvido com Flask, SQLite e os 4 pilares da POO        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Pra rodar:
  python run.py

Demo:
  Email: demo@remanexo.com
  Senha: 123456
"""

from remanexo_mobile.backend import app

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
