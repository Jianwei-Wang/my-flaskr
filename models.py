from sqlalchemy import Column, Integer, String, Text
from flaskr import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String(128), nullable = False, unique = True, index = True)
    email = Column(String(64), nullable = False, unique = True, index = True)
    password_hash = Column(String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Compose(db.Model):
    __tablename__ = 'composes'
    id = Column(Integer, primary_key = True)
    title = Column(Text, nullable = False)
    content = Column(Text, nullable = False)
