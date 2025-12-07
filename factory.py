# factory.py
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate  


db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()  

def register_extensions(app):
    """Registra todas as extensões na aplicação Flask"""
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)  # Adicionar esta linha
    
    return app

# Exporta db globalmente para uso nos modelos
__all__ = ['db', 'ma', 'jwt', 'cors', 'migrate', 'register_extensions']