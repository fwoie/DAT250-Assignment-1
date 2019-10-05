# configured as the entry point of the app, simply imports app to start application, just run 'flask run' to start
from app import app, os, database
from models import User, Posts

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' \
  #                                     + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database2.db')
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

@app.shell_context_processor
def make_shell_contect():
    return('db': db, 'User': User, 'Posts': Posts)
