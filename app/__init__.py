import os
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.moment import Moment
from flask.ext.pagedown import PageDown
from flask.ext.bootstrap import Bootstrap

db = SQLAlchemy()
pagedown = PageDown()
moment = Moment()
bootstrap = Bootstrap()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    db.init_app(app)
    pagedown.init_app(app)
    moment.init_app(app)
    bootstrap.init_app(app)
    # Load default config and override config from an environment variable
    app.config.update(dict(
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'flaskr.db'),
        DEBUG=True,
        SECRET_KEY='development key',
        FLASK_COPOSE_PER_PAGE = 10,
    ))
    app.config.from_envvar('FLASKR_SETTINGS', silent=True)

    from models import Compose, User, Permission, Role, AnonymousUser
    db.event.listen(Compose.body, 'set', Compose.on_changed_body)
    login_manager.session_protection = 'basic'
    login_manager.login_view = 'main.login'
    login_manager.anonymous_user = AnonymousUser
    login_manager.init_app(app)
    from flaskr import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
