# A model is a class that represents a table or collection in our DB, 
# and where every attribute of the class is a field of the table or collection.

from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# Imports db variable from __init__.py
from flaskblog import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Each class is a table in the database:
# Imports from db.Model.
# UserMixin is inherited from the flask_login Login Manager.
class User(db.Model, UserMixin):
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

    # Get a reset token by setting up the secret key with an expiration time.
    # Return the token with the dumps method, which returns
    # a payload with the current user.
    # expires_seconds=1800 = 30 minute default expiration.
    def get_reset_token(self, expires_sec=1800):
        # Create a Serializer object:
        # app.config['SECRET_KEY']
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        # Return the token:
        # ({ 'user_id' }) = payload
        # self.id = instance of the user
        # self = usual python 'self' for classes, meaning 'this instance'.
        return s.dumps({'user_id': self.id}).decode('utf-8')

    # Tell python not to expect 'self' as an argument.
    @staticmethod
    # Verify the token.
    # Takes a token as an argument.
    def verify_reset_token(token):
        # Creates a Serializer object with a SECRET_KEY.
        # SECRE_KEY is defined in __init__.py
        s = Serializer(app.config['SECRET_KEY'])
        # Because the key or expiry could be invalid, put in a try/except block:
        # If the user is valid...
        try: 
            # Try to load the token.
            # s.loads(token) = loads the token
            # Try to get 'user_id' out of the token.
            # ['user_id'] is the payload that we pass in, 
            # in get_reset_token above -> 'user_id': self.id
            user_id = s.loads(token)['user_id']
        except:
            # If we get an exception, return None.
            # i.e. if the token expired.
            return None
        # If the token is valid, return the User with that user_id.
        return User.query.get(user_id)


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