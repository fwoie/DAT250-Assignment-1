from flask_login import UserMixin
from app import database
from datetime import datetime


class Friend(database.Model):
    __tablename__ = 'Friends'
    friend_id = database.Column(database.Integer, database.ForeignKey('users.id'), primary_key=True)
    friend_of_id = database.Column(database.Integer, database.ForeignKey('users.id'), primary_key=True)
    timestamp = database.Column(database.DateTime, default=datetime.utcnow)


class User(UserMixin, database.Model):
    __tablename__ = 'Users'
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    username = database.Column(database.String(30), unique=True)
    # email = database.Column(database.String(30))
    password = database.Column(database.String(100))
    first_name = database.Column(database.String(30))
    last_name = database.Column(database.String(30))
    education = database.Column(database.String(30))
    employment = database.Column(database.String(30))
    music = database.Column(database.String(30))
    movie = database.Column(database.String(30))
    nationality = database.Column(database.String(30))
    birthday = database.Column(database.Date)
    comments = database.relationship('Comment', backref='user', lazy='dynamic')
    friends = database.relationship('Friend', foreign_keys=[Friend.follower_id],
                                    backref=database.backref('friend', lazy='joined'),
                                    lazy='dynamic', cascade='all, delete-orphan')

    friend_of = database.relationship('Friend', foreign_keys=[Friend.followed_id],
                                      backref=database.backref('friend_of', lazy='joined'),
                                      lazy='dynamic', cascade='all, delete-orphan')


class Post(database.Model):
    __tablename__ = 'Posts'
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    written_by = database.Column(database.Integer, database.ForeignKey('Users.id'))
    body = database.Column(database.Text)
    # body_html = database.Column(database.Text)
    timestamp = database.Column(database.DateTime, index=True, default=datetime.utcnow)
    comments = database.relationship('Comment', backref='post', lazy='dynamic')


class Comment(database.Model):
    __tablename__ = 'Comments'
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    written_by = database.Column(database.Integer, database.ForeignKey('Users.id'))
    post_id = database.Column(database.Integer, database.ForeignKey('Posts.id'))
    body = database.Column(database.Text)
    body_html = database.Column(database.Text)
    creation_time = database.Column(database.DateTime, index=True, default=datetime.utcnow)
    disabled = database.Column(database.Boolean)

