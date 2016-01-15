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
#from sqlite_sqlalchemy_create import init_db, dbsession, Compose, User


# create our little application :)
app = Flask(__name__)
app.debug = True
login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def get_user(ident):
    from sqlite_sqlalchemy_create import User, dbsession
    return dbsession.query(User).filter(User.id == int(ident)).one()

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
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


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    from sqlite_sqlalchemy_create import init_db
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
    from sqlite_sqlalchemy_create import dbsession
    dbsession.close()
#    if hasattr(g, 'sqlite_db'):
#        g.sqlite_db.close()


@app.route('/')
def show_entries():
#    db = get_db()
#    cur = db.execute('select title, text from entries order by id desc')
#    entries = cur.fetchall()
    from sqlite_sqlalchemy_create import dbsession, Compose, User
    entries = dbsession.query(Compose).all()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
@login_required
def add_entry():
    from sqlite_sqlalchemy_create import dbsession, Compose, User
#    if not session.get('logged_in'):
#        abort(401)
#    db = get_db()
#    db.execute('insert into entries (title, text) values (?, ?)',
#               [request.form['title'], request.form['text']])
#    db.commit()
    new_compose = Compose(title = request.form['title'],
                           content = request.form['text'])
    dbsession.add(new_compose)
    dbsession.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    from sqlite_sqlalchemy_create import dbsession, Compose, User
    error = None
    if request.method == 'POST':
        try:
            user = dbsession.query(User).filter(User.name == request.form['username']).one()
            if not user.verify_password(request.form['password']):
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
        except (NoResultFound, MultipleResultsFound):
            error = 'Invalid username'

    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
