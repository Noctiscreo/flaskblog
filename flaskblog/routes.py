# Grabs file extensions:
import os

# Creates a random hex:
import secrets

# Pillow for managing image size.
from PIL import Image

# render_template enables Flask to render html files.
# url_for enables linking to files, e.g. for CSS files:
# <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='main.css') }}">
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


# '@app' allows us to write a function for the route.
@app.route("/")
@app.route("/home")
def home():
    # Grab all of the posts from the database:
    posts = Post.query.all()
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
            # 'args' is a dictionary, so we use .get
            # in case the 'next' key doesn't exist 
            # (it won't crash, it will return 'None')
            next_page = request.args.get('next')
            # After they've logged in, redirect them to the homepage
            # if 'next_page' is None.
            # Below is a 'turnary' operator.
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            # 'danger' is the bootstrap style for an error.
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    # Imported from 'logout_user'
    logout_user()
    # Send the user back to the homepage.
    return redirect(url_for('home'))

def save_picture(form_picture):
    # Randomize the name of the picture with 8 bytes:
    random_hex = secrets.token_hex(8)
    # Grab file name and extension using the 'os' module:
    # form_picture.filename = data from the field that the user submits.
    # '_' is used in python for variables that we don't use.
    # f_ext = file extension
    _, f_ext = os.path.splitext(form_picture.filename)
    # Combing the random hex with the file name we want to save:
    picture_fn = random_hex + f_ext

    # To save our pics into our static folder:
    # app.root_path = gives the root path of our application up to our package directory.
    #  picture_path now contains the full path and file name of the image 
    # (i.e., the hex, the extension, and where we want to save it)
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # Set the pixel size you want for the website:
    output_size = (125, 125)
    # Open the image passed into the function above:
    i = Image.open(form_picture)
    # Resize the image:
    i.thumbnail(output_size)

    # Save the image above ('i') using the path we created:
    i.save(picture_path)

    # Removes the previous picture:
    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
    if os.path.exists(prev_picture):
        os.remove(prev_picture)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
# With @login_required, the extension knows 
# that we need to log in to access this route
@login_required
def account():
   # Create instance of 'UpdateAccount' form:
   form = UpdateAccountForm()
   # Validate the form when it's submitted:
   if form.validate_on_submit():
       # If there is a profile picture in the update field:
       if form.picture.data:
           # Save the picture and give back the file name:
            picture_file = save_picture(form.picture.data)
            # Set the picture_file to the image_file.
            # 'image_file' is defined below.
            current_user.image_file = picture_file

       # Set the current user's username in db to the new one submitted in the form.
       current_user.username = form.username.data
       # Set the current user's email in db to the new one submitted in the form.
       current_user.email = form.email.data
       # Commit these changes to the database:
       db.session.commit()
       # Add a flash message to notify user that the account has been updated.
       flash('Your account has been updated!', 'success')
       return redirect(url_for('account'))
   # Display the current username and email:
   elif request.method == 'GET':
       form.username.data = current_user.username
       form.email.data = current_user.email
   # current_user.image_file is a column in User's database, in 'models.py'.
   # In that column, there is a default='default.jpg'.
   image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
   # Pass the image_file into the account template so it can be used in the html:
   return render_template('account.html', title='Acount', 
                          image_file=image_file, form=form)

# Enabling GET and POST:
@app.route("/post/new", methods=['GET', 'POST'])
# Require the user to be logged in:
@login_required
def new_post():
    # Add our 'post' from forms.py into the route here:
    form = PostForm()
    # Add validation:
    if form.validate_on_submit():
        # Fills in database from the form that's filled in by the user.
        # 'author' is the backref used by User in models.py:
        # backref='author'
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        # Add the post to the database:
        db.session.add(post)
        # Commit the post to the database:
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    # Add form=form so we can pass it into the template:
    return render_template('create_post.html', title='New Post', form=form)

# <post_id> puts the 'int:post_id' integer variable into the route:
# e.g. /post/1
@app.route("/post/<int:post_id>")
# post_id is passed in as an argument.
def post(post_id):
    # get_or_404 = convenient method to get something or post a 404 error.
    post = Post.query.get_or_404(post_id)
    # post.html = url, title = the title of the page, 
    # post = passing the 'post'variable to the html page.
    return render_template('post.html', title=post.title, post=post)
