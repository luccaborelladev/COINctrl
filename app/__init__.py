from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Inicialização das extensões (globalmente, fora da função create_app)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='default'):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Importar e aplicar configurações
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Inicializar extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Importar modelos (IMPORTANTE: deve estar dentro da função)
    from app.models import User, Category, Transaction, Account
    
    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints (rotas)
    from app.routes.auth import auth_bp
    from app.routes.transaction import transactions_bp
    from app.routes.categories import categories_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    
    return app