# app/routes/categories.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Category # Importar modelo
from app import db # Importar a instância do banco de dados

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('O nome da categoria é obrigatório.', 'danger')
            return render_template('categories/add_category.html')
        
        new_category = Category(name=name, user_id=current_user.id)
        db.session.add(new_category)
        db.session.commit()
        flash('Categoria adicionada com sucesso!', 'success')
        return redirect(url_for('categories.list_categories'))
    return render_template('categories/add_category.html', title='Adicionar Categoria')

@categories_bp.route('/list')
@login_required
def list_categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('categories/list_categories.html', title='Minhas Categorias', categories=categories)

@categories_bp.route('/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        flash('Você não tem permissão para editar esta categoria.', 'danger')
        return redirect(url_for('categories.list_categories'))

    if request.method == 'POST':
        category.name = request.form.get('name')
        if not category.name:
            flash('O nome da categoria é obrigatório.', 'danger')
            return render_template('categories/edit_category.html', category=category)
        db.session.commit()
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('categories.list_categories'))
    return render_template('categories/edit_category.html', title='Editar Categoria', category=category)

@categories_bp.route('/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        flash('Você não tem permissão para deletar esta categoria.', 'danger')
        return redirect(url_for('categories.list_categories'))
    
    # Opcional: verificar se existem transações associadas antes de deletar
    if category.transactions:
        flash('Não é possível deletar uma categoria com transações associadas.', 'danger')
        return redirect(url_for('categories.list_categories'))

    db.session.delete(category)
    db.session.commit()
    flash('Categoria deletada com sucesso!', 'success')
    return redirect(url_for('categories.list_categories'))

# Você precisará criar os arquivos HTML correspondentes em app/templates/categories/
# - add_category.html
# - list_categories.html
# - edit_category.html