#!/usr/bin/env python3
"""
Arquivo principal para inicializar a aplicação COINctrl
Execute este arquivo para rodar o servidor Flask
"""

import os
from app import create_app, db
from app.models import User, Category, Transaction, Account
from flask_migrate import upgrade

# Criar a aplicação usando a factory function
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """
    Disponibiliza objetos no shell do Flask para facilitar testes
    Execute: flask shell
    """
    return {
        'db': db,
        'User': User,
        'Category': Category,
        'Transaction': Transaction,
        'Account': Account
    }

@app.cli.command()
def deploy():
    """
    Comando para fazer deploy da aplicação
    Execute: flask deploy
    """
    # Criar/atualizar tabelas do banco de dados
    upgrade()
    
    # Aqui você pode adicionar outras tarefas de deploy
    print("Deploy realizado com sucesso!")

@app.cli.command()
def init_db():
    """
    Inicializa o banco de dados
    Execute: flask init-db
    """
    db.create_all()
    print("Banco de dados inicializado!")

if __name__ == '__main__':
    # Configurações para desenvolvimento
    app.run(
        host='127.0.0.1',    # Localhost
        port=5000,           # Porta padrão do Flask
        debug=True           # Modo debug (recarrega automaticamente quando você salva arquivos)
    )