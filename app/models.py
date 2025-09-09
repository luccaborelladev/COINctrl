from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Adicionando email
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # Para desativar usuários se necessário
    
    # Relacionamento com transações (para futuras funcionalidades)
    # transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    def set_password(self, password):
        """Cria um hash seguro para a senha usando PBKDF2"""
        # O Werkzeug usa PBKDF2 por padrão, que é seguro
        # Você pode especificar o método explicitamente:
        self.password_hash = generate_password_hash(
            password, 
            method='pbkdf2:sha256',  # Método explícito
            salt_length=16           # Tamanho do salt
        )
    
    def check_password(self, password):
        """Verifica se a senha fornecida está correta"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Retorna o ID do usuário como string (requerido pelo Flask-Login)"""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """Retorna True se o usuário está autenticado"""
        return True
    
    @property
    def is_anonymous(self):
        """Retorna True se o usuário é anônimo"""
        return False

    def __repr__(self):
        return f'<User {self.username}>'

# Callback obrigatório do Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Carrega um usuário pelo ID"""
    return User.query.get(int(user_id))