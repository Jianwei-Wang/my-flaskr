from app import db, create_app
from app.models import User, Compose, Role

def init_db():

    app = create_app()
    with app.app_context():
    	db.create_all()

   	Role.insert_roles()

   	new_user = User(name = 'wangjw', password = '121', email = '550466233@qq.com',
   	                role_id = Role.query.filter_by(name = 'Administrator').first().id)
   	db.session.add(new_user)
   	new_user = User(name = 'luofl', password = '123', email = 'w550466233@163.com',
   	                role_id = Role.query.filter_by(name = 'Moderator').first().id)
   	db.session.add(new_user)
   	db.session.commit()
   	
   	new_compose = Compose(title = "The first blog", body = 'Hello world!')
   	db.session.add(new_compose)

   	User.generate_fake(50)
   	Compose.generate_fake(count = 500)

   	db.session.commit()
   	db.session.close()


if __name__ == '__main__':
    init_db()
    print 'Initialized the database.'
