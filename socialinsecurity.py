# configured as the entry point of the app, simply imports app to start application, just run 'flask run' to start
from app import app, os, db
from models import User, Posts, Password, Comments, Friends

@app.shell_context_processor
def make_shell_contect():
    return{'db': db, 'User': User, 'Posts': Posts, 'Password': Password, 'Comments': Comments, 'Friends': Friends}
