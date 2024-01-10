# render_template enables Flask to render html files.
# url_for enables linking to files, e.g. for CSS files:
# <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='main.css') }}">
from flask import render_template, url_for, flash, redirect
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user

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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Create an instance of the form class:
    form = RegistrationForm()
    # Check if form is valid on submit:
    if form.validate_on_submit():
        # If valid, create hashed password, 
        # taking the form.password.data from the user input.
        # And decode it into a string using decode('utf-8'):
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Then create a new user from the form:
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # Add the 'user' above to the database:
        db.session.add(user)
        # Commit the changes:
        db.session.commit()
        # Then add the 'success' parameter adds a bootstrap class
        # and adds a one time message to the user.
        flash('Your account has been created! You are now able to log in.', 'success')
        # Redirect user to a different page from the form.
        # 'home' is the name of the FUNCTION, not the route.
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        # If the user existsL
        user = User.query.filter_by(email=form.email.data).first()
        # and if the password they entered is valid:
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # First parameter is 'login this user,'
            # Second parameter checks 'remember me?' option.
            # Remember me is a true/false value (depending on if they checked it).
            login_user(user, remember=form.remember.data)
            # After they've logged in, redirect them to the homepage:
            return redirect(url_for('home'))
        else:
            # 'danger' is the bootstrap style for an error.
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)