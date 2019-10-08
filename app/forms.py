from flask import g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp, Optional
from models import User, Password, Posts
from wtforms.fields.html5 import DateField
from datetime import date
import re
import imghdr

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
    word = word.replace(" ", "")
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
    data = data.replace(" ", "")
    if data == '':
        return
    if not re.match("^[a-zA-Z0-9_]*$", data):
        consonant = ['a', 'e', 'i', 'o', 'u', 'y']
        for element in consonant:
            if field.name[0] == element:
                raise ValidationError('An ' + field.name + ' does not contain a special character')
        raise ValidationError('A ' + field.name + ' does not contain a special character')


def validateImage(form, field):
    if field.data.filename == "":
        return
    img = field.data
    type = imghdr.what(img)
    allowedTypes = ['rgb', 'gif', 'pbm', 'ppm', 'tiff', 'rast', 'xbm', 'jpeg', 'bmp', 'png']
    x = False
    for element in allowedTypes:
        if element == type:
            x = True

    if x is not True:
        raise ValidationError("Filetype not allowed")

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it


class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), checkNoNumber, checkNoSpecialCharacter], render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name', validators=[DataRequired(), checkNoNumber, checkNoSpecialCharacter], render_kw={'placeholder': 'Last Name'})
    username = StringField('Username', validators=[DataRequired(), Length(min=5), Regexp('^\w+$', message='Username must contain only letters, numbers and underscores')], render_kw={'placeholder': 'Username'})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), checkUpperCase, checkLowerCase, checkNumber, checkSpecialCharacter],  render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)


class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image', validators=[validateImage])
    submit = SubmitField('Post')


class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', validators=[DataRequired(), Length(max=140)], render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')


class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', validators=[Regexp('^\w+$', message="A username contains only letters, numbers and underscores")], render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')


class ProfileForm(FlaskForm):
    education = StringField('Education', validators=[isValidProfil], render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', validators=[isValidProfil], render_kw={'placeholder': 'Current employment'})
    email = StringField('Email', validators=[Optional(), Email()], render_kw={'placeholder': 'E-mail address'})
    music = StringField('Favorite song', validators=[isValidProfil], render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', validators=[isValidProfil], render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', validators=[isValidProfil], render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
            
    def validate_birthday(self, birthday):
        if birthday.data is not None and birthday.data > date.today():
            raise ValidationError('This isn\'t back to the future.')
    
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), checkUpperCase, checkLowerCase, checkNumber, checkSpecialCharacter])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')  

    def validate_password(self, password):
        user_id = g.user_id
        passwords = Password.query.filter_by(u_id=user_id).all()
        for p in passwords:
            if p.check_password(password.data):
                raise ValidationError('Password has been used before.') 
                
class EnableAccountRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Account Activation')