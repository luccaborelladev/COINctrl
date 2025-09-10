from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from datetime import date

class TransactionForm(FlaskForm):
    type = SelectField('Tipo', choices=[('income', 'Receita'), ('expense', 'Despesa')], 
                      validators=[DataRequired()])
    category_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Valor', validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('Descrição', validators=[DataRequired(), Length(max=255)])
    transaction_date = DateField('Data', validators=[DataRequired()], default=date.today)
    notes = TextAreaField('Observações', validators=[Optional(), Length(max=500)])
    payment_method = StringField('Método de Pagamento', validators=[Optional(), Length(max=50)])
    tags = StringField('Tags', validators=[Optional(), Length(max=255)])
    location = StringField('Local', validators=[Optional(), Length(max=255)])

class CategoryForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    type = SelectField('Tipo', choices=[('income', 'Receita'), ('expense', 'Despesa')], 
                      validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[Optional(), Length(max=500)])
    color = StringField('Cor', validators=[Optional(), Length(max=7)])
    icon = StringField('Ícone', validators=[Optional(), Length(max=50)])

class BudgetForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    amount = DecimalField('Valor', validators=[DataRequired(), NumberRange(min=0.01)])
    period = SelectField('Período', choices=[('weekly', 'Semanal'), ('monthly', 'Mensal'), ('yearly', 'Anual')], 
                        validators=[DataRequired()])
    category_id = SelectField('Categoria', coerce=int, validators=[Optional()])
    start_date = DateField('Data Início', validators=[DataRequired()])
    end_date = DateField('Data Fim', validators=[DataRequired()])
    alert_percentage = DecimalField('Alerta (%)', validators=[Optional(), NumberRange(min=0, max=100)])

class GoalForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Descrição', validators=[Optional(), Length(max=500)])
    target_amount = DecimalField('Valor Meta', validators=[DataRequired(), NumberRange(min=0.01)])
    target_date = DateField('Data Meta', validators=[Optional()])
    category = StringField('Categoria', validators=[Optional(), Length(max=50)])