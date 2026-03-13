import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # Fallback a SQLite local si no hay DATABASE_URL en .env
    # Permite levantar el proyecto sin configurar PostgreSQL en desarrollo
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///ferreteros_dev.db")


class ProductionConfig(BaseConfig):
    DEBUG = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"sslmode": "require"}
    }


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"