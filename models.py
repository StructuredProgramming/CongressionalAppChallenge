from imports import *


def _User(db):
    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(32), nullable=False, unique=True)
        password = db.Column(db.String(128), nullable=False)
    
    return User


def _Post(db):
    class Post(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        is_reply = db.Column(db.Boolean, default=False, nullable=True)
        reply_id = db.Column(db.Integer, default=0, nullable=True)
        owner = db.Column(db.Integer)
        Title = db.Column(db.String(100), default="Untitled")
        Body = db.Column(db.String(1000), nullable=False)
        upvotes = db.Column(
            db.Integer, default=0, nullable=True
        )  # remember to change Title, Body, upvotes and downvotes to be mutable
        downvotes = db.Column(db.Integer, default=0, nullable=True)
    
    return Post

def _Tag(db):
    class Tag(db.Model, UserMixin):
        id = db.Column(
            db.Integer, primary_key=True
        )  # don't rlly need this, just for the sake of having a unique id
        tag_string = db.Column(db.String(32), unique=True)
        tag_to = db.Column(db.Integer)
    
    return Tag


