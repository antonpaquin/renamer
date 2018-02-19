#! /usr/bin/python3

import sqlite3

conn = sqlite3.connect('files.db')

c = conn.cursor()

c.execute('''
CREATE TABLE files (
    name_hash TEXT UNIQUE NOT NULL,
    hidden INTEGER
)
''')

c.close()
conn.close()
