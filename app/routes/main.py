# app/routes/main.py
from flask import Blueprint
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>COINctrl - Teste</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f0f0f0; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🪙 COINctrl</h1>
            <p>Bem-vindo ao seu controle financeiro pessoal!</p>
            <p><strong>Status:</strong> Aplicação funcionando! ✅</p>
            
            <div>
                <a href="/auth/login" class="btn">Fazer Login</a>
                <a href="/auth/register" class="btn">Cadastrar</a>
                <a href="/test" class="btn" style="background: #28a745;">Página de Teste</a>
            </div>
            
            <hr>
            <small>Servidor Flask rodando em modo desenvolvimento</small>
        </div>
    </body>
    </html>
    '''

@main_bp.route('/test')
def test():
    return '''
    <h1>✅ Teste Funcionando!</h1>
    <p>O Flask está rodando corretamente.</p>
    <p><a href="/">← Voltar para a página inicial</a></p>
    '''