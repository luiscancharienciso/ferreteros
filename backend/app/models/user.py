from flask_login import UserMixin

from app.core.extensions import db
from app.models.mixins import TimestampMixin, TenantMixin


class User(UserMixin, TenantMixin, TimestampMixin, db.Model):
    """
    Representa un usuario del sistema.
    Ejemplo: administrador, cajero, supervisor.

    Política de email: único globalmente en la plataforma.
    Un mismo email no puede pertenecer a dos ferreterías distintas.
    Esto simplifica el login (no necesita selector de tenant) y se alinea
    con el modelo SaaS donde cada persona tiene una sola cuenta.
    En Fase 5, cuando se implementen subdominios, se podrá migrar
    a unicidad por tenant si el negocio lo requiere.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False,
        index=True
    )

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey("branches.id"),
        nullable=False
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id"),
        nullable=False
    )

    name = db.Column(
        db.String(255),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        nullable=False,
        unique=True,   # único globalmente en la plataforma
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    is_superadmin = db.Column(
        db.Boolean,
        default=False,
        server_default="false",
        nullable=False,
        index=True
    )

    # Relationships
    role   = db.relationship("Role",   foreign_keys=[role_id],   lazy="joined")
    branch = db.relationship("Branch", foreign_keys=[branch_id], lazy="joined",
                             back_populates="users")
    sales  = db.relationship("Sale",   back_populates="seller",  lazy="select")

    def __repr__(self):
        return f"<User {self.email}>"

    def has_permission(self, permission: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico.
        Si el rol no tiene JSON de permisos, usa el mapa por nombre de rol como fallback.
        """
        if not self.role:
            return False

        permissions = self.role.permissions

        # Fallback por nombre de rol si permissions es NULL en la DB
        if not permissions:
            from app.core.decorators import ROLE_PERMISSION_MAP
            permissions = ROLE_PERMISSION_MAP.get(self.role.name.lower(), [])

        return permission in permissions