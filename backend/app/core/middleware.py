import time
from flask import request, g
from flask_login import current_user
from app.core.logging_config import configure_logging

logger = configure_logging()


def register_middlewares(app):
    """
    Registra middlewares globales de la aplicación.
    """

    @app.before_request
    def before_request():
        """
        Ejecutado antes de cada request.

        Responsabilidades:
        - Registrar tiempo de inicio para calcular duración.
        - Inyectar g.tenant con el tenant del usuario autenticado.
          Si el request no está autenticado, g.tenant queda en None.
        """
        g.start_time = time.time()
        g.tenant = None

        # Import aquí para evitar importación circular en el arranque de la app
        if current_user.is_authenticated:
            from app.services.tenant_service import get_tenant_by_id
            tenant = get_tenant_by_id(current_user.tenant_id)

            if tenant and tenant.is_active:
                g.tenant = tenant
            else:
                logger.warning(
                    f"Request de usuario {current_user.id} con tenant inactivo o inexistente "
                    f"(tenant_id={current_user.tenant_id})"
                )


    @app.after_request
    def after_request(response):
        """
        Ejecutado después de cada request.
        Loguea método, path, status y duración.
        """
        duration = (time.time() - g.start_time) * 1000

        tenant_info = f" | tenant={g.tenant.slug}" if g.tenant else ""

        logger.info(
            f"{request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"{duration:.2f}ms{tenant_info}"
        )

        return response