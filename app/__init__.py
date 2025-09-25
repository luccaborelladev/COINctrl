from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import config # Assumindo que config.py está em app/config.py
from app.models import User, Category, Transaction, Account 

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='default'):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config.from_object(config[config_name])
    
    # Inicializar extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Redireciona para 'auth.login' se não logado
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Importar modelos (para que o Flask-Migrate os reconheça)
    # É uma boa prática importar os modelos aqui para que o db.create_all() ou Flask-Migrate os encontre.
    from app.models import User, Category, Transaction, Account
    
    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        # Retorna o objeto User com base no ID
        return User.query.get(int(user_id))
    
    # Registrar blueprints (rotas)
    # Importar os blueprints DENTRO da função create_app para evitar problemas de importação circular
    from app.routes.auth import auth_bp
    from app.routes.transaction import transactions_bp
    from app.routes.categories import categories_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    
    return app

# Opcional: Se você quiser um ponto de entrada simples para o shell ou para rodar diretamente
# from app.config import DevelopmentConfig
# app = create_app(DevelopmentConfig)