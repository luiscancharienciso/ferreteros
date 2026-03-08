from app.core.extensions import db
from app.models.mixins import TimestampMixin, TenantMixin


class AILog(TenantMixin, TimestampMixin, db.Model):
    """
    Registro de análisis realizados por el módulo de IA.
    """

    __tablename__ = "ai_logs"

    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(
        db.String(100),
        nullable=False
    )

    input_data = db.Column(
        db.JSON,
        nullable=True
    )

    output_data = db.Column(
        db.JSON,
        nullable=True
    )

    def __repr__(self):
        return f"<AILog {self.type}>"