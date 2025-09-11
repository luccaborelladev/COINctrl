from flask import Blueprint, render_template
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from .models import User, Category, Transaction, Budget, Goal

main_blueprint = Blueprint('main', __name__)
routes = Blueprint("routes", __name__)

@routes.route("/")
def welcome():
    return render_template("index.html")

@routes.route("/login")
def login():
    return render_template("login.html")

@main_blueprint.route('/')
def index():
    """Página inicial"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_blueprint.route('/dashboard')
@login_required
def dashboard():
    from . import db
    """Dashboard principal"""
    # Dados resumidos para o dashboard
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc()).limit(5).all()
    
    total_income = db.session.query(db.func.coalesce(db.func.sum(Transaction.amount), 0))\
        .filter_by(user_id=current_user.id, type='income').scalar()
    
    total_expense = db.session.query(db.func.coalesce(db.func.sum(Transaction.amount), 0))\
        .filter_by(user_id=current_user.id, type='expense').scalar()
    
    balance = float(total_income - total_expense)
    
    return render_template('dashboard/index.html',
                         recent_transactions=recent_transactions,
                         total_income=float(total_income),
                         total_expense=float(total_expense),
                         balance=balance)

@main_blueprint.route('/transactions')
@login_required
def transactions():
    """Lista todas as transações"""
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.transaction_date.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    categories = Category.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    return render_template('dashboard/transactions.html',
                         transactions=transactions,
                         categories=categories)

@main_blueprint.route('/categories')
@login_required
def categories():
    """Gerenciamento de categorias"""
    income_categories = Category.query.filter_by(user_id=current_user.id, type='income', is_active=True).all()
    expense_categories = Category.query.filter_by(user_id=current_user.id, type='expense', is_active=True).all()
    
    return render_template('dashboard/categories.html',
                         income_categories=income_categories,
                         expense_categories=expense_categories)

@main_blueprint.route('/budgets')
@login_required
def budgets():
    """Gerenciamento de orçamentos"""
    active_budgets = Budget.query.filter_by(user_id=current_user.id, is_active=True).all()
    categories = Category.query.filter_by(user_id=current_user.id, type='expense', is_active=True).all()
    
    return render_template('dashboard/budgets.html',
                         budgets=active_budgets,
                         categories=categories)

@main_blueprint.route('/goals')
@login_required
def goals():
    """Gerenciamento de metas"""
    active_goals = Goal.query.filter_by(user_id=current_user.id).filter(
        Goal.status.in_(['active', 'paused'])).all()
    completed_goals = Goal.query.filter_by(user_id=current_user.id, status='completed').all()
    
    return render_template('dashboard/goals.html',
                         active_goals=active_goals,
                         completed_goals=completed_goals)

# Rotas API serão implementadas nos arquivos da pasta api/