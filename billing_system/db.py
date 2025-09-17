import sqlite3
con = sqlite3.connect("store.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT
)
""")