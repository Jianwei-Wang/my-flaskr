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
#from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, abort, \
     render_template, flash
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
#from flask_wtf import Form
#from wtforms import StringField, TextAreaField, SubmitField, PasswordField
#from wtforms.validators import DataRequired, Email
from forms import RegisteForm, LoginForm, ComposeForm, ProfileForm, EditProfileAdminForm
from flask.ext.sqlalchemy import SQLAlchemy
from decorators import permission_required, admin_required
from flask.ext.moment import Moment
from flask.ext.pagedown import PageDown

# create our little application :)
app = Flask(__name__)
app.debug = True

db = SQLAlchemy(app)

from models import Compose, User, Permission, Role, AnonymousUser
db.event.listen(Compose.body, 'set', Compose.on_changed_body)
login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'login'
login_manager.anonymous_user = AnonymousUser
login_manager.init_app(app)

moment = Moment(app)

pagedown = PageDown(app)

@login_manager.user_loader
def get_user(ident):
#    from models import User
    return User.query.filter_by(id = int(ident)).first()

# Load default config and override config from an environment variable
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    FLASK_COPOSE_PER_PAGE = 10,
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)



#def connect_db():
#    """Connects to the specific database."""
#    rv = sqlite3.connect(app.config['DATABASE'])
#    rv.row_factory = sqlite3.Row
#    return rv


#def init_db():
#    """Initializes the database."""
#    db = get_db()
#    with app.open_resource('schema.sql', mode='r') as f:
#        db.cursor().executescript(f.read())
#    db.commit()

#from sqlalchemy import Column, Integer, String, Text
#from werkzeug.security import generate_password_hash, check_password_hash
#from flask.ext.login import UserMixin
#
#class User(UserMixin, db.Model):
#    __tablename__ = 'users'
#    id = Column(Integer, primary_key = True)
#    name = Column(String(128), nullable = False, unique = True, index = True)
#    email = Column(String(64), nullable = False, unique = True, index = True)
#    password_hash = Column(String(128))
#
#    @property
#    def password(self):
#        raise AttributeError('password is not a readable attribute')
#    @password.setter
#    def password(self, password):
#        self.password_hash = generate_password_hash(password)
#    
#    def verify_password(self, password):
#        return check_password_hash(self.password_hash, password)
#
#class Compose(db.Model):
#    __tablename__ = 'composes'
#    id = Column(Integer, primary_key = True)
#    title = Column(Text, nullable = False)
#    content = Column(Text, nullable = False)

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    from sqlite_flask_create import init_db
    init_db()
    print('Initialized the database.')


#def get_db():
#    """Opens a new database connection if there is none yet for the
#    current application context.
#    """
#    if not hasattr(g, 'sqlite_db'):
#        g.sqlite_db = connect_db()
#    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
#    from models import db
    db.session.close()
#    if hasattr(g, 'sqlite_db'):
#        g.sqlite_db.close()

@app.before_first_request
def before_request():
    if current_user is not None:
        current_user.ping()


@app.route('/', methods=['GET', 'POST'])
def show_entries():
#    db = get_db()
#    cur = db.execute('select title, text from entries order by id desc')
#    entries = cur.fetchall()
  #  from models import db, Compose, User
    form = ComposeForm()
    composes = Compose.query.order_by(Compose.timestamp.desc()).all()
    page = request.args.get('page', 1, type = int)
    pagination = Compose.query.order_by(Compose.timestamp.desc()).paginate(
                 page, per_page = app.config['FLASK_COPOSE_PER_PAGE'],
                 error_out = False)
#    composes = pagination.items

    if current_user.can(Permission.WRITE_ARTICLES) and \
       form.validate_on_submit():
        new_compose = Compose(title = form.title.data,
                              body = form.body.data,
                              author = current_user._get_current_object())
        db.session.add(new_compose)
        db.session.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('show_entries'))

    return render_template('show_entries.html', form=form, entries=composes,
                           pagination = pagination, Permission=Permission,
                           pagedown = pagedown)

@app.route('/composes/<int:id>')
def compose(id):
    compose = Compose.query.get_or_404(id)
    return render_template('compose.html', composes = [compose])

@app.route('/edit/<int:id>', methods = ['get', 'post'])
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
        return redirect(url_for('compose', id=compose.id))
    form.body.data = compose.body
    return render_template('edit.html', form = form, compose = compose)


@app.route('/register', methods=['GET', 'POST'])
def register():
#    from models import db, User
    form = RegisteForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name = form.username.data).first()
        if user:
            flash('Username exist, try other name')
            return redirect(url_for('register'))
        else:
            user = User.query.filter_by(email = form.email.data).first()
            if user:
                flash('This email had registed already! try other email')
                return redirect(url_for('register'))
            else:
                new_user = User(name = form.username.data,
                                password = form.password.data,
                                email = form.email.data)
                db.session.add(new_user)
                db.session.commit()
                flash('You can login now.')
                return redirect(url_for('login'))
    else:
        flash('Fill in block')
    return render_template('register.html', form = form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(name = username).first()
    if user is None:
        abort(404)
    composes = user.composes.order_by(Compose.timestamp.desc()).all()
    return render_template('user.html', user = user, composes = composes)

@app.route('/edit-profile', methods=['get', 'post'])
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
	return redirect(url_for('.user', username = current_user.name))
    form.real_name.data = current_user.real_name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form = form)

@app.route('/edit-profile/<int:id>', methods = ['get', 'post'])
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
	return redirect(url_for('.user', username = user.name))
    form.name.data = user.name 
    form.email.data = user.email 
    form.real_name.data = user.real_name 
    form.location.data = user.location 
    form.about_me.data = user.about_me 
    form.role.data = user.role_id
    return render_template('edit_profile_admin.html', form = form, user = user)
    
    
#@app.route('/add', methods=['POST'])
#@login_required
#def add_entry():
#    from models import dbsession, Compose, User
##    if not session.get('logged_in'):
##        abort(401)
##    db = get_db()
##    db.execute('insert into entries (title, text) values (?, ?)',
##               [request.form['title'], request.form['text']])
##    db.commit()
#    new_compose = Compose(title = request.form['title'],
#                           content = request.form['text'])
#    dbsession.add(new_compose)
#    dbsession.commit()
#    flash('New entry was successfully posted')
#    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
   # from models import db, Compose, User
    error = None

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name = form.name.data).first()
        if not user:
            error = 'Invalid username'
        else:
            if not user.verify_password(form.password.data):
                error = 'Invalid password'
#            if request.form['username'] != app.config['USERNAME']:
#                error = 'Invalid username'
#            elif request.form['password'] != app.config['PASSWORD']:
#                error = 'Invalid password'
            else:
                login_user(user)
                flash('You were logged in')
                return redirect(url_for('show_entries'))

    return render_template('login.html', form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('show_entries'))
