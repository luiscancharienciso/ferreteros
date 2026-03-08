from app.core.extensions import db
from app.models.mixins import TimestampMixin


class SaleItem(TimestampMixin, db.Model):
    """
    Representa un producto dentro de una venta.
    """

    __tablename__ = "sale_items"

    id = db.Column(db.Integer, primary_key=True)

    sale_id = db.Column(
        db.Integer,
        db.ForeignKey("sales.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    unit_price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    discount = db.Column(
        db.Numeric(10, 2),
        default=0
    )

    def __repr__(self):
        return f"<SaleItem sale={self.sale_id} product={self.product_id}>"