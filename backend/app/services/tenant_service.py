"""
tenant_service.py — Servicio de gestión de tenants.

Responsabilidades:
- Crear un tenant completo (ferretería + sucursal principal + roles base + admin)
  en una sola transacción atómica.
- Consultar y gestionar tenants existentes.

Regla: toda la lógica de negocio vive aquí. Los blueprints solo llaman a estas funciones.
"""

import re
from werkzeug.security import generate_password_hash

from app.core.extensions import db
from app.models.tenant import Tenant
from app.models.branch import Branch
from app.models.role import Role
from app.models.user import User


# ---------------------------------------------------------------------------
# Permisos base por rol
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS = {
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """
    Convierte un nombre de ferretería en un slug URL-safe.
    Ejemplo: 'Ferretería El Clavo' → 'ferreteria-el-clavo'
    """
    text = text.lower().strip()
    # Reemplazar caracteres con tilde
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ñ": "n", "ü": "u",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    # Eliminar caracteres no permitidos y reemplazar espacios con guiones
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def _ensure_unique_slug(base_slug: str) -> str:
    """
    Si el slug ya existe, agrega un sufijo numérico incremental.
    Ejemplo: 'ferreteria-norte' → 'ferreteria-norte-2'
    """
    slug = base_slug
    counter = 2
    while Tenant.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


# ---------------------------------------------------------------------------
# Función principal: bootstrap de tenant completo
# ---------------------------------------------------------------------------

def create_tenant(
    tenant_name: str,
    branch_name: str,
    admin_name: str,
    admin_email: str,
    admin_password: str,
    branch_address: str | None = None,
    plan: str = "free",
) -> dict:
    """
    Crea un tenant completo en una sola transacción atómica:
      1. Tenant (la ferretería)
      2. Branch principal (sucursal principal)
      3. Roles base: admin, supervisor, cajero (con sus permisos)
      4. Usuario administrador asignado al rol admin

    Args:
        tenant_name:     Nombre de la ferretería. Ej: "Ferretería Norte"
        branch_name:     Nombre de la sucursal principal. Ej: "Casa Central"
        admin_name:      Nombre completo del administrador.
        admin_email:     Email del administrador (único por tenant).
        admin_password:  Contraseña en texto plano (se hashea aquí).
        branch_address:  Dirección física de la sucursal (opcional).
        plan:            Plan de suscripción. Default: "free".

    Returns:
        dict con las instancias creadas: tenant, branch, roles, admin_user.

    Raises:
        ValueError: si el email del admin ya existe en la plataforma.
        Exception:  cualquier error de base de datos hace rollback completo.
    """

    # Validar email único a nivel plataforma
    if User.query.filter_by(email=admin_email).first():
        raise ValueError(f"El email '{admin_email}' ya está registrado en la plataforma.")

    if len(admin_password) < 8:
        raise ValueError("La contraseña del administrador debe tener al menos 8 caracteres.")

    try:
        # 1. Crear tenant
        slug = _ensure_unique_slug(_slugify(tenant_name))
        tenant = Tenant(
            name=tenant_name,
            slug=slug,
            plan=plan,
            is_active=True,
        )
        db.session.add(tenant)
        db.session.flush()  # obtener tenant.id sin hacer commit

        # 2. Crear sucursal principal
        branch = Branch(
            tenant_id=tenant.id,
            name=branch_name,
            address=branch_address,
            is_main=True,
        )
        db.session.add(branch)
        db.session.flush()  # obtener branch.id

        # 3. Crear roles base con sus permisos
        created_roles = {}
        for role_name, permissions in ROLE_PERMISSIONS.items():
            role = Role(
                tenant_id=tenant.id,
                name=role_name,
                permissions=permissions,
            )
            db.session.add(role)
            created_roles[role_name] = role

        db.session.flush()  # obtener role.id para el admin

        # 4. Crear usuario administrador
        admin_user = User(
            tenant_id=tenant.id,
            branch_id=branch.id,
            role_id=created_roles["admin"].id,
            name=admin_name,
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            is_active=True,
        )
        db.session.add(admin_user)

        db.session.commit()

        return {
            "tenant": tenant,
            "branch": branch,
            "roles": created_roles,
            "admin_user": admin_user,
        }

    except Exception:
        db.session.rollback()
        raise


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------

def get_tenant_by_id(tenant_id: int) -> Tenant | None:
    """Devuelve un tenant por su ID, o None si no existe."""
    return db.session.get(Tenant, tenant_id)


def get_tenant_by_slug(slug: str) -> Tenant | None:
    """Devuelve un tenant por su slug único."""
    return Tenant.query.filter_by(slug=slug).first()


def get_all_tenants() -> list[Tenant]:
    """Lista todos los tenants de la plataforma. Uso exclusivo de superadmins."""
    return Tenant.query.order_by(Tenant.created_at.desc()).all()


def deactivate_tenant(tenant_id: int) -> Tenant:
    """
    Desactiva un tenant. Sus usuarios no podrán iniciar sesión.

    Raises:
        ValueError: si el tenant no existe.
    """
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        raise ValueError(f"Tenant con id={tenant_id} no encontrado.")

    tenant.is_active = False
    db.session.commit()
    return tenant