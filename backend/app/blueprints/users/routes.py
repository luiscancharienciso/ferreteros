"""
Blueprint: users
Rutas: /users

Responsabilidad: routing + respuesta HTTP únicamente.
Toda la lógica de negocio vive en user_service.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from app.services import user_service
from app.core.decorators import require_permission
from .forms import UserForm
from . import users_bp


def _load_role_choices(form):
    """Puebla el SelectField de roles con los del tenant actual."""
    roles = user_service.get_roles_for_tenant(current_user.tenant_id)
    form.role_id.choices = [(role.id, role.name) for role in roles]


# ---------------------------------------------------------------------------
# GET /users — listado
# ---------------------------------------------------------------------------

@users_bp.route("/")
@login_required
def index():
    """Lista todos los usuarios del tenant actual."""
    users = user_service.get_users(current_user.tenant_id)
    csrf_form = FlaskForm()
    return render_template("users/index.html", users=users, csrf_form=csrf_form)


# ---------------------------------------------------------------------------
# GET /users/create — formulario de creación
# POST /users/create — procesar creación
# ---------------------------------------------------------------------------

@users_bp.route("/create", methods=["GET", "POST"])
@login_required
@require_permission("manage_users")
def create():
    """Crea un nuevo usuario en el tenant actual."""
    form = UserForm()
    _load_role_choices(form)

    if form.validate_on_submit():
        try:
            user_service.create_user(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                name=form.name.data,
                email=form.email.data,
                password=form.password.data,
                role_id=form.role_id.data,
                is_active=form.is_active.data,
            )
            flash("Usuario creado correctamente.", "success")
            return redirect(url_for("users.index"))

        except ValueError as e:
            flash(str(e), "danger")

    return render_template("users/create.html", form=form)


# ---------------------------------------------------------------------------
# GET /users/<id>/edit — formulario de edición
# POST /users/<id>/edit — procesar edición
# ---------------------------------------------------------------------------

@users_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("manage_users")
def edit(user_id):
    """Edita un usuario existente del tenant actual."""
    user = user_service.get_user_by_id(current_user.tenant_id, user_id)
    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("users.index"))

    # GET: pre-poblar con datos del usuario. POST: WTForms lee request.form automáticamente.
    form = UserForm(obj=user) if request.method == "GET" else UserForm()

    _load_role_choices(form)

    if form.validate_on_submit():
        try:
            user_service.update_user(
                tenant_id=current_user.tenant_id,
                user_id=user_id,
                name=form.name.data,
                email=form.email.data,
                role_id=form.role_id.data,
                is_active=form.is_active.data,
                password=form.password.data or None,
            )
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("users.index"))

        except ValueError as e:
            flash(str(e), "danger")

    return render_template("users/edit.html", form=form, user=user)


# ---------------------------------------------------------------------------
# POST /users/<id>/delete — eliminar usuario
# (Se usa POST porque HTML no soporta DELETE nativo en forms)
# ---------------------------------------------------------------------------

@users_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@require_permission("manage_users")
def delete(user_id):
    """Elimina un usuario del tenant actual."""
    try:
        user_service.delete_user(
            tenant_id=current_user.tenant_id,
            user_id=user_id,
            requesting_user_id=current_user.id,
        )
        flash("Usuario eliminado correctamente.", "success")

    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("users.index"))