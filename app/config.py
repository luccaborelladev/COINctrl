import os
import json
from datetime import timedelta

class Config:
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///coinctrl.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configurações de segurança
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 30  # minutos
    
    # OAuth Google
    @staticmethod
    def load_google_credentials():
        """Carregar credenciais do Google OAuth"""
        try:
            with open('google_credentials.json', 'r') as f:
                google_config = json.load(f)
                return (
                    google_config['web']['client_id'],
                    google_config['web']['client_secret']
                )
        except FileNotFoundError:
            print("⚠️ Arquivo google_credentials.json não encontrado.")
            return None, None
        except Exception as e:
            print(f"❌ Erro ao carregar credenciais Google: {e}")
            return None, None
    
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET = load_google_credentials()