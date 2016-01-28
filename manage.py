#!/usr/bin/env python
from app import create_app, db

app = create_app()
if __name__ == '__main__':
    app.run(host="192.168.1.106")
