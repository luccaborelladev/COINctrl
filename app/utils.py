from datetime import datetime, date, timedelta
from decimal import Decimal
from .models import Category

def create_default_categories(user_id):
    """Cria categorias padrão para um novo usuário"""
    from . import db
    
    default_categories = [
        # Receitas
        {'name': 'Salário', 'type': 'income', 'color': '#27ae60', 'icon': 'dollar-sign'},
        {'name': 'Freelance', 'type': 'income', 'color': '#2ecc71', 'icon': 'briefcase'},
        {'name': 'Investimentos', 'type': 'income', 'color': '#16a085', 'icon': 'trending-up'},
        {'name': 'Outros', 'type': 'income', 'color': '#1abc9c', 'icon': 'plus'},
        
        # Despesas
        {'name': 'Alimentação', 'type': 'expense', 'color': '#e74c3c', 'icon': 'utensils'},
        {'name': 'Transporte', 'type': 'expense', 'color': '#f39c12', 'icon': 'car'},
        {'name': 'Moradia', 'type': 'expense', 'color': '#8e44ad', 'icon': 'home'},
        {'name': 'Saúde', 'type': 'expense', 'color': '#e67e22', 'icon': 'heart'},
        {'name': 'Educação', 'type': 'expense', 'color': '#3498db', 'icon': 'book'},
        {'name': 'Lazer', 'type': 'expense', 'color': '#9b59b6', 'icon': 'gamepad-2'},
        {'name': 'Compras', 'type': 'expense', 'color': '#e91e63', 'icon': 'shopping-bag'},
        {'name': 'Outros', 'type': 'expense', 'color': '#95a5a6', 'icon': 'tag'},
    ]
    
    for cat_data in default_categories:
        category = Category(
            user_id=user_id,
            name=cat_data['name'],
            type=cat_data['type'],
            color=cat_data['color'],
            icon=cat_data['icon'],
            is_default=True
        )
        db.session.add(category)
    
    db.session.commit()

def format_currency(value):
    """Formata valor monetário para BRL"""
    if value is None:
        return "R$ 0,00"
    return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def get_date_range(period):
    """Retorna range de datas baseado no período"""
    today = date.today()
    
    if period == 'this_month':
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    elif period == 'last_month':
        if today.month == 1:
            start = today.replace(year=today.year - 1, month=12, day=1)
            end = today.replace(day=1) - timedelta(days=1)
        else:
            start = today.replace(month=today.month - 1, day=1)
            end = today.replace(day=1) - timedelta(days=1)
    elif period == 'this_year':
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
    else:  # all_time
        start = None
        end = None
    
    return start, end