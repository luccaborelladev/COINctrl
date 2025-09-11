from flask import Flask
from .routes import routes
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from .models import db, login_manager

def create_app():  
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///labsoftware.db'  # Exemplo usando SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    login_manager.init_app(app)
    # ...restante da configuração...
    return app
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", default="devkey-change-in-production")
    database_url = os.getenv("DATABASE_URL", default="sqlite:///cointrl.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configurações de segurança
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    
    # Registra blueprints
    from .routes import main_blueprint
    from .auth import auth_routes
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_routes, url_prefix='/auth')
    
    # Cria tabelas no contexto da aplicação
    with app.app_context():
        db.create_all()
    
    return app

# Mantém função original para compatibilidade
def setup_flask_app():
    return create_app()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///labsoftware.db'  # Exemplo usando SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    login_manager.init_app(app)
    return app