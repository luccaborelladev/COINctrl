# app/auth/routes.py - VERSÃO COMPLETA E FUNCIONAL
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import timedelta
import re
import os
import json

# PERMITIR HTTP PARA DESENVOLVIMENTO LOCAL
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de cadastro de usuário"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Capturar dados do formulário
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Lista para armazenar erros
        errors = []
        
        # Validar nome
        if not first_name:
            errors.append('Nome é obrigatório.')
        
        # Validar email
        if not email:
            errors.append('Email é obrigatório.')
        elif not validate_email(email):
            errors.append('Email inválido.')
        
        # Validar senha
        if not password:
            errors.append('Senha é obrigatória.')
        elif len(password) < 6:
            errors.append('Senha deve ter pelo menos 6 caracteres.')
        
        # Validar confirmação de senha
        if not confirm_password:
            errors.append('Confirmação de senha é obrigatória.')
        elif password != confirm_password:
            errors.append('Senhas não coincidem.')
        
        # Verificar se email já existe
        if not errors:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                errors.append('Este email já está cadastrado.')
        
        # Se houver erros, mostrar e retornar
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Tentar criar o usuário
        try:
            # Gerar username único
            username = email.split('@')[0]
            counter = 1
            original_username = username
            
            while User.query.filter_by(username=username).first():
                username = f"{original_username}{counter}"
                counter += 1
            
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                username=username,
                auth_provider='local'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro interno. Tente novamente.', 'error')
            print(f"❌ Erro no cadastro: {e}")
            return render_template('register.html')
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not email or not password:
            flash('Email e senha são obrigatórios.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email ou senha incorretos.', 'error')
            return render_template('login.html')
        
        if user.check_password(password):
            login_user(user, remember=remember_me, duration=timedelta(hours=24))
            flash(f'Bem-vindo, {user.first_name}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Email ou senha incorretos.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    user_name = current_user.first_name if current_user.is_authenticated else 'Usuário'
    session.clear()
    logout_user()
    flash(f'Até logo, {user_name}!', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/google')
def google_login():
    """Iniciar login com Google"""
    try:
        # Carregar credenciais Google
        credential_paths = [
            'google_credentials.json',
            './google_credentials.json',
            os.path.join(os.getcwd(), 'google_credentials.json')
        ]
        
        google_config = None
        for path in credential_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    google_config = json.load(f)
                print(f"✅ Credenciais Google encontradas em: {path}")
                break
        
        if not google_config:
            flash('Credenciais Google não encontradas.', 'error')
            return redirect(url_for('auth.login'))
        
        # Importar bibliotecas Google
        from google_auth_oauthlib.flow import Flow
        
        client_id = google_config['web']['client_id']
        client_secret = google_config['web']['client_secret']
        
        flow = Flow.from_client_config(
            google_config,
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ]
        )
        flow.redirect_uri = 'http://127.0.0.1:5000/auth/google/callback'
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        session['state'] = state
        print(f"🚀 Redirecionando para Google: {authorization_url}")
        return redirect(authorization_url)
        
    except ImportError:
        flash('Bibliotecas Google OAuth não instaladas. Execute: pip install google-auth-oauthlib', 'error')
        return redirect(url_for('auth.login'))
    except Exception as e:
        print(f"❌ Erro no Google login: {e}")
        flash('Erro ao iniciar login com Google.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/google/callback')
def google_callback():
    """Callback do OAuth Google"""
    try:
        from google_auth_oauthlib.flow import Flow
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        
        if 'state' not in session:
            flash('Estado de sessão inválido.', 'error')
            return redirect(url_for('auth.login'))
        
        # Carregar credenciais
        with open('google_credentials.json', 'r') as f:
            google_config = json.load(f)
        
        client_id = google_config['web']['client_id']
        
        flow = Flow.from_client_config(
            google_config,
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ],
            state=session['state']
        )
        flow.redirect_uri = 'http://127.0.0.1:5000/auth/google/callback'
        
        # Obter token
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        # Verificar token ID
        id_info = id_token.verify_oauth2_token(
            credentials._id_token,
            google_requests.Request(),
            client_id
        )
        
        user_email = id_info.get('email')
        user_name = id_info.get('name', '').split()[0] if id_info.get('name') else 'Usuário'
        user_picture = id_info.get('picture')
        google_id = id_info.get('sub')
        
        print(f"📧 Google user: {user_email}, {user_name}")
        
        # Verificar se usuário já existe
        user = User.query.filter_by(email=user_email).first()
        
        if user:
            # Usuário existe - fazer login
            if user.auth_provider != 'google':
                user.auth_provider = 'google'
                user.google_id = google_id
                user.profile_picture = user_picture
                db.session.commit()
            
            login_user(user)
            flash(f'Bem-vindo de volta, {user.first_name}!', 'success')
        else:
            # Criar novo usuário
            username = user_email.split('@')[0]
            counter = 1
            original_username = username
            
            while User.query.filter_by(username=username).first():
                username = f"{original_username}{counter}"
                counter += 1
            
            new_user = User(
                email=user_email,
                first_name=user_name,
                username=username,
                auth_provider='google',
                google_id=google_id,
                profile_picture=user_picture
            )
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash(f'Conta criada com sucesso! Bem-vindo, {user_name}!', 'success')
        
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        print(f"❌ Erro no callback Google: {e}")
        flash('Erro ao processar login com Google.', 'error')
        return redirect(url_for('auth.login'))