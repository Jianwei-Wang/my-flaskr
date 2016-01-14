import sqlite3

conn = sqlite3.connect('flaskr.db')
c = conn.cursor()

def initdb():
    '''Initializes the database with raw sentences.'''

    try:
        c.execute('''create table users(id integer primary key asc,
                                        name varchar(250) not null,
                                        email varchar(250) not null)''')
    except sqlite3.OperationalError:
        pass
    else:
        c.execute('''insert into users(name, email)
                                       values("wangjw", "550466233@qq.com")''')
    try:
        c.execute('''create table composes(id integer primary key asc,
                                           title text not null,
                                           content text not null)''')
    except sqlite3.OperationalError:
        pass
    else:
        c.execute('''insert into composes(title, content)
                                          values("Love", "I love you!")''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initdb()
