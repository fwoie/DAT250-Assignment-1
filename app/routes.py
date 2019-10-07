from flask import render_template, flash, redirect, url_for, request, g
from app import app, db, login
from models import User, Password, Posts
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
    form = IndexForm()
    loginForm = LoginForm()
    registerForm = RegisterForm()
    if form.login.is_submitted() and form.login.submit.data:
        # user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True)
        user = User.query.filter_by(username=form.login.username.data).first()

        if user and user.check_password(form.login.password.data):  # and check_password(user.password, password) == True:
            login_user(user, remember=loginForm.remember_me.data)
            return redirect(url_for('profile', username = form.login.username.data))

        flash('Sorry, wrong combination of username and password!')

    elif form.register.validate_on_submit():

        user = User.query.filter_by(username=form.register.username.data).first()
        if not user:
            new_user = User(username=form.register.username.data, email=form.register.email.data, first_name=form.register.first_name.data, last_name=form.register.last_name.data)
            new_user.set_password(form.register.password.data)
            try:
                try:
                    db.session.add(new_user)
                    db.session.commit()
                except:
                    db.session.rollback()
                    flash("Registration unsuccessful, please try again.")
                    return redirect(url_for("index"))
                new_password = Password(u_id=new_user.id, password_hash=new_user.password_hash)
                db.session.add(new_password)
                db.session.commit()
                flash("Registration successful!")
                return redirect(url_for('index'))
            except:
                flash("Registration unsuccessful, please try again.")
                return redirect(url_for("index"))
        else:
            flash('Username taken!')
            return redirect(url_for('index'))

    return render_template('index.html', title='Welcome', form=form)


# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
#@login_required
def stream(username):
    form = PostForm()
    
    user = User.query.filter_by(username=username).first()


    if form.is_submitted():
        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)

        post = Posts(content=form.content.data, image=form.image.data.filename)
        db.session.add(post)
        db.session.commit()




        # query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'
        # .format(user['id'], form.content.data, form.image.data.filename, datetime.now()))
        return redirect(url_for('stream', username=username))

    #posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    posts = Posts.query.all()

    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)


# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
def comments(username, p_id):
    form = CommentsForm()
    """
    if form.is_submitted():
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(p_id, user['id'], form.comment.data, datetime.now()))
    """
    post = Posts.query.filter_by(id = p_id)
    #post = query_db('SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
    #all_comments = query_db('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
    
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)


# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
def friends(username):
    form = FriendsForm()
    """
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        friend = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.username.data), one=True)
        if friend is None:
            flash('User does not exist')
        else:
            query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))
    
    all_friends = query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
    """
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)


# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = ProfileForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        try:
            user.education = form.education.data
            user.employment = form.employment.data
            user.music = form.music.data
            user.movie = form.movie.data
            user.nationality = form.nationality.data
            user.birthday = form.birthday.data
            db.session.commit()
        except:
            db.session.rollback()
            flash('An error occured while updating your profile. Please try again.')
            return redirect(url_for('profile', title='profile', username=username, user=user, form=form))
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', title='profile', username=username, user=user, form=form)


@login_required
@app.route('/test', methods=['GET', 'POST'])
def profile_test():
    form = ProfileForm()
    return render_template('test.html', form=form)


@login_required
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash("You are now logged out")
    return redirect(url_for('index'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your mail for further instructions.')
        return redirect(url_for('index'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)
                           
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    g.user_id = user.id
    form = ResetPasswordForm()
    if form.validate_on_submit():
        #Check if the password has been used before using a custom validator in forms.py
        #Check if the maximum old password limit (5) has been reached.                  
        if db.session.execute('SELECT COUNT(*) FROM User INNER JOIN Password').first()[0] < 5:
            try:
                user.set_password(form.password.data)
                new_password = Password(u_id=user.id, password_hash=user.password_hash)
                db.session.add(new_password)
                db.session.commit()
                flash('Your password has been reset.')
                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash('Something went wrong. Please try again.')
                return redirect(url_for('index'))
        #If so, order passwords by creation_time and delete the oldest entry. Then add the new one.
        else:
            try:
                password = db.session.execute('SELECT P.* FROM User INNER JOIN Password AS P WHERE P.u_id=:val GROUP BY P.creation_time', {'val': user.id}).first()
                db.session.delete(Password.query.filter_by(u_id=password['u_id'], creation_time=password['creation_time']).first())
                user.set_password(form.password.data)
                new_password = Password(u_id=user.id, password_hash=user.password_hash)
                db.session.add(new_password)
                db.session.commit()
                flash('Your password has been reset.')
                return redirect(url_for('index'))
            except:
                db.session.rollback()
                flash('Something went wrong. Please try again.')
                return redirect(url_for('index'))
    return render_template('reset_password.html', title='Reset Password', form=form, user=user)        
