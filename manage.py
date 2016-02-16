#!/usr/bin/env python
import sys
from app import create_app, db

app = create_app()
if __name__ == '__main__':
    try:
        host = sys.argv[1]
    except IndexError:
        host = ''
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 5000

#     from sqlite_flask_create import init_db
#     init_db()
    app.run(host = host, port = port)
