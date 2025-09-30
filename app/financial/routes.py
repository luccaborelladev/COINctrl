from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError  # ✅ CORREÇÃO
from app.financial import financial_bp
from app import db
from app.models import Category, Transaction, TransactionType
from datetime import datetime
from decimal import Decimal

@financial_bp.route('/')
@login_required
def dashboard():
    """Dashboard financeiro principal"""
    # Obter estatísticas do usuário
    totals = Transaction.get_totals_by_user(current_user.id)
    
    # Contar categorias e transações
    total_categories = Category.query.filter_by(user_id=current_user.id).count()
    total_transactions = Transaction.query.filter_by(user_id=current_user.id).count()
    
    # Últimas 5 transações
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc()).limit(5).all()
    
    return render_template('financial/dashboard.html',
                         totals=totals,
                         total_categories=total_categories,
                         total_transactions=total_transactions,
                         recent_transactions=recent_transactions)

# === CRUD DE CATEGORIAS ===

@financial_bp.route('/categories')
@login_required  
def categories():
    """Listar categorias do usuário"""
    # Aplicar filtros se fornecidos
    search = request.args.get('search', '').strip()
    type_filter = request.args.get('type', '')
    
    # Query base
    query = Category.query.filter_by(user_id=current_user.id)
    
    # Aplicar filtro de busca
    if search:
        query = query.filter(Category.name.ilike(f'%{search}%'))
    
    # Aplicar filtro de tipo
    if type_filter and type_filter in ['receita', 'despesa']:
        query = query.filter_by(transaction_type=TransactionType(type_filter))
    
    # Obter todas as categorias filtradas
    categories = query.order_by(Category.transaction_type, Category.name).all()
    
    # Separar por tipo para estatísticas
    receita_categories = [c for c in categories if c.transaction_type == TransactionType.RECEITA]
    despesa_categories = [c for c in categories if c.transaction_type == TransactionType.DESPESA]
    
    return render_template('financial/categories.html',
                         categories=categories,  # ✅ ADICIONADO
                         receita_categories=receita_categories,
                         despesa_categories=despesa_categories)

@financial_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
def new_category():
    """Criar nova categoria"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#007bff')
        icon = request.form.get('icon', '💰')
        transaction_type = request.form.get('transaction_type')
        
        # Validações
        if not name:
            flash('Nome da categoria é obrigatório!', 'danger')
            return redirect(url_for('financial.new_category'))
            
        if transaction_type not in ['receita', 'despesa']:
            flash('Tipo de transação inválido!', 'danger')
            return redirect(url_for('financial.new_category'))
        
        # Verificar se já existe categoria com esse nome
        existing = Category.query.filter_by(
            user_id=current_user.id,
            name=name,
            transaction_type=TransactionType(transaction_type)
        ).first()
        
        if existing:
            flash(f'Já existe uma categoria "{name}" para {transaction_type}!', 'warning')
            return redirect(url_for('financial.new_category'))
        
        # Criar categoria
        category = Category(
            name=name,
            description=description,
            color=color,
            icon=icon,
            transaction_type=TransactionType(transaction_type),
            user_id=current_user.id
        )
        
        try:
            db.session.add(category)
            db.session.commit()
            flash(f'Categoria "{name}" criada com sucesso!', 'success')
            return redirect(url_for('financial.categories'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar categoria. Tente novamente.', 'danger')
            return redirect(url_for('financial.new_category'))
    
    return render_template('financial/category_form.html', category=None)

@financial_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """Editar categoria existente"""
    category = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#007bff')
        icon = request.form.get('icon', '💰')
        
        # Validações
        if not name:
            flash('Nome da categoria é obrigatório!', 'danger')
            return redirect(url_for('financial.edit_category', id=id))
        
        # Verificar se já existe outra categoria com esse nome
        existing = Category.query.filter_by(
            user_id=current_user.id,
            name=name,
            transaction_type=category.transaction_type
        ).filter(Category.id != id).first()
        
        if existing:
            flash(f'Já existe outra categoria "{name}" para {category.transaction_type.value}!', 'warning')
            return redirect(url_for('financial.edit_category', id=id))
        
        # Atualizar categoria
        category.name = name
        category.description = description
        category.color = color
        category.icon = icon
        
        try:
            db.session.commit()
            flash(f'Categoria "{name}" atualizada com sucesso!', 'success')
            return redirect(url_for('financial.categories'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar categoria. Tente novamente.', 'danger')
    
    return render_template('financial/category_form.html', category=category)

@financial_bp.route('/categories/<int:id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_category(id):
    """
    Exclui uma categoria específica
    
    Args:
        id (int): ID da categoria a ser excluída
        
    Returns:
        Response: Redirecionamento para lista de categorias
        
    Raises:
        404: Se categoria não for encontrada
        400: Se categoria possui transações
    """
    try:
        # Buscar categoria
        category = Category.query.filter_by(
            id=id, 
            user_id=current_user.id
        ).first()
        
        if not category:
            flash('Categoria não encontrada.', 'error')
            return redirect(url_for('financial.categories'))
        
        # Verificar se categoria possui transações
        transaction_count = Transaction.query.filter_by(category_id=id).count()
        if transaction_count > 0:
            flash(f'Não é possível excluir a categoria "{category.name}" porque ela possui {transaction_count} transação(ões) associada(s).', 'warning')
            return redirect(url_for('financial.categories'))
        
        # Excluir categoria
        category_name = category.name
        db.session.delete(category)
        db.session.commit()
        
        flash(f'Categoria "{category_name}" excluída com sucesso!', 'success')
        
    except IntegrityError as e:
        db.session.rollback()
        flash('Erro de integridade: Não é possível excluir categoria com transações associadas.', 'error')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro interno: {str(e)}', 'error')
        
    return redirect(url_for('financial.categories'))

# === CRUD DE TRANSAÇÕES ===

@financial_bp.route('/transactions')
@login_required  
def transactions():
    """Listar transações do usuário"""
    # Aplicar filtros
    search = request.args.get('search', '').strip()
    type_filter = request.args.get('type', '')
    category_filter = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Query base
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Aplicar filtro de busca
    if search:
        query = query.filter(Transaction.description.ilike(f'%{search}%'))
    
    # Aplicar filtro de tipo
    if type_filter and type_filter in ['receita', 'despesa']:
        query = query.filter_by(transaction_type=TransactionType(type_filter))
    
    # Aplicar filtro de categoria
    if category_filter and category_filter.isdigit():
        query = query.filter_by(category_id=int(category_filter))
    
    # Aplicar filtros de data
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Transaction.transaction_date <= date_to_obj)
        except ValueError:
            pass
    
    # Obter transações
    transactions = query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc()).all()
    
    # Obter categorias para filtro
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    
    # Obter totais
    totals = Transaction.get_totals_by_user(current_user.id)
    
    return render_template('financial/transactions.html',
                         transactions=transactions,
                         categories=categories,
                         totals=totals) 

@financial_bp.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def new_transaction():
    """Criar nova transação"""
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        amount = request.form.get('amount', '').strip()
        transaction_type = request.form.get('transaction_type')
        category_id = request.form.get('category_id')
        transaction_date = request.form.get('transaction_date')
        notes = request.form.get('notes', '').strip()
        
        # Validações
        if not description:
            flash('Descrição é obrigatória!', 'danger')
            return redirect(url_for('financial.new_transaction'))
            
        if not amount:
            flash('Valor é obrigatório!', 'danger')
            return redirect(url_for('financial.new_transaction'))
            
        try:
            amount = Decimal(amount)
            if amount <= 0:
                flash('Valor deve ser maior que zero!', 'danger')
                return redirect(url_for('financial.new_transaction'))
        except:
            flash('Valor inválido!', 'danger')
            return redirect(url_for('financial.new_transaction'))
            
        if transaction_type not in ['receita', 'despesa']:
            flash('Tipo de transação inválido!', 'danger')
            return redirect(url_for('financial.new_transaction'))
            
        if not category_id or not category_id.isdigit():
            flash('Categoria é obrigatória!', 'danger')
            return redirect(url_for('financial.new_transaction'))
            
        # Verificar se categoria pertence ao usuário
        category = Category.query.filter_by(
            id=int(category_id), 
            user_id=current_user.id,
            transaction_type=TransactionType(transaction_type)
        ).first()
        
        if not category:
            flash('Categoria inválida!', 'danger')
            return redirect(url_for('financial.new_transaction'))
            
        if not transaction_date:
            flash('Data da transação é obrigatória!', 'danger')
            return redirect(url_for('financial.new_transaction'))
            
        try:
            transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
        except:
            flash('Data inválida!', 'danger')
            return redirect(url_for('financial.new_transaction'))
        
        # Criar transação
        transaction = Transaction(
            description=description,
            amount=amount,
            transaction_type=TransactionType(transaction_type),
            category_id=category.id,
            transaction_date=transaction_date,
            notes=notes,
            user_id=current_user.id
        )
        
        try:
            db.session.add(transaction)
            db.session.commit()
            flash(f'Transação "{description}" criada com sucesso!', 'success')
            return redirect(url_for('financial.transactions'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar transação. Tente novamente.', 'danger')
            return redirect(url_for('financial.new_transaction'))
    
    return render_template('financial/transaction_form.html', transaction=None)

@financial_bp.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    """Editar transação existente"""
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        amount = request.form.get('amount', '').strip()
        transaction_type = request.form.get('transaction_type')
        category_id = request.form.get('category_id')
        transaction_date = request.form.get('transaction_date')
        notes = request.form.get('notes', '').strip()
        
        # Validações (mesmo código da criação)
        if not description:
            flash('Descrição é obrigatória!', 'danger')
            return redirect(url_for('financial.edit_transaction', id=id))
            
        try:
            amount = Decimal(amount)
            if amount <= 0:
                flash('Valor deve ser maior que zero!', 'danger')
                return redirect(url_for('financial.edit_transaction', id=id))
        except:
            flash('Valor inválido!', 'danger')
            return redirect(url_for('financial.edit_transaction', id=id))
            
        # Verificar categoria
        category = Category.query.filter_by(
            id=int(category_id), 
            user_id=current_user.id,
            transaction_type=TransactionType(transaction_type)
        ).first()
        
        if not category:
            flash('Categoria inválida!', 'danger')
            return redirect(url_for('financial.edit_transaction', id=id))
            
        try:
            transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
        except:
            flash('Data inválida!', 'danger')
            return redirect(url_for('financial.edit_transaction', id=id))
        
        # Atualizar transação
        transaction.description = description
        transaction.amount = amount
        transaction.transaction_type = TransactionType(transaction_type)
        transaction.category_id = category.id
        transaction.transaction_date = transaction_date
        transaction.notes = notes
        
        try:
            db.session.commit()
            flash(f'Transação "{description}" atualizada com sucesso!', 'success')
            return redirect(url_for('financial.transactions'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar transação. Tente novamente.', 'danger')
    
    return render_template('financial/transaction_form.html', transaction=transaction)

# === API ENDPOINTS ===

@financial_bp.route('/api/categories/<transaction_type>')
@login_required
def api_categories_by_type(transaction_type):
    """API para obter categorias por tipo"""
    if transaction_type not in ['receita', 'despesa']:
        return jsonify({'error': 'Tipo inválido'}), 400
    
    categories = Category.query.filter_by(
        user_id=current_user.id,
        transaction_type=TransactionType(transaction_type)
    ).order_by(Category.name).all()
    
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'icon': cat.icon,
        'color': cat.color
    } for cat in categories])

@financial_bp.route('/transactions/<int:id>/delete', methods=['POST', 'DELETE'])
@login_required
def delete_transaction(id):
    """Excluir transação"""
    try:
        transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()
        
        if not transaction:
            flash('Transação não encontrada.', 'error')
            return redirect(url_for('financial.transactions'))
        
        transaction_desc = transaction.description
        db.session.delete(transaction)
        db.session.commit()
        
        flash(f'Transação "{transaction_desc}" excluída com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir transação: {str(e)}', 'error')
        
    return redirect(url_for('financial.transactions'))