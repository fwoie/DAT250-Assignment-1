from flask_login import UserMixin
from app import database


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

