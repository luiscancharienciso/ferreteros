from app.core.extensions import db
from app.models.mixins import TimestampMixin, TenantMixin

class Role(TenantMixin, TimestampMixin, db.Model):
    """
    Representa un rol dentro de la ferretería.
    Define los permisos de los usuarios.
    """

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    permissions = db.Column(
        db.JSON,
        nullable=True
    )

    def __repr__(self):
        return f"<Role {self.name}>"