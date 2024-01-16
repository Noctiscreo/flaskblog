import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

# Instantiates a Flask application into 'app'.
app = Flask(__name__)

# Sets up a 'secret key' for WTForms
app.config['SECRET_KEY'] = 'b8453cb5dd480b2a768f4ae0acc3eaa0'

# /// = relative path from the current file.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
# 'login' is the route that gets used if the user is not logged in.
login_manager.login_view = 'login'
# 'info' is a bootstrap class.
login_manager.login_message_category = 'info'

# Email account setup for sending password resets.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config["MAIL_USE_TLS"] = False
app.config['MAIL_USE_SSL'] = True

# Set up environment variables to hide username and password. Then:
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

# Initialize extension
mail = Mail(app)

from flaskblog import routes

