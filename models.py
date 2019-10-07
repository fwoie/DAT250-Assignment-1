from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from time import time
import jwt
from app import app, db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), index = True, unique = True)
    email = db.Column(db.String(30), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    education = db.Column(db.String(30))
    employment = db.Column(db.String(30))
    music = db.Column(db.String(30))
    movie = db.Column(db.String(30))
    nationality = db.Column(db.String(30))
    birthday = db.Column(db.Date)
    last_login_try = db.Column(db.DateTime, default = datetime.utcnow)
    failed_logins = db.Column(db.Integer, default = 0)
    is_blocked = db.Column(db.Boolean, default = True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in = 600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
            
    def get_account_enable_token(self, expires_in = 600):
        return jwt.encode(
            {'enable_account': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
        
    @staticmethod
    def verify_enable_account_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['enable_account']
        except:
            return
        return User.query.get(id)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    u_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    content = db.Column(db.Integer)
    image = db.Column(db.String())
    creation_time = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    
    def __repr__(self):
        return '<Post {}>'.format(self.content)

class Password(db.Model):
    u_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    password_hash = db.Column(db.String(128), primary_key = True)
    creation_time = db.Column(db.DateTime, index = True, default = datetime.utcnow)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Password for user #{}>'.format(self.u_id)

class Friends(db.Model):
    u_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    f_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)

    def __repr__(self):
        return '<User #{} is friends with user #{}>'.format(self.u_id, self.f_id)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    p_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    u_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comment = db.Column(db.String())
    creation_time = db.Column(db.DateTime, default = datetime.utcnow)
    
    def __repr__(self):
        return '<Comment body: {}>'.format(self.comment)