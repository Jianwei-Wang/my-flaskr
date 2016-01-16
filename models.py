from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from flaskr import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from datetime import datetime
from markdown import markdown
import bleach

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key = True)
    name = Column(String(64), unique = True)
    default = Column(Boolean, default = False, index = True)
    permissions = Column(Integer)
    users = db.relationship('User', backref = 'role', lazy = 'dynamic')

    @staticmethod
    def insert_roles():
        roles = {'User' : (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
                 'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES |
                               Permission.MODERATE_COMMENTS, False),
                 'Administrator' : (0xff, False)}
        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role is None:
                role = Role(name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String(128), nullable = False, unique = True, index = True)
    email = Column(String(64), nullable = False, unique = True, index = True)
    real_name = Column(String(128))
    location = Column(String(128))
    about_me = Column(Text())
    member_since = Column(DateTime(), default = datetime.utcnow)
    last_seen = Column(DateTime())
    password_hash = Column(String(128))
    role_id = Column(Integer, db.ForeignKey('roles.id'))
    composes = db.relationship('Compose', backref = 'author', lazy = 'dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role_id is None:
            self.role = Role.query.filter_by(default = True).first()

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                    name=forgery_py.internet.user_name(True),
                    password=forgery_py.lorem_ipsum.word(),
                    real_name=forgery_py.name.full_name(),
                    location=forgery_py.address.city(),
                    about_me=forgery_py.lorem_ipsum.sentence(),
                    member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

class Compose(db.Model):
    __tablename__ = 'composes'
    id = Column(Integer, primary_key = True)
    title = Column(Text)
    body = Column(Text, nullable = False)
    body_html = Column(Text)
    timestamp = Column(DateTime, index = True, default = datetime.utcnow)
    author_id = Column(Integer, db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
            'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Compose(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()
