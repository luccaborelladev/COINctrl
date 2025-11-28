from flask import Blueprint

financial_bp = Blueprint('financial', __name__, url_prefix='/financial')

from app.financial.routes import *