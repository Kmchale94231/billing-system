from pathlib import Path
DB_PATH = str((Path(__file__).resolve().parent / "store.db"))

import sqlite3

def connect():
    con = sqlite3.connect("store.db")
    con.execute("PRAGMA foreign_keys = ON")
    return con

con = connect()
cur = con.cursor()

# Customer and product table creation

cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT,            
        name TEXT NOT NULL,
        price_cents INTEGER NOT NULL,
        tax_rate FLOAT NOT NULL
    )   
""")

# Orders table

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN('OPEN', 'PAID', 'VOID')),
        subtotal_cents INTEGER NOT NULL DEFAULT 0,
        tax_cents INTEGER NOT NULL DEFAULT 0,
        total_cents INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS order_item (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        sku TEXT,
        name TEXT,
        unit_price_cents INTEGER NOT NULL,
        qty INTEGER NOT NULL CHECK(qty > 0),
        tax_rate FLOAT NOT NULL,
        line_subtotal_cents INTEGER NOT NULL,
        line_tax_cents INTEGER NOT NULL,
        line_total_cents INTEGER NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    )
""")

# Inserting products in to the database

products = [
    ("Appl001", "Apple", 79, 0.07),
    ("Milk001", "Milk", 450, 0.07),
    ("Baco001", "Bacon", 600, 0.07),
    ("Chee001", "Cheese", 179, 0.07),
    ("Past001", "Pasta", 55, 0.07),
    ("Yogu001", "Yogurt", 132, 0.07)
]

for sku, name, price, tax in products:
    cur.execute(
        """
        INSERT OR IGNORE INTO PRODUCTS (sku, name, price_cents, tax_rate)
        VALUES(?, ?, ?, ?)
        """, (sku, name, price, tax))

con.commit()
con.close()