from app.core.extensions import db
from app.models.mixins import TimestampMixin

class Product(TimestampMixin, db.Model):
    """
    Catálogo global del producto.
    No pertenece a ningún tenant.
    """
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        index=True
    )
    name = db.Column(
        db.String(255),
        nullable=False
    )
    description = db.Column(
        db.Text,
        nullable=True
    )
    category = db.Column(
        db.String(100),
        nullable=True
    )
    brand = db.Column(
        db.String(100),
        nullable=True
    )
    image_url = db.Column(
        db.String(500),
        nullable=True
    )
    is_active = db.Column(
        db.Boolean,
        default=True
    )
    def __repr__(self):
        return f"<Product {self.name}>"