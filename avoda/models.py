from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import sqlalchemy.orm as so
from avoda import db
from flask_login import UserMixin
from avoda import login
     
class Users(UserMixin,db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(40))
    password = db.Column(db.String(256), nullable=False)
    isactive = db.Column(db.Integer())
    settings = db.Column(db.String(256))
    issend = db.Column(db.Integer())
    mailsend = db.Column(db.DateTime())
    created = db.Column(db.DateTime())
    roles = db.relationship("Role", secondary="user_role")
    addresses = db.relationship('Posts', lazy=True)



# Define the Role data-model
class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    name = db.Column(db.String(40), unique=True, nullable=False)


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = "user_role"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer(), db.ForeignKey("role.id", ondelete="CASCADE"))


class Posts(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(40), nullable=False)
    place = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(40))
    text = db.Column(db.String(500))
    len=db.Column(db.String(100))
    occupations = db.Column(db.String(100))
    o_kind = db.Column(db.String(100))
    sex = db.Column(db.Integer)
    created = db.Column(db.DateTime())
    updated = db.Column(db.DateTime())
    docs = db.Column(db.String(50))
    contacts = db.Column(db.String(100))
    # Relationship
    user = db.relationship('Users')
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

class Refs(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    value = db.Column(db.String(40), nullable=False)
    levels = db.relationship('Refs')
    levelUp = db.Column(db.Integer,db.ForeignKey("refs.id"))

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    head = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(500))
    link = db.Column(db.String(100))
    created = db.Column(db.DateTime())

@login.user_loader
def load_user(id):
    return db.session.get(Users, int(id))  