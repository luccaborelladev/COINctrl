from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import os

db = SQLAlchemy()
login_manager = LoginManager()  
login_manager.login_view = 'auth.login'
login_manager.login_message = "Login necessário para acessar esta página!"

def setup_flask_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", default="devkey")
    database_url = os.getenv("DATABASE_URL", default="sqlite:///cointrl.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import main_blueprint
    from .auth import auth_routes
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_routes, url_prefix='/auth')

    return app

