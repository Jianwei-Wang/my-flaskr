from flaskr import db
from models import User, Compose

def init_db():
    db.create_all()

    new_user = User(name = 'wangjw', password = '121', email = '550466233@qq.com')
    db.session.add(new_user)
    new_user = User(name = 'luofl', password = '123', email = 'w550466233@163.com')
    db.session.add(new_user)
    db.session.commit()
    
    new_compose = Compose(title = 'Love', content = 'I love you!')
    db.session.add(new_compose)
    db.session.commit()
    db.session.close()

if __name__ == '__main__':
    init_db()
    print 'Initialized the database.'
