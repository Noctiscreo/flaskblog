# render_template enalbes Flask to render html files.
# url_for enables linking to files, e.g. for CSS files:
# <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='main.css') }}">
from flask import Flask, render_template, url_for
from forms import RegistrationForm, LoginForm
# Instantiates a Flask application into 'app'.
app = Flask(__name__)

# Sets up a 'secret key' for WTForms
app.config['SECRET_KEY'] = 'b8453cb5dd480b2a768f4ae0acc3eaa0'

posts = [
    {
        'author': 'Corey Shafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'John Hasznosi',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'Jan 4, 2024'
    }
]

# '@app' allows us to write a function for the route.
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)

@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)

if __name__ =='__main__':
    app.run(debug=True)
