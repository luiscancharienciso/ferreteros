from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from app.models.user import User
from app.services import tenant_service
from . import auth_bp
from .forms import LoginForm, RegisterForm


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Maneja el inicio de sesión de usuarios.
    Redirige al dashboard si ya está autenticado.
    """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash("Tu cuenta está desactivada. Contactá al administrador.", "danger")
                return redirect(url_for("auth.login"))

            login_user(user)
            flash(f"Bienvenido, {user.name}.", "success")
            return redirect(url_for("dashboard.index"))

        flash("Credenciales incorrectas.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Cierra la sesión del usuario actual."""
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Registro de nueva ferretería (tenant).
    Crea en una sola transacción:
        - Tenant (la ferretería)
        - Branch principal (sucursal)
        - Roles base: admin, supervisor, cajero
        - Usuario administrador
    Tras el registro, inicia sesión automáticamente.
    """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        try:
            result = tenant_service.create_tenant(
                tenant_name=form.tenant_name.data,
                branch_name="Casa Central",
                admin_name=form.admin_name.data,
                admin_email=form.email.data,
                admin_password=form.password.data,
            )

            # Iniciar sesión automáticamente con el admin recién creado
            login_user(result["admin_user"])
            flash(f"¡Ferretería registrada correctamente! Bienvenido, {result['admin_user'].name}.", "success")
            return redirect(url_for("dashboard.index"))

        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("Ocurrió un error al registrar la ferretería. Intentá de nuevo.", "danger")

    return render_template("auth/register.html", form=form)