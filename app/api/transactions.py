from flask import request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from .. import db
from ..models import Transaction, Category
from . import api_bp

@api_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    """API para listar transações"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.transaction_date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'transactions': [{
            'id': t.id,
            'type': t.type,
            'amount': float(t.amount),
            'description': t.description,
            'category': t.category.name,
            'transaction_date': t.transaction_date.isoformat(),
            'created_at': t.created_at.isoformat()
        } for t in transactions.items],
        'total': transactions.total,
        'pages': transactions.pages,
        'current_page': transactions.page
    })

@api_bp.route('/transactions', methods=['POST'])
@login_required
def create_transaction():
    """API para criar transação"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    # Validações básicas
    required_fields = ['category_id', 'type', 'amount', 'description', 'transaction_date']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Campo obrigatório: {field}'}), 400
    
    try:
        # Verifica se a categoria pertence ao usuário
        category = Category.query.filter_by(id=data['category_id'], user_id=current_user.id).first()
        if not category:
            return jsonify({'error': 'Categoria não encontrada'}), 404
        
        # Verifica se o tipo da transação é válido
        if data['type'] not in ['income', 'expense']:
            return jsonify({'error': 'Tipo de transação inválido'}), 400
        
        # Cria a transação
        transaction = Transaction(
            user_id=current_user.id,
            category_id=data['category_id'],
            type=data['type'],
            amount=data['amount'],
            description=data['description'],
            transaction_date=datetime.strptime(data['transaction_date'], '%Y-%m-%d').date(),
            notes=data.get('notes'),
            payment_method=data.get('payment_method'),
            tags=data.get('tags'),
            location=data.get('location')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transação criada com sucesso',
            'transaction': {
                'id': transaction.id,
                'type': transaction.type,
                'amount': float(transaction.amount),
                'description': transaction.description,
                'category': transaction.category.name,
                'transaction_date': transaction.transaction_date.isoformat()
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Formato de data inválido: {str(e)}'}), 400
    except KeyError as e:
        return jsonify({'error': f'Campo obrigatório não encontrado: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@api_bp.route('/transactions/<int:transaction_id>', methods=['PUT'])
@login_required
def update_transaction(transaction_id):
    """API para atualizar transação"""
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if not transaction:
        return jsonify({'error': 'Transação não encontrada'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    try:
        # Atualiza campos se fornecidos
        if 'category_id' in data:
            category = Category.query.filter_by(id=data['category_id'], user_id=current_user.id).first()
            if not category:
                return jsonify({'error': 'Categoria não encontrada'}), 404
            transaction.category_id = data['category_id']
        
        if 'type' in data:
            if data['type'] not in ['income', 'expense']:
                return jsonify({'error': 'Tipo de transação inválido'}), 400
            transaction.type = data['type']
        
        if 'amount' in data:
            transaction.amount = data['amount']
        
        if 'description' in data:
            transaction.description = data['description']
        
        if 'transaction_date' in data:
            transaction.transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        
        if 'notes' in data:
            transaction.notes = data['notes']
        
        if 'payment_method' in data:
            transaction.payment_method = data['payment_method']
        
        if 'tags' in data:
            transaction.tags = data['tags']
        
        if 'location' in data:
            transaction.location = data['location']
        
        transaction.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Transação atualizada com sucesso',
            'transaction': {
                'id': transaction.id,
                'type': transaction.type,
                'amount': float(transaction.amount),
                'description': transaction.description,
                'category': transaction.category.name,
                'transaction_date': transaction.transaction_date.isoformat()
            }
        })
        
    except ValueError as e:
        return jsonify({'error': f'Formato de data inválido: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@api_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    """API para deletar transação"""
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    
    if not transaction:
        return jsonify({'error': 'Transação não encontrada'}), 404
    
    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'message': 'Transação deletada com sucesso'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar transação: {str(e)}'}), 500