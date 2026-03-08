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
    
    # 👇 Log de entorno activo
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
)
    app.config.from_object(config_class)

    from flask import render_template                       #temporal


    logger.info(f"Inicializando extensiones")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return None


    register_middlewares(app)

     # RUTA TEMPORAL PARA VISUALIZAR UI
    from flask import render_template

    @app.route("/")
    def home():
        return render_template("dashboard/index.html")



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