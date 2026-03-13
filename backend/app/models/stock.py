from app.core.extensions import db
from app.models.mixins import TimestampMixin, TenantMixin


class Stock(TenantMixin, TimestampMixin, db.Model):
    """
    Inventario de productos por sucursal.
    Aquí viven el precio y la cantidad disponible.
    """

    __tablename__ = "stocks"

    id = db.Column(db.Integer, primary_key=True)

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey("branches.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    min_stock = db.Column(
        db.Integer,
        default=0
    )

    max_stock = db.Column(
        db.Integer,
        nullable=True
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    cost = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )

    # Relationships
    product = db.relationship("Product", foreign_keys=[product_id], lazy="joined")
    branch  = db.relationship("Branch",  foreign_keys=[branch_id],  lazy="joined",
                              back_populates="stocks")

    def __repr__(self):
        return f"<Stock product={self.product_id} qty={self.quantity}>"