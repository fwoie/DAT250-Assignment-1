import os
#Fallback value in case SQLALCHEMY_DATABASE_URI doesn't provide a path.
basedir = os.path.abspath(os.path.dirname(__file__))
# contains application-wide configuration, and is loaded in __init__.py


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SecretPasswordForGroup17FOBQS' # TODO: Use this with wtforms
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_PATH = 'app/static/uploads'
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = "uistestkonto@gmail.com"
    MAIL_PASSWORD = "cajdfnhwplsfrrcq"
    ADMINS = ['reset@SocialInsecurity.com']
    ALLOWED_EXTENSIONS = {}  # Might use this at some point, probably don't want people to upload any file type
