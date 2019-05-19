# provides db access for the app on the g object
import sqlite3

from flask import g

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('data.db')
        g.db.row_factory = dict_factory
    return g.db

def close_db():
    db = g.pop('db', None)

    if db:
        db.close()
