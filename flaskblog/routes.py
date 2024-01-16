# Grabs file extensions:
import os

# Creates a random hex:
import secrets

# Pillow for managing image size.
from PIL import Image

# render_template enables Flask to render html files.
# url_for enables linking to files, e.g. for CSS files:
# <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='main.css') }}">
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                             PostForm, RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

# '@app' allows us to write a function for the route.
@app.route("/")
@app.route("/home")
def home():
    # Grab a query parameter in the URL to get the page the user wants.
    # 'page' is optional parameter, so '1' is default.
    page = request.args.get('page', 1, type=int)
    # Grab all of the posts from the database:
    # Paginate the page so that there are 5 pages on a page.
    # page=page sets the page displayed to the 'page' set above (1 by default).
    # .order_by(Post.date_posted.desc()) changes the order of the posts so newest = top on the page.
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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
    return render_template('create_post.html', title='New Post', 
                           form=form, legend='New Post')

# <post_id> puts the 'int:post_id' integer variable into the route.
# It does this from the template. The home.html template creates a url here:
# The home.html line takes post.id from the Post class in models.py(?)
# href="{{ url_for('post', post_id=post.id) }}"
# This URL id is then sent to the route below(?), which tries
# to get the post_id, and if there isn't one, creates a 404 error.
# e.g. /post/1
@app.route("/post/<int:post_id>")
# post_id is passed in as an argument.
def post(post_id):
    # Get a post with the id that's been passed into the URL:
    # get_or_404 = convenient method to get something or post a 404 error.
    post = Post.query.get_or_404(post_id)
    # post.html = url, title = the title of the page, 
    # post = passing the 'post'variable to the html page.
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
# To update a post, require the user to be logged in.:
@login_required
# post_id is passed in as an argument.
def update_post(post_id):
    # Get a post with the id of the page we're on:
    post = Post.query.get_or_404(post_id)
    # Only the use who wrote this post can update it:
    if post.author != current_user:
        # 403 = forbidden route.
        abort(403)
    # Create a post form.
    form = PostForm()
    # If the form entries are valid:
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        # Commit the changes to the database.
        # Note there is no 'adding,' as the changes are already in the database.
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    # Make sure the form is populated when there is a GET request:
    elif request.method == 'GET':
        # The html form's title is populated with the post.title data.
        form.title.data = post.title
        # The html form's data is populated with the post.content data.
        form.content.data = post.content
    # legend='Update Post' creates a new legend we can use in the template.
    return render_template('create_post.html', title='Update Post', 
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
# To update a post, require the user to be logged in.:
@login_required
# post_id is passed in as an argument.
def delete_post(post_id):
    # Get a post with the id of the page we're on:
    post = Post.query.get_or_404(post_id)
    # Only the use who wrote this post can update it:
    if post.author != current_user:
        # 403 = forbidden route.
        abort(403)
    # Deletes post:
    db.session.delete(post)
    # Commits the delete:
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

# <str:username> = user's user name (a dynmaic parameter)
# username = variable name
@app.route("/user/<string:username>")
def user_posts(username):
    # Grab a query parameter in the URL to get the page the user wants.
    # 'page' is optional parameter, so '1' is default.
    page = request.args.get('page', 1, type=int)
    # Get this user.
    # first_or_404() = get the first user with this user name,
    # if you get a None, just use a 404.
    user = User.query.filter_by(username=username).first_or_404()

    # Grab all of the posts from the database:
    # Paginate the page so that there are 5 pages on a page.
    # page=page sets the page displayed to the 'page' set above (1 by default).
    # .order_by(Post.date_posted.desc()) changes the order of the posts so newest = top on the page.
    # \ just breaks up the line to make it more readable code.
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    # We'll create a new template, and poass in the posts and the user:
    return render_template('user_posts.html', posts=posts, user=user)

# Send the user an email with the reset token:
def send_reset_email(user):
    # Get the token we made in models.py 'get_reset_token':
    token = user.get_reset_token()
    # Send email with the URL of the reset token.
    # '[subject line]', sender email, user email
    msg = Message('Password Reset Request', 
                  sender='temp.email.username.7@gmail.com', 
                  recipients=[user.email])
    # token = token we got for the user above
    # _external = used for getting an absolute URL (rather than relative URL).
    # The link in the email needs to have the full domain.
    # You can use Jinja2 templates for messages if wanted.
    # *Note tabs in the string will actually show up in the email.
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and on changes will be made.
'''# Send the message:
    mail.send(msg)

# User enters email to request password reset:
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    # Make sure that the user is logged out.
    # current_user.is_authenticated = False when user is logged out(?)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    # At this point, they have submitted an email into the form (22:08 in tutoral 10):
    # Forms will submit back to this same route they were rendered from.
    if form.validate_on_submit():
        # Grab the user for that email:
        # User.query.filter_by(email=form.email.data) = the query.
        # .first() = get the first user with that email.
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        # Redirect back to login page:
        return redirect(url_for('login'))
        # Send the user an email with the token.

    return render_template('reset_request.html', title="Reset Password", form=form)

# User resets their password while the token is active:
# The token is passed in as a parameter to the URL.
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        # Make sure that the user is logged out.
        return redirect(url_for('home'))
    # very_reset_token is a static method we defined in models.py,
    # which returns User.query.get(user_id)
    user = User.verify_reset_token(token)
    # If user above is expired or invalid (due to invalid token):
    if user is None:
        # 'warning' = bootstrap alert
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    # If we pass the conditional above (the use IS valid):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # If valid, create hashed password, 
        # taking the form.password.data from the user input.
        # And decode it into a string using decode('utf-8'):
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Set the hash_password to the user's password.
        user.password = hashed_password
        # Commit the changes to the user's password:
        db.session.commit()
        # Then add the 'success' parameter adds a bootstrap class
        # and adds a one time message to the user.
        flash('Your password has been updated! You are now able to log in.', 'success')
        # Redirect user to a different page from the form.
        # 'home' is the name of the FUNCTION, not the route.
        return redirect(url_for('login'))
    # Render and send the 'reset password' form to the template.
    return render_template('reset_token.html', title="Reset Password", form=form)
