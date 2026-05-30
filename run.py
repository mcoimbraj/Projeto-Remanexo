#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🎯 Remanexo - SISTEMA FINANCEIRO COM POO              ║
║                                                               ║
║  Sistema de gestão financeira com Open Finance simulado       ║
║  Desenvolvido com Flask, SQLite e os 4 pilares da POO        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Pra rodar:
  python run.py

Demo:
  Email: demo@Remanexo.com
  Senha: 123456
"""

from remanexo_mobile.backend.app import create_app

app = create_app()

if __name__ == "__main__":
   app.run(debug=True, host="0.0.0.0", port=5000)
