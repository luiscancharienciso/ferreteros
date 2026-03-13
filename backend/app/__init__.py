from dotenv import load_dotenv
import os
# Cargar variables de entorno desde .env
load_dotenv()

from flask import Flask
from app.core.config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.core.extensions import db, migrate, login_manager
from app.core.logging_config import configure_logging
from app.core.middleware import register_middlewares


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

def create_app():
    env = os.getenv("FLASK_ENV", "development").lower()
    config_class = CONFIG_MAP.get(env, DevelopmentConfig)

    # Log de entorno activo
    print(f"⚙️  Flask environment: {env}")

    logger = configure_logging()
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        logger.info(f"Starting FERRETEROS backend")
        logger.info(f"Enviroment: {env}")

    if env == "production":
        _validate_production_env()

    app = Flask(
        __name__,
        template_folder="../../frontend/src/templates",
        # static_folder apunta a frontend/src mientras no haya build de Tailwind.
        # En Fase 2 (cuando se active el build con PostCSS), cambiar a:
        #   static_folder="../../frontend/dist"
        static_folder="../../frontend/src",
        static_url_path="/static",
    )
    app.config.from_object(config_class)

    logger.info(f"Inicializando extensiones")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    # load_user está definido en extensions.py — no se duplica aquí

    register_middlewares(app)

    # Registrar blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)

    from app import models

    logger.info(f"Aplicación iniciada correctamente")

    return app

def _validate_production_env():
    required = ["SECRET_KEY", "DATABASE_URL"]
    missing = [var for var in required if not os.getenv(var, "").strip()]
    if missing:
        raise EnvironmentError(f"Variables faltantes en producción: {', '.join(missing)}")

    # Validar que SECRET_KEY no sea la de desarrollo
    secret = os.getenv("SECRET_KEY")

    insecure_keys = [
        "dev-secret-key",
        "default-secret",
        "change-me",
        "secret",
    ]

    if secret in insecure_keys or len(secret) < 32:
        raise RuntimeError(
            "SECRET_KEY insegura. Debe ser una clave fuerte en producción."
        )