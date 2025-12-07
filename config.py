# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    # SQLite - caminho relativo
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///pdi.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    
    # Opcional: Habilitar WAL para SQLite (melhor performance)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'check_same_thread': False,
            'timeout': 30
        }
    }