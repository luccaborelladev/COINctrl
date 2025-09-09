from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from . import db
from .models import User
import re

auth_routes = Blueprint("auth", __name__)

def validate_password(password):
    """Valida se a senha atende aos critérios de segurança"""
    if len(password) < 8:
        return False, "Senha deve ter pelo menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "Senha deve conter pelo menos uma letra maiúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "Senha deve conter pelo menos uma letra minúscula"
    
    if not re.search(r'\d', password):
        return False, "Senha deve conter pelo menos um número"
    
    return True, "Senha válida"

def validate_email(email):
    """Valida formato do email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_routes.route("/login", methods=['GET', 'POST'])
def login():
    """Rota de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = bool(request.form.get('remember_me'))
        
        # Validações básicas
        if not username or not password:
            flash('Por favor, preencha todos os campos', 'error')
            return render_template('auth/login.html')
        
        # Busca usuário
        user = User.query.filter_by(username=username).first()
        
        # Verifica credenciais
        if user is None or not user.check_password(password):
            flash('Usuário ou senha incorretos', 'error')
            return render_template('auth/login.html')
        
        # Verifica se usuário está ativo
        if not user.is_active:
            flash('Conta desativada. Entre em contato com o suporte', 'error')
            return render_template('auth/login.html')
        
        # Faz login
        login_user(user, remember=remember_me)
        
        # Redireciona para página solicitada ou dashboard
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')  # Você criará essa rota
        
        flash('Login realizado com sucesso!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth_routes.route("/register", methods=['GET', 'POST'])
def register():
    """Rota de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validações
        errors = []
        
        if not all([username, email, password, password_confirm]):
            errors.append('Todos os campos são obrigatórios')
        
        if len(username) < 3:
            errors.append('Nome de usuário deve ter pelo menos 3 caracteres')
        
        if not validate_email(email):
            errors.append('Email inválido')
        
        if password != password_confirm:
            errors.append('Senhas não conferem')
        
        is_valid_password, password_message = validate_password(password)
        if not is_valid_password:
            errors.append(password_message)
        
        # Verifica se usuário ou email já existe
        if User.query.filter_by(username=username).first():
            errors.append('Nome de usuário já existe')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email já está em uso')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Cria novo usuário
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Cadastro realizado com sucesso! Faça login', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro interno. Tente novamente', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_routes.route("/logout")
@login_required
def logout():
    """Rota de logout"""
    logout_user()
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('main.index'))

@auth_routes.route("/profile")
@login_required
def profile():
    """Página de perfil do usuário"""
    return render_template('auth/profile.html', user=current_user)

@auth_routes.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    """Alterar senha"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validações
        if not current_user.check_password(current_password):
            flash('Senha atual incorreta', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('Novas senhas não conferem', 'error')
            return render_template('auth/change_password.html')
        
        is_valid, message = validate_password(new_password)
        if not is_valid:
            flash(message, 'error')
            return render_template('auth/change_password.html')
        
        # Atualiza senha
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')

# Middleware personalizado para roles (futuro)
def admin_required(f):
    """Decorator para rotas que requerem admin"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Aqui você pode adicionar lógica de roles
        # if not current_user.is_admin:
        #     flash('Acesso negado', 'error')
        #     return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function