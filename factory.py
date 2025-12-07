import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from spectree import SecurityScheme, SpecTree
from sqlalchemy import select
from flask_cors import CORS

from config import DevelopmentConfig, ProductionConfig
    

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

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
    CORS(app)

    #ambiente de produção ou desenvolvimento
    is_vercel = os.getenv("VERCEL") == "1"
    flask_env = os.getenv("FLASK_ENV")

    if is_vercel or flask_env == "production":
        print(">>> PRODUCTION mode")
        # app.config.from_object(ProductionConfig)
    else:
        print(">>> DEVELOPMENT mode")
        app.config.from_object(DevelopmentConfig)


    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from models import User, Talks, Role, Registrations

    @jwt.user_lookup_loader
    def user_load(header, data):
        return db.session.scalars(
            select(User).filter_by(username=data["sub"])
        ).first()

    from controllers import (
        user_controller,
        auth_controller,
        talk_controller,
        registration_controller,
    )

    app.register_blueprint(user_controller)
    app.register_blueprint(auth_controller)
    app.register_blueprint(talk_controller)
    app.register_blueprint(registration_controller)

    api.register(app)

    return app
