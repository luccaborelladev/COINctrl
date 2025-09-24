# app/routes/main.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Transaction, Account # Importar modelos necessários
from app import db # Importar a instância do banco de dados

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title='Bem-vindo')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Lógica para calcular o saldo e buscar transações recentes
    # Exemplo básico:
    total_income = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=current_user.id, type='income'
    ).scalar() or 0

    total_expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=current_user.id, type='expense'
    ).scalar() or 0
    
    current_balance = total_income - total_expenses

    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
                                    .order_by(Transaction.date.desc())\
                                    .limit(5).all()

    return render_template(
        'dashboard.html', 
        title='Dashboard', 
        balance=current_balance,
        recent_transactions=recent_transactions
    )

# Você precisará criar os arquivos HTML correspondentes em app/templates/
# - index.html
# - dashboard.html