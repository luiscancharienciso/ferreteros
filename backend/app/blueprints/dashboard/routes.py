from flask import render_template
from flask_login import login_required

from app.blueprints.dashboard import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():
    """
    Página principal del dashboard.
    Solo accesible para usuarios autenticados.
    """
    return render_template("dashboard/index.html")