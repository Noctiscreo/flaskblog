from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Instantiates a Flask application into 'app'.
app = Flask(__name__)

# Sets up a 'secret key' for WTForms
app.config['SECRET_KEY'] = 'b8453cb5dd480b2a768f4ae0acc3eaa0'

# /// = relative path from the current file.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

from flaskblog import routes

