from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Campos OAuth
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    auth_provider = db.Column(db.String(20), default='local')
    
    def set_password(self, password):
        """Criptografar senha"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, password):
        """Verificar senha"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """Verificar se conta está bloqueada"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def increment_login_attempts(self):
        """Incrementar tentativas de login"""
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
    
    def reset_login_attempts(self):
        """Resetar tentativas de login"""
        self.login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def validate_email(email):
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validar força da senha"""
        if len(password) < 8:
            return False, "Senha deve ter pelo menos 8 caracteres."
        if not re.search(r'[A-Z]', password):
            return False, "Senha deve conter pelo menos uma letra maiúscula."
        if not re.search(r'[a-z]', password):
            return False, "Senha deve conter pelo menos uma letra minúscula."
        if not re.search(r'\d', password):
            return False, "Senha deve conter pelo menos um número."
        return True, "Senha válida."
    
    def __repr__(self):
        return f'<User {self.email}>'

from decimal import Decimal
from enum import Enum

class TransactionType(Enum):
    """Enum para tipos de transação"""
    RECEITA = "receita"
    DESPESA = "despesa"

class Category(db.Model):
    """Modelo para categorias financeiras"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default='#007bff')  # Cor hexadecimal
    icon = db.Column(db.String(50), default='💰')  # Emoji ou classe de ícone
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('categories', lazy=True))
    transactions = db.relationship('Transaction', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'transaction_type': self.transaction_type.value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Transaction(db.Model):
    """Modelo para transações financeiras (receitas e despesas)"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # Valor com 2 casas decimais
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    notes = db.Column(db.Text, nullable=True)
    
    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    
    def __repr__(self):
        return f'<Transaction {self.description} - R\$ {self.amount}>'
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            'id': self.id,
            'description': self.description,
            'amount': float(self.amount),
            'transaction_type': self.transaction_type.value,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'notes': self.notes,
            'category': self.category.to_dict() if self.category else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def formatted_amount(self):
        """Valor formatado em Real brasileiro"""
        return f"R\$ {self.amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def get_balance_by_user(user_id):
        """Calcular saldo total do usuário"""
        receitas = db.session.query(db.func.sum(Transaction.amount)).filter_by(
            user_id=user_id, 
            transaction_type=TransactionType.RECEITA
        ).scalar() or Decimal('0')
        
        despesas = db.session.query(db.func.sum(Transaction.amount)).filter_by(
            user_id=user_id, 
            transaction_type=TransactionType.DESPESA
        ).scalar() or Decimal('0')
        
        return receitas - despesas
    
    @staticmethod
    def get_totals_by_user(user_id):
        """Obter totais de receitas e despesas"""
        receitas = db.session.query(db.func.sum(Transaction.amount)).filter_by(
            user_id=user_id, 
            transaction_type=TransactionType.RECEITA
        ).scalar() or Decimal('0')
        
        despesas = db.session.query(db.func.sum(Transaction.amount)).filter_by(
            user_id=user_id, 
            transaction_type=TransactionType.DESPESA
        ).scalar() or Decimal('0')
        
        return {
            'receitas': receitas,
            'despesas': despesas,
            'saldo': receitas - despesas
        }