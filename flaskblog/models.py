from datetime import datetime
# Imports db variable from __init__.py
from flaskblog import db

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
    # 'author' gets the user who created the post. This is an SQLAlchemy feature(?)
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