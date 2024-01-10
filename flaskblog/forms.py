# flast_wtf and wtforms etc. were installed with the same:
# pip install flask-wtf
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User


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

    # validate_[field name], and pass in [field name] as an argument.
    def validate_username(self, username):

        # If there's a user, it will add to variable.
        # If there isn't, it will return 'None'.
        user = User.query.filter_by(username=username.data).first()

        # If the user already exists in the db:
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    
    # validate_[field name], and pass in [field name] as an argument.
    def validate_email(self, email):

        # If there's an email, it will add to variable.
        # If there isn't, it will return 'None'.
        user = User.query.filter_by(email=email.data).first()

        # If the email already exists in the db:
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')



# Creates a login form, inherited from FlaskForm.
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    password = PasswordField('Password',
                             validators=[DataRequired()])
    
    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Login')
