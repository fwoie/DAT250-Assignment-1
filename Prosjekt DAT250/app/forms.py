from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField, validators, ValidationError
from wtforms.fields.html5 import DateField
import re
import imghdr
from app import app, query_db
from datetime import date

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it

today = date.today()

def checkSpecialCharacter(form, field):
    word = field.data
    if re.match("^[a-zA-Z0-9_]*$", word):
        raise ValidationError('Password need at least one Special character.')

def checkNumber(form, field):
    word = field.data
    if not re.search('\d', word):
        raise ValidationError('Password need at least one number.')

def checkNoNumber(form, field):
    word = field.data
    if re.search('\d', word):
        raise ValidationError('A name does not contain a number')

def checkNoSpecialCharacter(form, field):
    word = field.data
    if not re.match("^[a-zA-Z0-9_]*$", word):
        raise ValidationError('A name does not contain a special character')

def checkUpperCase(form, field):
    x = 0
    for element in field.data:
        if element.isupper() == True:
            x += 1

    if x == 0:
        raise ValidationError('Password need at least one upper case letter.')

def checkLowerCase(form, field):
    x = 0
    for element in field.data:
        if element.islower() == True:
            x += 1

    if x == 0:
        raise ValidationError('Password need at least one lower case letter.')

def userEx(form, field):
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(field.data), one=True)
    if user != None:
        raise ValidationError('This username is in use, please choose another one')

def isValidProfil(form, field):
    data = field.data
    if data == '':
        return
    if not re.match("^[a-zA-Z0-9_]*$", data):
        consonant = ['a', 'e', 'i', 'o', 'u', 'y']
        for element in consonant:
            if field.name[0] == element:
                raise ValidationError('An ' + field.name + ' does not contain a special character')
        raise ValidationError('A ' + field.name + ' does not contain a special character')

def checkDate(form, field):
    if field.data > date.today():
        raise ValidationError('We have not come to this date')


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=5), validators.Regexp('^\w+$', message="Username must contain only letters, numbers and underscores")], render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', [validators.Length(min=8), checkUpperCase, checkLowerCase, checkNumber, checkSpecialCharacter], render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', [validators.InputRequired(), checkNoNumber, checkNoSpecialCharacter], render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name', [validators.InputRequired(), checkNoNumber, checkNoSpecialCharacter], render_kw={'placeholder': 'Last Name'})
    username = StringField('Username', [validators.Length(min=5), userEx, validators.Regexp('^\w+$', message="Username must contain only letters, numbers and underscores")], render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', [validators.Length(min=8), checkUpperCase, checkLowerCase, checkNumber, checkSpecialCharacter], render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password', [validators.EqualTo('password',message="Do not match Password!")],render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image')
    submit = SubmitField('Post')

    #[FileAllowed(['rgb', 'gif', 'pbm', 'pgm', 'ppm', 'tiff', 'rast', 'xbm', 'jpeg', 'bmp', 'png'], "Images only!")]

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')

class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', [validators.Regexp('^\w+$', message="A username contains only letters, numbers and underscores")], render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')

class ProfileForm(FlaskForm):
    education = StringField('Education', [isValidProfil], render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', [isValidProfil], render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', [isValidProfil], render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', [isValidProfil], render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', [isValidProfil], render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday', [validators.DataRequired(message="format: YYYY-mm-dd"), checkDate], format='%Y-%m-%d')
    submit = SubmitField('Update Profile')
