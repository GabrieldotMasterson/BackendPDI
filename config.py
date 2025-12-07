import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mysecretkey")
    APP_TITLE = "Doar o Saber API"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "mysecretkey")
    JWT_TOKEN_LOCATION = ["headers"]

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")


class ProductionConfig(Config):

    pass
    # raw_uri = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL") or ""

    # if raw_uri.startswith("postgres://"):
    #     raw_uri = raw_uri.replace("postgres://", "postgresql+psycopg://", 1)
    # elif raw_uri.startswith("postgresql://"):
    #     raw_uri = raw_uri.replace("postgresql://", "postgresql+psycopg://", 1)

    # SQLALCHEMY_DATABASE_URI = raw_uri
