# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError

from db_models import ChatUser


class RegistrationForm(FlaskForm):
    """Registration form"""
    fullname = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=25,
               message="Username must be between 3 and 25 characters.")
    ])

    username = StringField('username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=12,
               message="username must be between 8 and 35 characters.")
    ])

    sex = StringField('Male or Female', validators=[
        DataRequired(message="Gender is required."),
        Length(min=4, max=6,
               message="Sex must be 'male', 'female', or 'other'."),
        Regexp('^(male|female|Male|Female|other|Other)$',
               message="Sex must be 'male' or 'female', or 'other'.")
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=5, max=15,
               message="Password must be at least 5 characters long.")
    ])

    confirm_password = PasswordField('Password', validators=[
        DataRequired(message="Re-Enter Password."),
        EqualTo('password', message="Password must be matched")
    ])

    submit_btn = SubmitField('Create')
    
    
    def validate_username(self, username):
        user_object = ChatUser.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already chosen. Choose another")
        else:
            pass
