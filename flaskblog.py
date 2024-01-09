from datetime import datetime

# render_template enalbes Flask to render html files.
# url_for enables linking to files, e.g. for CSS files:
# <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='main.css') }}">
from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
# Import the forms you've made in forms.py:
from forms import RegistrationForm, LoginForm

# Instantiates a Flask application into 'app'.
app = Flask(__name__)

# Sets up a 'secret key' for WTForms
app.config['SECRET_KEY'] = 'b8453cb5dd480b2a768f4ae0acc3eaa0'
# /// = relative path from the current file.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

# Each class is a table in the database:
# Imports from db.Model.
class User(db.Model):
    # Columns for each table (primary key = unique ID for the user):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    # The password will be a hashed string, 60 characters long.
    password = db.Column(db.String(60), nullable=False)
    
    # Establish relationship to other tables.
    # Does not create a column in the database, it only makes a query.
    # The User table is related to the Post table.
    # 'Post' references the Post class.
    # 'author' gets the user who created the post.
    # lazy means SQLAlchemy will load the data as necessary in one go,
    # i.e. all of the posts created by a user.
    posts = db.relationship('Post', backref='author', lazy=True)

    # Specifies an __repr__ method (magic method / dunderscore method).
    def __repr__ (self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # Be sure to import datetime from datetime.
    # utcnow is needed to keep dates and times consistent.
    # No parentheses for utcnow because you don't want the current time now.
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    # Grabs the primary key of the user.
    # 'user.id' references the user table name, and id column.
    # User class automatically sets its table name to 'user'.
    # Table names can be changed if needed.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__ (self):
        return f"Post('{self.title}', '{self.date_posted}')"
    


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

@app.route("/register", methods=['GET', 'POST'])
def register():
    # Create an instance of the form class:
    form = RegistrationForm()
    if form.validate_on_submit():
        # 'flash' sends a one time alert. 
        # The 'success' parameter adds a bootstrap class.
        flash(f'Account created for {form.username.data}!', 'success')
        # Redirect user to a different page from the form.
        # 'home' is the name of the FUNCTION, not the route.
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Dummy data to test the form entry is successful:
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            # 'danger' is the bootstrap style for an error.
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

if __name__ =='__main__':
    app.run(debug=True)
