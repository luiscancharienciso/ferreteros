from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional


class UserForm(FlaskForm):
    """
    Formulario para crear y editar usuarios.
    """

    name = StringField(
        "Nombre",
        validators=[DataRequired(), Length(min=2, max=120)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Contraseña",
        validators=[Optional(), Length(min=8)]
    )

    role_id = SelectField(
        "Rol",
        coerce=int,
        validators=[DataRequired()]
    )

    is_active = BooleanField("Usuario activo")