# flast_wtf and wtforms etc. were installed with the same:
# pip install flask-wtf
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

# Creates a registration form, and inherits this from FlaskForm.
class RegistrationForm(FlaskForm):
    # Form fields are all imported classes from the WTForms package.

    # StringField = string input by user. 'Username' = label.
    username = StringField('Username', 
                           # DataRequired = 'can't be empty'.
                           # Lengh = min and max length of entry.
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    password = PasswordField('Password',
                             validators=[DataRequired()])
    
    confirm_password = PasswordField('Confirm Password',
                             validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Sign Up')


# Creates a login form, inherited from FlaskForm.
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    password = PasswordField('Password',
                             validators=[DataRequired()])
    
    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Login')

