# run.py
import os
from app import create_app, db
from dotenv import load_dotenv
load_dotenv()
# PERMITIR HTTP EM DESENVOLVIMENTO (apenas para desenvolvimento local)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados criado!")
    
    print("�� Servidor iniciando em http://127.0.0.1:5000")
    print("⚠️  ATENÇÃO: OAUTHLIB_INSECURE_TRANSPORT ativado para desenvolvimento")
    app.run(debug=True)