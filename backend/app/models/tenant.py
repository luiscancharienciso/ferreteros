from app.core.extensions import db
from app.models.mixins import TimestampMixin

class Tenant(TimestampMixin, db.Model):
    """
    Representa una ferretería dentro de la plataforma.
    Cada tenant es una empresa independiente.
    """

    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(255),
        nullable=False
    )

    slug = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True 
    )

    plan = db.Column(
        db.String(50),
        default="free"
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    def __repr__(self):
        return f"<Tenant {self.name}>"