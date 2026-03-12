"""
decorators.py — Decoradores de autorización del sistema FERRETEROS.

Uso:
    from app.core.decorators import require_permission

    @users_bp.route("/create")
    @login_required
    @require_permission("manage_users")
    def create():
        ...

Regla: @login_required siempre ANTES de @require_permission.
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

# Mapa de permisos por nombre de rol — fallback para roles sin JSON de permisos
ROLE_PERMISSION_MAP = {
    "admin": [
        "manage_users",
        "manage_inventory",
        "manage_sales",
        "view_reports",
        "manage_roles",
        "manage_branches",
    ],
    "supervisor": [
        "manage_inventory",
        "manage_sales",
        "view_reports",
    ],
    "cajero": [
        "manage_sales",
    ],
}


def require_permission(permission: str):
    """
    Decorador que verifica que el usuario autenticado tenga el permiso indicado.

    Estrategia de verificación (en orden):
    1. Si el rol tiene permisos en JSON (Role.permissions), los usa.
    2. Si no, usa el mapa ROLE_PERMISSION_MAP por nombre de rol como fallback.
       Esto cubre usuarios creados antes de que los roles tuvieran JSON de permisos.

    Si el usuario no tiene el permiso:
        - Muestra un flash de error.
        - Redirige al dashboard.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if not current_user.role:
                flash("No tenés un rol asignado. Contactá al administrador.", "danger")
                return redirect(url_for("dashboard.index"))

            # Intentar permisos desde JSON primero
            permissions = current_user.role.permissions

            # Fallback: usar mapa por nombre de rol si JSON está vacío o es None
            if not permissions:
                role_name = current_user.role.name.lower()
                permissions = ROLE_PERMISSION_MAP.get(role_name, [])

            if permission not in permissions:
                flash("No tenés permiso para acceder a esta sección.", "danger")
                return redirect(url_for("dashboard.index"))

            return f(*args, **kwargs)

        return decorated_function
    return decorator