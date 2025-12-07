# app.py
from flask import Flask
from factory import register_extensions
from config import Config
from routes import register_routes  # Importar do routes.py

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Registrar extensões
    register_extensions(app)
    
    # Registrar rotas
    register_routes(app)
    
    return app

# Criar a aplicação
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)