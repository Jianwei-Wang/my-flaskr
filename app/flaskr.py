# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from flask import Blueprint, request, g, redirect, url_for, abort, render_template, flash
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import login_required, login_user, logout_user, current_user
from forms import RegisteForm, LoginForm, ComposeForm, ProfileForm, EditProfileAdminForm
from decorators import permission_required, admin_required
from app import pagedown, login_manager
from models import Compose, User, Permission

main = Blueprint('main', __name__)

@login_manager.user_loader
def get_user(ident):
#    from models import User
    return User.query.filter_by(id = int(ident)).first()

# @main.cli.command('initdb')
# def initdb_command():
    # """Creates the database tables."""
    # from sqlite_flask_create import init_db
    # init_db()
    # print('Initialized the database.')

# @main.teardown_appcontext
# def close_db(error):
    # """Closes the database again at the end of the request."""
# #    from models import db
    # db.session.close()
# #    if hasattr(g, 'sqlite_db'):
# #        g.sqlite_db.close()

# @app.before_first_request
# def before_request():
    # if current_user is not None:
        # current_user.ping()


@main.route('/', methods=['GET', 'POST'])
def show_entries():
    form = ComposeForm()
    page = request.args.get('page', 1, type = int)
    pagination = Compose.query.order_by(Compose.timestamp.desc()).paginate(
                 page, per_page = 10,
                 error_out = False)
    composes = pagination.items

    if current_user.can(Permission.WRITE_ARTICLES) and \
       form.validate_on_submit():
        new_compose = Compose(title = form.title.data,
                              body = form.body.data,
                              author = current_user._get_current_object())
        db.session.add(new_compose)
        db.session.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('main.show_entries'))

    return render_template('show_entries.html', form=form, entries=composes,
                           pagination = pagination, Permission=Permission,
                           pagedown = pagedown)

@main.route('/composes/<int:id>')
def compose(id):
    compose = Compose.query.get_or_404(id)
    return render_template('compose.html', composes = [compose])

@main.route('/edit/<int:id>', methods = ['get', 'post'])
@login_required
def edit(id):
    compose = Compose.query.get_or_404(id)
    if current_user != compose.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = ComposeForm()
    if form.validate_on_submit():
        compose.body = form.body.data
        db.session.add(compose)
        db.session.commit()
        flash('The article has been updated.')
        return redirect(url_for('main.compose', id=compose.id))
    form.body.data = compose.body
    return render_template('edit.html', form = form, compose = compose)


@main.route('/register', methods=['GET', 'POST'])
def register():
#    from models import db, User
    form = RegisteForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name = form.username.data).first()
        if user:
            flash('Username exist, try other name')
            return redirect(url_for('main.register'))
        else:
            user = User.query.filter_by(email = form.email.data).first()
            if user:
                flash('This email had registed already! try other email')
                return redirect(url_for('main.register'))
            else:
                new_user = User(name = form.username.data,
                                password = form.password.data,
                                email = form.email.data)
                db.session.add(new_user)
                db.session.commit()
                flash('You can login now.')
                return redirect(url_for('main.login'))
    else:
        flash('Fill in block')
    return render_template('register.html', form = form)

@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(name = username).first()
    if user is None:
        abort(404)
    composes = user.composes.order_by(Compose.timestamp.desc()).all()
    return render_template('user.html', user = user, composes = composes)

@main.route('/edit-profile', methods=['get', 'post'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
	current_user.real_name = form.real_name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
	db.session.add(current_user)
	db.session.commit()
	flash('Your profile has been updated.')
	return redirect(url_for('main.user', username = current_user.name))
    form.real_name.data = current_user.real_name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form = form)

@main.route('/edit-profile/<int:id>', methods = ['get', 'post'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user = user)
    if form.validate_on_submit():
        user.name = form.name.data
	user.email = form.email.data
	user.real_name = form.real_name.data
	user.location = form.location.data
	user.about_me = form.about_me.data
	user.role = Role.query.get(form.role.data)
	db.session.add(user)
	db.session.commit()
	flash('The profile has been updated.')
	return redirect(url_for('main.user', username = user.name))
    form.name.data = user.name 
    form.email.data = user.email 
    form.real_name.data = user.real_name 
    form.location.data = user.location 
    form.about_me.data = user.about_me 
    form.role.data = user.role_id
    return render_template('edit_profile_admin.html', form = form, user = user)
    
@main.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name = form.name.data).first()
        if not user:
            error = 'Invalid username'
        else:
            if not user.verify_password(form.password.data):
                error = 'Invalid password'
            else:
                login_user(user)
                flash('You were logged in')
                return redirect(url_for('main.show_entries'))

    return render_template('login.html', form=form, error=error)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('main.show_entries'))
