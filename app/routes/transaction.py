# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User # Importa o modelo User
from app import db # Importa a instância do banco de dados

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Assumindo que você está enviando dados de formulário HTML
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validação de Dados (Backend)
        if not email or not password or not confirm_password:
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado. Por favor, use outro.', 'warning')
            return render_template('auth/register.html')
        
        # Criar e Salvar Usuário
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Sua conta foi criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', title='Registrar')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user) # Inicia a sessão do usuário
            flash('Login bem-sucedido!', 'success')
            next_page = request.args.get('next') # Redireciona para a página anterior, se houver
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Email ou senha inválidos. Por favor, tente novamente.', 'danger')
            
    return render_template('auth/login.html', title='Login')

@auth_bp.route('/logout')
@login_required # Apenas usuários logados podem fazer logout
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

# Você precisará criar os arquivos HTML correspondentes em app/templates/auth/
# - register.html
# - login.html