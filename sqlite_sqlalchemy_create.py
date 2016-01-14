from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)

class Composes(Base):
    __tablename__ = 'composes'
    id = Column(Integer, primary_key = True)
    title = Column(Text, nullable = False)
    content = Column(Text, nullable = False)

engine = create_engine('sqlite:///sqlalchemy_sqlite.db')
Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
dbsession = DBsession()

def initdb():
    new_user = Users(name = 'wangjw', email = '550466233@qq.com')
    dbsession.add(new_user)
    dbsession.commit()
    
    new_compose = Composes(title = 'Love', content = 'I love you!')
    dbsession.add(new_compose)
    dbsession.commit()
    dbsession.close()

if __name__ == '__main__':
    initdb()
