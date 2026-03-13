from app.core.extensions import db
from app.models.mixins import TimestampMixin

class Branch(TimestampMixin, db.Model):
    """
    Representa una sucursal de una ferretería (tenant).
    """

    __tablename__ = "branches"

    id = db.Column(db.Integer, primary_key=True)

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id"),
        nullable=False,
        index=True
    )

    name = db.Column(
        db.String(255),
        nullable=False
    )

    address = db.Column(
        db.String(255),
        nullable=True
    )

    is_main = db.Column(
        db.Boolean,
        default=False
    )

    # Relationships
    tenant = db.relationship("Tenant", foreign_keys=[tenant_id], lazy="joined")
    users  = db.relationship("User",  back_populates="branch", lazy="select")
    stocks = db.relationship("Stock", back_populates="branch", lazy="select")
    sales  = db.relationship("Sale",  back_populates="branch", lazy="select")

    def __repr__(self):
        return f"<Branch {self.name}>"