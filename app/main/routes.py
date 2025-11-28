# app/main/routes.py
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.main import main_bp
from app.models import Transaction

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
            <small>Sistema de autenticação e financeiro implementado com Flask</small>
        </div>
    </body>
    </html>
    '''

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal do usuário"""
    # Obter estatísticas financeiras básicas
    totals = Transaction.get_totals_by_user(current_user.id)
    total_transactions = Transaction.query.filter_by(user_id=current_user.id).count()
    
    return render_template('dashboard.html', 
                         user=current_user,
                         totals=totals,
                         total_transactions=total_transactions)