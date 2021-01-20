from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash


class RegistrationForm(FlaskForm):
    username = StringField('username',
                           validators=[InputRequired(), Length(min=3, max=20)])
    email = StringField('email',
                        validators=[InputRequired(), Length(max=50)])
    password = PasswordField('password',
                             validators=[InputRequired(), Length(min=8)])


class LoginForm(FlaskForm):
    username = StringField('username',
                           validators=[InputRequired()])
    password = PasswordField('password',
                             validators=[InputRequired(), Length(min=8)])
    remember = BooleanField('remember me')