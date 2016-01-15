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
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import LoginManager, login_required, login_user, logout_user
from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
from flask.ext.sqlalchemy import SQLAlchemy


# create our little application :)
app = Flask(__name__)
app.debug = True
login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'login'
login_manager.init_app(app)

db = SQLAlchemy(app)

@login_manager.user_loader
def get_user(ident):
#    from models import User
    return User.query.filter_by(id = int(ident)).first()

# Load default config and override config from an environment variable
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

class RegisteForm(Form):
    username = StringField('username', validators = [DataRequired()])
    email = StringField('username', validators = [DataRequired(), Email()])
    password = PasswordField('password', validators = [DataRequired()])
    confirm = PasswordField('confirm', validators = [DataRequired()])
    submit = SubmitField('submit')

class LoginForm(Form):
    name = StringField('name', validators = [DataRequired()])
    password = PasswordField('password', validators = [DataRequired()])
    submit = SubmitField('submit')

class ArticleForm(Form):
    title = StringField('title', validators = [DataRequired()])
    content = TextAreaField('content', validators = [DataRequired()])
    submit = SubmitField('submit')


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
from models import Compose, User

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


@app.route('/', methods=['GET', 'POST'])
def show_entries():
#    db = get_db()
#    cur = db.execute('select title, text from entries order by id desc')
#    entries = cur.fetchall()
  #  from models import db, Compose, User
    form = ArticleForm()
    entries = Compose.query.all()

    if form.validate_on_submit():
        new_compose = Compose(title = form.title.data,
                           content = form.content.data)
        db.session.add(new_compose)
        db.session.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('show_entries'))

    return render_template('show_entries.html', form=form, entries=entries)

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
                session['logged_in'] = True
                login_user(user)
                flash('You were logged in')
                return redirect(url_for('show_entries'))

    return render_template('login.html', form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
