
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import os
from spectree import SpecTree, SecurityScheme

# Inicializar extensões globalmente
db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()

api = SpecTree(
    "flask",
    title="PDI API",
    version="v.1.0",
    path="docs",
    security_schemes=[
        SecurityScheme(
            name="api_key",
            data={"type": "apiKey", "name": "Authorization", "in": "header"},
        )
    ],
    security={"api_key": []},
)

def create_app():
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-me'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///pdi.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    
    # Inicializar extensões
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    # Importar controllers DENTRO da função para evitar imports circulares
    from controllers.auth import auth_controller
    from controllers.user import user_controller
    from controllers.PDIController import pdi_bp
    
    # Registrar blueprints
    app.register_blueprint(auth_controller, url_prefix='/api/auth')
    app.register_blueprint(user_controller, url_prefix='/api/users')
    app.register_blueprint(pdi_bp, url_prefix='/api/pdi')
    
    # Rota de teste
    @app.route('/')
    def index():
        return {'message': 'PDI API is running', 'status': 'ok'}
    
    api.register(app) 
    return app

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)