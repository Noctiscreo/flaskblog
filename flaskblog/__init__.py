# render_template enables Flask to render html files.
# url_for enables linking to files, e.g. for CSS files:
# <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='main.css') }}">
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Instantiates a Flask application into 'app'.
app = Flask(__name__)

# Sets up a 'secret key' for WTForms
app.config['SECRET_KEY'] = 'b8453cb5dd480b2a768f4ae0acc3eaa0'
# /// = relative path from the current file.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

from flaskblog import routes