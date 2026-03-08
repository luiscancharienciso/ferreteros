import time
from flask import request, g
from app.core.logging_config import configure_logging

logger = configure_logging()


def register_middlewares(app):
    """
    Registra middlewares globales de la aplicación.
    """

    @app.before_request
    def before_request():
        """
        Middleware ejecutado antes de cada request.
        """

        # Guardar tiempo de inicio
        g.start_time = time.time()

        # Placeholder para tenant (se usará cuando tengamos auth)
        g.tenant = None


    @app.after_request
    def after_request(response):
        """
        Middleware ejecutado después de cada request.
        """

        duration = (time.time() - g.start_time) * 1000

        logger.info(
            f"{request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"{duration:.2f}ms"
        )

        return response