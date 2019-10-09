from flask import render_template, flash, redirect, url_for, request, g
from app import app, db, login
from models import User, Password, Posts, Friends, Comments
from flask_login import login_user, login_required, current_user, logout_user
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm, ResetPasswordRequestForm, ResetPasswordForm, LoginForm, RegisterForm, EnableAccountRequestForm
from app.email import send_password_reset_email, send_enable_account_email
from datetime import datetime
import os
# this file contains all the different routes, and the logic for communicating with the database


# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.username))
    form = IndexForm()
    loginForm = LoginForm()
    registerForm = RegisterForm()
    if form.login.is_submitted() and form.login.submit.data:
        user = User.query.filter_by(username=form.login.username.data).first()
        if user and user.is_blocked:
            flash('Your account is blocked/inactive. Please click on link below to reactivate it.')
            return redirect(url_for('index'))
        else:
            if user and user.check_password(form.login.password.data): 
                login_user(user, remember=loginForm.remember_me.data)
                try:
                    user.last_login_try = datetime.utcnow
                    user.failed_logins = 0
                    db.session.commit()
                except:
                    db.session.rollback()
                return redirect(url_for('profile', username = form.login.username.data))
            elif user and not user.check_password(form.login.password.data):
                try: 
                    user.failed_logins += 1
                    user.last_login_try = datetime.utcnow()
                    if user.failed_logins >= 3:
                        user.is_blocked = True
                    db.session.commit()
                except:
                    db.session.rollback()
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
                flash("Registration successful! Please check your email to activate your account.")
                send_enable_account_email(new_user)
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
@login_required
def stream(username):
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PostForm()
    if current_user.username != username:
        return redirect(url_for('stream', title='Stream', username = current_user.username))
    user = User.query.filter_by(username=username).first()
    if form.validate_on_submit():
        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)
        try:
            new_post = Posts(u_id = user.id, content = form.content.data, image = form.image.data.filename)
            db.session.add(new_post)
            db.session.commit()
        except:
            db.session.rollback()
            #return redirect(url_for('stream', username=current_user.username))
        #query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'
        #         .format(user['id'], form.content.data, form.image.data.filename, datetime.now()))    

    posts = db.session.execute('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN User AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id=:val) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id=:val) OR p.u_id=:val ORDER BY p.creation_time DESC;', {'val': user.id})
    #posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)


# comment page for a given post and user.
@app.route('/post/<int:p_id>', methods=['GET', 'POST'])
@login_required
def posts(p_id):
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    form = CommentsForm()

    e = db.session.execute(
        'SELECT f_id FROM Friends WHERE u_id = :u_id AND f_id = (SELECT u_id FROM Posts WHERE id = :p_id)',
        {'u_id': current_user.id, 'p_id': p_id})
    friend_id = [row['f_id'] for row in e]
    post = Posts.query.filter_by(id=p_id).first()

    if len(friend_id) == 0 and not current_user.id == post.u_id:
        return redirect(url_for('stream', username=current_user.username))

    if form.validate_on_submit():
        try:
            new_comment = Comments(p_id = p_id, u_id = current_user.id, comment = form.comment.data)
            db.session.add(new_comment)
            db.session.commit()
        except:
            db.session.rollback()
    all_comments = db.session.execute('SELECT DISTINCT * FROM Comments AS c JOIN User AS u ON c.u_id=u.id WHERE c.p_id=:val ORDER BY c.creation_time DESC;', {'val': p_id})
    if len(friend_id) == 0:
        poster_name = current_user.username
    else:
        poster_name = User.query.get(friend_id[0]).username
    return render_template('comments.html', title='Comments', username=current_user.username, form=form, post=post, comments=all_comments, poster_name=poster_name)


# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    if current_user.username != username:
        return redirect(url_for('friends', username = current_user.username))
    form = FriendsForm()
    user = User.query.filter_by(username = username).first()
    if form.validate_on_submit():
        friend = User.query.filter_by(username = form.username.data).first()
        print(friend)
        if friend is None:
            flash('User does not exist')
        else:
            try:
                new_friend = Friends(u_id = user.id, f_id = friend.id)
                db.session.add(new_friend)
                db.session.commit()
                print('success')
            except:
                db.session.rollback()
                flash('Something went wrong, please try again.')

    all_friends = db.session.execute('SELECT * FROM Friends AS f JOIN User as u ON f.f_id=u.id WHERE f.u_id=:val AND f.f_id!=:val2 ;', {'val': user.id, 'val2': user.id})
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)


# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = ProfileForm()
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        try:
            if form.education.data is not None:
                user.education = form.education.data
            if form.employment.data is not None:
                user.employment = form.employment.data
            if form.music.data is not None:
                user.music = form.music.data
            if form.movie.data is not None:
                user.movie = form.movie.data
            if form.nationality.data is not None:
                user.nationality = form.nationality.data
            if form.birthday.data is not None:
                user.birthday = form.birthday.data
            db.session.commit()
            return render_template('profile.html', title='profile', username=current_user.username, user=current_user, form=form)
        except:
            db.session.rollback()

            flash('An error occured while updating your profile. Please try again.')
            return redirect(url_for('profile', username=username, user=user, form=form))
    elif form.is_submitted():
        flash('An error occured while updating your profile. Please try again.')
        return render_template('profile.html', username=username, user=user, form=form)

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
        return redirect(url_for('profile', username=current_user.username))
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
        return redirect(url_for('profile', username = current_user.username))
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


@app.route('/enable_account_request', methods=['GET', 'POST'])
def enable_account_request():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.username))
    form = EnableAccountRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.is_blocked:
            send_enable_account_email(user)
        flash('Check your mail for further instructions.')
        return redirect(url_for('index'))
    return render_template('enable_account_request.html', title='Enable Account', form=form)


@app.route('/enable_account/<token>', methods=['GET'])
def enable_account(token):
    if current_user.is_authenticated:
        return redirect(url_for('profile', username = current_user.username))
    user = User.verify_enable_account_token(token)
    if not user:
        return redirect(url_for('index'))
    else:
        try:
            user.is_blocked = False;
            user.failed_logins = 0
            flash('Your account has been enabled. Please log in.')
            db.session.commit()
        except:
            flash('Something went wrong, please try again.')
            db.session.rollback()
        return redirect(url_for('index'))
    return render_template('reset_password.html', title='Enable Account', user=user)
