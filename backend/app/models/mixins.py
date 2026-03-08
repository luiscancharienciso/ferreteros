from datetime import datetime
from app.core.extensions import db


class TimestampMixin:
    """
    Agrega timestaps automáticos a los modelos
    """

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

class TenantMixin:
    """
    Agrega aislamiento multi-tenat.
    Cada registro pertenece a una ferretería (tenant)
    """

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False,
        index=True
    )