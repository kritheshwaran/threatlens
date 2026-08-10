import sqlite3

DATABASE_URL = 'backend/dev.db'

def get_connection():
    return sqlite3.connect(DATABASE_URL)
