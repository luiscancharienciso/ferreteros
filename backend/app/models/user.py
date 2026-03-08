from sqlalchemy import UniqueConstraint

from app.core.extensions import db
from app.models.mixins import TimestampMixin, TenantMixin


class User(TenantMixin, TimestampMixin, db.Model):
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

    def __repr__(self):
        return f"<User {self.email}>"