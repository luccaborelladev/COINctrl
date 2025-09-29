# app/main/routes.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>COINctrl</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; text-align: center; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .btn { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
            .btn:hover { background: #0056b3; }
            .btn-success { background: #28a745; }
            .btn-success:hover { background: #1e7e34; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🪙 COINctrl</h1>
            <p>Sistema de Controle Financeiro</p>
            <p><strong>Status:</strong> Aplicação funcionando! ✅</p>
            
            <div>
                <a href="/auth/login" class="btn">Fazer Login</a>
                <a href="/auth/register" class="btn btn-success">Cadastrar</a>
            </div>
            
            <hr style="margin: 30px 0;">
            <small>Sistema de autenticação implementado com Flask</small>
        </div>
    </body>
    </html>
    '''

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard do usuário"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - COINctrl</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
            .btn {{ background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            .btn:hover {{ background: #c82333; }}
            .welcome {{ background: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🪙 COINctrl - Dashboard</h1>
                <a href="{url_for('auth.logout')}" class="btn">Logout</a>
            </div>
            
            <div class="welcome">
                <h2>Bem-vindo, {current_user.first_name}! 🎉</h2>
                <p><strong>Email:</strong> {current_user.email}</p>
                <p><strong>Username:</strong> {current_user.username}</p>
            </div>
            
            <div>
                <h3>Sistema de Autenticação Funcionando! ✅</h3>
                <p>Você está logado com sucesso no COINctrl.</p>
                
                <h4>Funcionalidades Implementadas:</h4>
                <ul>
                    <li>✅ Cadastro de usuários</li>
                    <li>✅ Login/Logout seguro</li>
                    <li>✅ Senhas criptografadas</li>
                    <li>✅ Gerenciamento de sessão</li>
                    <li>✅ OAuth Google (se configurado)</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''