from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flaskr import app
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin


Base = declarative_base()

class User(UserMixin, Base):
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

class Compose(Base):
    __tablename__ = 'composes'
    id = Column(Integer, primary_key = True)
    title = Column(Text, nullable = False)
    content = Column(Text, nullable = False)

engine = create_engine('sqlite:///' + app.config['DATABASE'])
Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
dbsession = DBsession()

def init_db():
    new_user = User(name = 'wangjw', password = '121', email = '550466233@qq.com')
    dbsession.add(new_user)
    dbsession.commit()
    new_user = User(name = 'luofl', password = '123', email = 'w550466233@163.com')
    dbsession.add(new_user)
    dbsession.commit()
    
    new_compose = Compose(title = 'Love', content = 'I love you!')
    dbsession.add(new_compose)
    dbsession.commit()
    dbsession.close()

if __name__ == '__main__':
    init_db()
