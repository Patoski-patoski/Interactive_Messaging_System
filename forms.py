#forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo

class RegistrationForm(FlaskForm):
    """Registration form"""
    fullname = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=25, message="Username must be between 3 and 25 characters.")
    ])
    
    username = StringField('username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=12, message="username must be between 8 and 35 characters.")
    ])
    
    gender = StringField('Gender', validators=[
        DataRequired(message="Gender is required."),
        Length(min=4, max=6, message="Gender must be either 'male' or 'female'."),
        Regexp('^(male|female|Male|Female)$', message="Gender must be 'male' or 'female'.")
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=5, max=15, message="Password must be at least 5 characters long.")
    ])
    
    confirm_password = PasswordField('Password', validators=[
        DataRequired(message="Re-Enter Password."),
        EqualTo('password', message="Password must be matched")
    ])

    submit_btn = SubmitField('Create')