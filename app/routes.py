from flask import render_template, flash, redirect, url_for, request
from app import app, db, login
from models import User
from flask_login import login_user, login_required, current_user, logout_user
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm, ResetPasswordRequestForm, ResetPasswordForm, LoginForm, RegisterForm
from app.email import send_password_reset_email
from datetime import datetime
import os
# this file contains all the different routes, and the logic for communicating with the database


# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    print("at login")
    form = IndexForm()
    loginForm = LoginForm()
    registerForm = RegisterForm()
    if form.login.is_submitted() and form.login.submit.data:
        # user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True)
        user = User.query.filter_by(username=form.login.username.data).first()

        if user and user.check_password(form.login.password.data):  # and check_password(user.password, password) == True:
            login_user(user, remember=loginForm.remember_me.data)
            return redirect(url_for('profile_test'))

        flash('Sorry, wrong combination of username and password!')

    elif form.register.validate_on_submit():
    #elif form.register.is_submitted() and form.register.submit.data:
        print("register form validated")
        #first_name, last_name = form.register.first_name.data, form.register.last_name.data
        #username = form.register.username.data
        #  query_db('INSERT INTO Users (username, first_name, last_name, password, is_active) VALUES("{}", "{}", "{}", "{}",0);'.format(
        #    username, firstname, lastname, password))
        user = User.query.filter_by(username=form.register.username.data).first()

        if not user:
            new_user = User(username=form.register.username.data, email=form.register.email.data, first_name=form.register.first_name.data, last_name=form.register.last_name.data)
            new_user.set_password(form.register.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!")
            return redirect(url_for('index'))
        else:
            flash('Username taken!')
            return redirect(url_for('index'))

    return render_template('index.html', title='Welcome', form=form)

"""
# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
def stream(username):
    form = PostForm()
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)

        query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'
                 .format(user['id'], form.content.data, form.image.data.filename, datetime.now()))
        return redirect(url_for('stream', username=username))

    posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)


# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
def comments(username, p_id):
    form = CommentsForm()
    if form.is_submitted():
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(p_id, user['id'], form.comment.data, datetime.now()))

    post = query_db('SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
    all_comments = query_db('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)


# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
def friends(username):
    form = FriendsForm()
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        friend = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.username.data), one=True)
        if friend is None:
            flash('User does not exist')
        else:
            query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))
    
    all_friends = query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)


# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    form = ProfileForm()
    if form.is_submitted():
        query_db('UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
            form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username
        ))
        return redirect(url_for('profile', username=username))
    
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    return render_template('profile.html', title='profile', username=username, user=user, form=form)
"""

@login_required
@app.route('/test', methods=['GET', 'POST'])
def profile_test():
    form = ProfileForm()
    return render_template('test.html', form=form)


@login_required
@app.route('/index', methods=['GET', 'POST'])
def logout():
    form = IndexForm()
    print("heisann")
    logout_user()
    flash("You are now logged out")
    return render_template('index.html', title='Welcome', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    print("linje133")
    #if current_user.is_authenticated:
    #    return redirect(url_for('profile_test'))#Dette må endre til Profile.
    form = ResetPasswordRequestForm()
    print("linje137")
    if form.validate_on_submit():
        print("linje139")
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your mail for further instructions.')
        return redirect(url_for('index'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)
                           
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    #if current_user.is_authenticated:
    #    return redirect(url_for('profile_test'))#Denne må endre til profile.
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('index'))
    return render_template('reset_password.html', form=form)