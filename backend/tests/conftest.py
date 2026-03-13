import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Forzar entorno testing ANTES de importar la app
os.environ["FLASK_ENV"]    = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app
from app.core.extensions import db


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        # SECRET_KEY requerida por Flask-Login y WTForms (firma de cookies y tokens CSRF)
        # aunque WTF_CSRF_ENABLED=False, la ausencia provoca errores en sesiones firmadas
        SECRET_KEY="test-secret-key-not-for-production",
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()