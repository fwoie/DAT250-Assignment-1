from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
# import sqlite3
import os

# create and configure app
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
mail = Mail(app)


# TODO: Handle login management better, maybe with flask_login?
login = LoginManager(app)
login.init_app(app)
login.login_view = 'login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# TODO: Add more specific queries to simplify code


# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])


from app import routes
