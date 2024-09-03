from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(150), unique=True)
    passwordHash = db.Column(db.String(20))
    isVerified = db.Column(db.Boolean(), default = False)