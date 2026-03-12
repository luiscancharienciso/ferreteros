from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    """
    Formulario de inicio de sesión.
    """

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="El email es obligatorio."),
            Email(message="Ingresa un email válido.")
        ]
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria.")
        ]
    )

    submit = SubmitField("Iniciar sesión")


class RegisterForm(FlaskForm):
    """
    Formulario de registro de nueva ferretería.
    Crea un tenant completo: ferretería + sucursal + admin en una transacción.
    """

    tenant_name = StringField(
        "Nombre de la ferretería",
        validators=[
            DataRequired(message="El nombre de la ferretería es obligatorio."),
            Length(min=2, max=255, message="El nombre debe tener entre 2 y 255 caracteres.")
        ]
    )

    admin_name = StringField(
        "Tu nombre completo",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=2, max=120, message="El nombre debe tener entre 2 y 120 caracteres.")
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="El email es obligatorio."),
            Email(message="Ingresa un email válido.")
        ]
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=8, message="La contraseña debe tener al menos 8 caracteres.")
        ]
    )

    confirm_password = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(message="Debes confirmar la contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden.")
        ]
    )

    submit = SubmitField("Registrar ferretería")