from app import create_app
from app import db

app = create_app()
with app.app_context():
    db.session.execute(db.text('DELETE FROM alembic_version'))
    db.session.commit()
    print("alembic_version limpiada")