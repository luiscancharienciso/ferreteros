from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Redirección automática si no está autenticado
login_manager.login_view = "auth.login"
login_manager.login_message = None
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    """
    Carga el usuario desde la base de datos usando su ID.
    Flask-Login usa esta función para reconstruir la sesión.
    """
    from app.models.user import User
    return db.session.get(User, int(user_id))