# provides db access for the app on the g object
import sqlite3

from flask import g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('data.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db():
    db = g.pop('db', None)

    if db:
        db.close()
