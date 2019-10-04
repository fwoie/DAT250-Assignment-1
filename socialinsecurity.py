# configured as the entry point of the app, simply imports app to start application, just run 'flask run' to start
from app import app, os

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' \
  #                                     + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database2.db')
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
