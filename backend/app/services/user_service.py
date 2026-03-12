"""
user_service.py — Servicio de gestión de usuarios por tenant.

Responsabilidades:
- CRUD completo de usuarios dentro de un tenant.
- Toda operación filtra obligatoriamente por tenant_id (regla multi-tenant).
- La lógica de validación vive aquí, nunca en los blueprints.

Regla: los blueprints solo llaman estas funciones y manejan la respuesta HTTP.
"""

from werkzeug.security import generate_password_hash

from app.core.extensions import db
from app.models.user import User
from app.models.role import Role


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------

def get_users(tenant_id: int) -> list[User]:
    """
    Devuelve todos los usuarios del tenant, ordenados por nombre.
    Nunca devuelve usuarios de otro tenant.
    """
    return (
        User.query
        .filter_by(tenant_id=tenant_id)
        .order_by(User.name.asc())
        .all()
    )


def get_user_by_id(tenant_id: int, user_id: int) -> User | None:
    """
    Devuelve un usuario por ID, validando que pertenezca al tenant.
    Devuelve None si no existe o si pertenece a otro tenant.
    """
    return User.query.filter_by(id=user_id, tenant_id=tenant_id).first()


def get_roles_for_tenant(tenant_id: int) -> list[Role]:
    """
    Devuelve los roles disponibles para el tenant.
    Usado para poblar el SelectField en formularios.
    """
    return (
        Role.query
        .filter_by(tenant_id=tenant_id)
        .order_by(Role.name.asc())
        .all()
    )


# ---------------------------------------------------------------------------
# Creación
# ---------------------------------------------------------------------------

def create_user(
    tenant_id: int,
    branch_id: int,
    name: str,
    email: str,
    password: str,
    role_id: int,
    is_active: bool = True,
) -> User:
    """
    Crea un nuevo usuario dentro del tenant.

    Args:
        tenant_id:  ID del tenant al que pertenece el usuario.
        branch_id:  ID de la sucursal asignada al usuario.
        name:       Nombre completo del usuario.
        email:      Email (único dentro del tenant).
        password:   Contraseña en texto plano (se hashea aquí).
        role_id:    ID del rol asignado (debe pertenecer al mismo tenant).
        is_active:  Estado inicial del usuario. Default: True.

    Returns:
        La instancia User creada.

    Raises:
        ValueError: si el email ya existe en el tenant o el rol no pertenece al tenant.
    """
    _validate_email_unique_in_tenant(tenant_id, email)
    _validate_role_belongs_to_tenant(tenant_id, role_id)
    _validate_password_length(password)

    user = User(
        tenant_id=tenant_id,
        branch_id=branch_id,
        name=name.strip(),
        email=email.strip().lower(),
        password_hash=generate_password_hash(password),
        role_id=role_id,
        is_active=is_active,
    )

    db.session.add(user)
    db.session.commit()

    return user


# ---------------------------------------------------------------------------
# Actualización
# ---------------------------------------------------------------------------

def update_user(
    tenant_id: int,
    user_id: int,
    name: str,
    email: str,
    role_id: int,
    is_active: bool,
    password: str | None = None,
) -> User:
    """
    Actualiza los datos de un usuario existente.

    - El password solo se actualiza si se pasa un valor no vacío.
    - Valida que el email no esté en uso por otro usuario del mismo tenant.
    - Valida que el rol pertenezca al tenant.

    Args:
        tenant_id:  ID del tenant (para aislamiento).
        user_id:    ID del usuario a actualizar.
        name:       Nuevo nombre.
        email:      Nuevo email.
        role_id:    Nuevo rol.
        is_active:  Nuevo estado.
        password:   Nueva contraseña (opcional). Si es None o vacío, no se cambia.

    Returns:
        La instancia User actualizada.

    Raises:
        ValueError: si el usuario no existe, email duplicado, o rol inválido.
    """
    user = get_user_by_id(tenant_id, user_id)
    if not user:
        raise ValueError(f"Usuario con id={user_id} no encontrado en este tenant.")

    # Validar email solo si cambió
    if email.strip().lower() != user.email:
        _validate_email_unique_in_tenant(tenant_id, email, exclude_user_id=user_id)

    _validate_role_belongs_to_tenant(tenant_id, role_id)

    user.name = name.strip()
    user.email = email.strip().lower()
    user.role_id = role_id
    user.is_active = is_active

    if password and password.strip():
        _validate_password_length(password)
        user.password_hash = generate_password_hash(password)

    db.session.commit()

    return user


# ---------------------------------------------------------------------------
# Eliminación / desactivación
# ---------------------------------------------------------------------------

def delete_user(tenant_id: int, user_id: int, requesting_user_id: int) -> None:
    """
    Elimina permanentemente un usuario del tenant.

    Restricciones:
    - Un usuario no puede eliminarse a sí mismo.
    - No se puede eliminar al único admin activo del tenant.

    Args:
        tenant_id:           ID del tenant.
        user_id:             ID del usuario a eliminar.
        requesting_user_id:  ID del usuario que hace la solicitud.

    Raises:
        ValueError: si el usuario no existe, intenta eliminarse a sí mismo,
                    o es el último admin activo.
    """
    if user_id == requesting_user_id:
        raise ValueError("No puedes eliminarte a ti mismo.")

    user = get_user_by_id(tenant_id, user_id)
    if not user:
        raise ValueError(f"Usuario con id={user_id} no encontrado en este tenant.")

    _validate_not_last_admin(tenant_id, user)

    db.session.delete(user)
    db.session.commit()


def deactivate_user(tenant_id: int, user_id: int, requesting_user_id: int) -> User:
    """
    Desactiva un usuario sin eliminarlo (soft disable).
    El usuario no podrá iniciar sesión, pero sus registros históricos se preservan.

    Raises:
        ValueError: si el usuario no existe, intenta desactivarse a sí mismo,
                    o es el último admin activo.
    """
    if user_id == requesting_user_id:
        raise ValueError("No puedes desactivarte a ti mismo.")

    user = get_user_by_id(tenant_id, user_id)
    if not user:
        raise ValueError(f"Usuario con id={user_id} no encontrado en este tenant.")

    _validate_not_last_admin(tenant_id, user)

    user.is_active = False
    db.session.commit()

    return user


# ---------------------------------------------------------------------------
# Validaciones internas
# ---------------------------------------------------------------------------

def _validate_email_unique_in_tenant(
    tenant_id: int,
    email: str,
    exclude_user_id: int | None = None,
) -> None:
    """
    Valida que el email no esté en uso dentro del tenant.
    Si se pasa exclude_user_id, ignora ese usuario (útil en edición).

    Raises:
        ValueError: si el email ya está registrado.
    """
    query = User.query.filter_by(
        tenant_id=tenant_id,
        email=email.strip().lower(),
    )
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)

    if query.first():
        raise ValueError(f"El email '{email}' ya está en uso en esta ferretería.")


def _validate_role_belongs_to_tenant(tenant_id: int, role_id: int) -> None:
    """
    Valida que el rol asignado pertenezca al mismo tenant.
    Previene asignación de roles de otras ferreterías.

    Raises:
        ValueError: si el rol no existe en el tenant.
    """
    role = Role.query.filter_by(id=role_id, tenant_id=tenant_id).first()
    if not role:
        raise ValueError(f"El rol seleccionado no es válido para esta ferretería.")


def _validate_password_length(password: str) -> None:
    """
    Valida que la contraseña tenga al menos 8 caracteres.

    Raises:
        ValueError: si la contraseña es muy corta.
    """
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")


def _validate_not_last_admin(tenant_id: int, user: User) -> None:
    """
    Previene eliminar o desactivar al único admin activo del tenant.
    Si solo queda un admin activo, no se puede tocar.

    Raises:
        ValueError: si el usuario es el último admin activo.
    """
    # Obtener el rol "admin" del tenant
    admin_role = Role.query.filter_by(tenant_id=tenant_id, name="admin").first()
    if not admin_role:
        return  # Sin rol admin definido, no hay restricción

    # Solo aplica si el usuario tiene rol admin
    if user.role_id != admin_role.id:
        return

    # Contar admins activos restantes (excluyendo al usuario en cuestión)
    active_admins_count = User.query.filter_by(
        tenant_id=tenant_id,
        role_id=admin_role.id,
        is_active=True,
    ).count()

    if active_admins_count <= 1:
        raise ValueError(
            "No puedes eliminar o desactivar al único administrador activo de la ferretería."
        )