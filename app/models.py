from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from decimal import Decimal

db = SQLAlchemy()
login_manager = LoginManager()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    birth_date = db.Column(db.Date)
    profile_picture = db.Column(db.String(255))
    currency = db.Column(db.String(3), default='BRL')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password, 
            method='pbkdf2:sha256',  
            salt_length=16          
        )
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_balance(self):
        """Calcula o saldo atual do usuário"""
        income = db.session.query(db.func.coalesce(db.func.sum(Transaction.amount), 0)).\
            filter_by(user_id=self.id, type='income').scalar()
        expense = db.session.query(db.func.coalesce(db.func.sum(Transaction.amount), 0)).\
            filter_by(user_id=self.id, type='expense').scalar()
        return float(income - expense)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3498db')
    icon = db.Column(db.String(50), default='tag')
    type = db.Column(db.String(20), nullable=False)  # 'income' ou 'expense'
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', 'type', name='unique_user_category'),
        db.CheckConstraint("type IN ('income', 'expense')", name='check_category_type')
    )
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' ou 'expense'
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    transaction_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_frequency = db.Column(db.String(20))  # 'daily', 'weekly', 'monthly', 'yearly'
    recurring_end_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    tags = db.Column(db.String(255))
    location = db.Column(db.String(255))
    receipt_path = db.Column(db.String(255))
    is_confirmed = db.Column(db.Boolean, default=True)
    parent_transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'))
    
    # Relacionamentos
    child_transactions = db.relationship('Transaction', backref=db.backref('parent', remote_side=[id]))
    goal_contributions = db.relationship('GoalContribution', backref='transaction', lazy=True)
    
    __table_args__ = (
        db.CheckConstraint("type IN ('income', 'expense')", name='check_transaction_type'),
        db.CheckConstraint("amount > 0", name='check_positive_amount'),
        db.CheckConstraint("recurring_frequency IN ('daily', 'weekly', 'monthly', 'yearly') OR recurring_frequency IS NULL", 
                         name='check_recurring_frequency')
    )
    
    @property
    def formatted_amount(self):
        return f"R$ {self.amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def __repr__(self):
        return f'<Transaction {self.description} - {self.amount}>'

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    period = db.Column(db.String(20), nullable=False)  # 'weekly', 'monthly', 'yearly'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    alert_percentage = db.Column(db.Integer, default=80)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.CheckConstraint("period IN ('weekly', 'monthly', 'yearly')", name='check_budget_period'),
        db.CheckConstraint("amount > 0", name='check_budget_positive_amount'),
        db.CheckConstraint("alert_percentage >= 0 AND alert_percentage <= 100", name='check_alert_percentage')
    )
    
    def get_spent_amount(self):
        """Calcula quanto já foi gasto neste orçamento"""
        query = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.type == 'expense',
            Transaction.transaction_date >= self.start_date,
            Transaction.transaction_date <= self.end_date
        )
        
        if self.category_id:
            query = query.filter(Transaction.category_id == self.category_id)
            
        return float(query.with_entities(db.func.coalesce(db.func.sum(Transaction.amount), 0)).scalar())
    
    def get_percentage_used(self):
        """Calcula a porcentagem do orçamento utilizada"""
        spent = self.get_spent_amount()
        return (spent / float(self.amount)) * 100 if self.amount > 0 else 0
    
    def __repr__(self):
        return f'<Budget {self.name} - {self.amount}>'

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_amount = db.Column(db.Numeric(15, 2), nullable=False)
    current_amount = db.Column(db.Numeric(15, 2), default=0.00)
    target_date = db.Column(db.Date)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'paused', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    contributions = db.relationship('GoalContribution', backref='goal', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.CheckConstraint("status IN ('active', 'completed', 'paused', 'cancelled')", name='check_goal_status'),
        db.CheckConstraint("target_amount > 0", name='check_goal_positive_target'),
        db.CheckConstraint("current_amount >= 0", name='check_goal_positive_current')
    )
    
    def get_percentage_complete(self):
        """Calcula a porcentagem de conclusão da meta"""
        if self.target_amount <= 0:
            return 0
        return min((float(self.current_amount) / float(self.target_amount)) * 100, 100)
    
    def add_contribution(self, amount, transaction_id=None, notes=None):
        """Adiciona uma contribuição à meta"""
        contribution = GoalContribution(
            goal_id=self.id,
            transaction_id=transaction_id,
            amount=amount,
            contribution_date=datetime.utcnow().date(),
            notes=notes
        )
        db.session.add(contribution)
        
        # Atualiza o valor atual
        self.current_amount += Decimal(str(amount))
        
        # Marca como completa se atingiu a meta
        if self.current_amount >= self.target_amount and self.status == 'active':
            self.status = 'completed'
        
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Goal {self.name} - {self.current_amount}/{self.target_amount}>'

class GoalContribution(db.Model):
    __tablename__ = 'goal_contributions'
    
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    contribution_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.CheckConstraint("amount > 0", name='check_contribution_positive_amount'),
    )
    
    def __repr__(self):
        return f'<GoalContribution {self.amount} to Goal {self.goal_id}>'

# Callback obrigatório do Flask-Login (manter)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))