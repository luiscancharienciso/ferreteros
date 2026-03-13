from app.core.extensions import db
from app.models.mixins import TimestampMixin, TenantMixin


class Sale(TenantMixin, TimestampMixin, db.Model):
    """
    Representa una venta realizada en el sistema.
    Es la cabecera de la venta (no los productos).
    """

    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey("branches.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    total = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    discount = db.Column(
        db.Numeric(10, 2),
        default=0
    )

    payment_method = db.Column(
        db.String(50),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="completed"
    )

    # Relationships
    branch = db.relationship("Branch", foreign_keys=[branch_id], lazy="joined",
                             back_populates="sales")
    seller = db.relationship("User",   foreign_keys=[user_id],   lazy="joined")
    items  = db.relationship("SaleItem", back_populates="sale",  lazy="select",
                             cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sale {self.id}>"