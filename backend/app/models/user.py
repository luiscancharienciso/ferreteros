from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

from app.core.extensions import db
from app.models.mixins import TimestampMixin, TenantMixin


class User(UserMixin, TenantMixin, TimestampMixin, db.Model):
    """
    Representa un usuario del sistema.
    Ejemplo: administrador, cajero, supervisor.
    """

    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint('tenant_id', 'email', name='uq_user_tenant_email'),
    )

    id = db.Column(db.Integer, primary_key=True)

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

    # Relación al rol — permite acceder a current_user.role.permissions
    role = db.relationship("Role", foreign_keys=[role_id], lazy="joined")

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