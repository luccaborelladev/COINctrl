from app import db 
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum
import re

db = SQLAlchemy()

class TransactionType(Enum):
    """Tipos de transação"""
    INCOME = "receita"
    EXPENSE = "despesa"

class AccountType(Enum):
    """Tipos de conta""" 
    CHECKING = "conta_corrente"
    SAVINGS = "poupanca"
    CREDIT = "cartao_credito"
    CASH = "dinheiro"

class User(UserMixin, db.Model):
    """Modelo de usuário"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    accounts = db.relationship('Account', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Gera hash da senha"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def validate_email(email):
        """Valida formato do email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def get_balance(self):
        """Calcula saldo total do usuário"""
        total_income = sum(t.amount for t in self.transactions if t.transaction_type == TransactionType.INCOME)
        total_expense = sum(t.amount for t in self.transactions if t.transaction_type == TransactionType.EXPENSE)
        return total_income - total_expense
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    """Modelo de categoria"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default="#4CAF50")  # Hex color
    icon = db.Column(db.String(50), default="💰")
    is_default = db.Column(db.Boolean, default=False)  # Categorias padrão do sistema
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    
    # Constraint para evitar nomes duplicados por usuário
    __table_args__ = (db.UniqueConstraint('name', 'user_id', name='unique_category_per_user'),)
    
    @staticmethod
    def create_default_categories(user_id):
        """Cria categorias padrão para um novo usuário"""
        default_categories = [
            {'name': 'Alimentação', 'color': '#FF5722', 'icon': '🍔'},
            {'name': 'Transporte', 'color': '#2196F3', 'icon': '🚗'},
            {'name': 'Moradia', 'color': '#9C27B0', 'icon': '🏠'},
            {'name': 'Saúde', 'color': '#F44336', 'icon': '⚕️'},
            {'name': 'Educação', 'color': '#607D8B', 'icon': '📚'},
            {'name': 'Lazer', 'color': '#FF9800', 'icon': '🎮'},
            {'name': 'Salário', 'color': '#4CAF50', 'icon': '💼'},
            {'name': 'Freelance', 'color': '#8BC34A', 'icon': '💻'},
        ]
        
        categories = []
        for cat_data in default_categories:
            category = Category(
                name=cat_data['name'],
                color=cat_data['color'],
                icon=cat_data['icon'],
                is_default=True,
                user_id=user_id
            )
            categories.append(category)
        
        return categories
    
    def get_total_amount(self, transaction_type=None, start_date=None, end_date=None):
        """Calcula total gasto/ganho nesta categoria"""
        query = self.transactions
        
        if transaction_type:
            query = [t for t in query if t.transaction_type == transaction_type]
        if start_date:
            query = [t for t in query if t.date >= start_date]
        if end_date:
            query = [t for t in query if t.date <= end_date]
            
        return sum(t.amount for t in query)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat(),
            'transactions_count': len(self.transactions)
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Transaction(db.Model):
    """Modelo de transação"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)  # Observações adicionais
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    
    # Índices para melhor performance
    __table_args__ = (
        db.Index('idx_transaction_user_date', 'user_id', 'date'),
        db.Index('idx_transaction_type', 'transaction_type'),
        db.Index('idx_transaction_category', 'category_id'),
    )
    
    def validate_amount(self):
        """Valida se o valor é positivo"""
        return self.amount > 0
    
    @staticmethod
    def get_monthly_summary(user_id, year, month):
        """Retorna resumo mensal das transações"""
        from sqlalchemy import extract, func
        
        query = db.session.query(
            Transaction.transaction_type,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            extract('year', Transaction.date) == year,
            extract('month', Transaction.date) == month
        ).group_by(Transaction.transaction_type)
        
        result = {'income': 0, 'expense': 0}
        for row in query:
            if row.transaction_type == TransactionType.INCOME:
                result['income'] = float(row.total)
            else:
                result['expense'] = float(row.total)
        
        result['balance'] = result['income'] - result['expense']
        return result
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'description': self.description,
            'amount': float(self.amount),
            'transaction_type': self.transaction_type.value,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes,
            'category': self.category.to_dict() if self.category else None,
            'account': self.account.to_dict() if self.account else None
        }
    
    def __repr__(self):
        return f'<Transaction {self.description}: {self.amount}>'

class Account(db.Model):
    """Modelo de conta/carteira"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    initial_balance = db.Column(db.Numeric(10, 2), default=0.00)
    current_balance = db.Column(db.Numeric(10, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    transactions = db.relationship('Transaction', backref='account', lazy=True)
    
    # Constraint para evitar nomes duplicados por usuário
    __table_args__ = (db.UniqueConstraint('name', 'user_id', name='unique_account_per_user'),)
    
    def update_balance(self):
        """Atualiza saldo baseado nas transações"""
        income = sum(t.amount for t in self.transactions if t.transaction_type == TransactionType.INCOME)
        expense = sum(t.amount for t in self.transactions if t.transaction_type == TransactionType.EXPENSE)
        self.current_balance = self.initial_balance + income - expense
        db.session.commit()
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'account_type': self.account_type.value,
            'initial_balance': float(self.initial_balance),
            'current_balance': float(self.current_balance),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'description': self.description,
            'transactions_count': len(self.transactions)
        }
    
    def __repr__(self):
        return f'<Account {self.name}: {self.current_balance}>'

# Eventos para atualizar saldos automaticamente
from sqlalchemy import event

@event.listens_for(Transaction, 'after_insert')
def update_account_balance_insert(mapper, connection, target):
    """Atualiza saldo da conta após inserir transação"""
    if target.account:
        target.account.update_balance()

@event.listens_for(Transaction, 'after_update')
def update_account_balance_update(mapper, connection, target):
    """Atualiza saldo da conta após atualizar transação"""
    if target.account:
        target.account.update_balance()

@event.listens_for(Transaction, 'after_delete')
def update_account_balance_delete(mapper, connection, target):
    """Atualiza saldo da conta após deletar transação"""
    if target.account:
        target.account.update_balance()