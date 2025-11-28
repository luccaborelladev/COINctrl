# recreate_db.py
from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Banco criado com sucesso!")
    
    # Verificar
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📊 Tabelas: {', '.join(tables)}")