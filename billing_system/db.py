import sqlite3
con = sqlite3.connect("store.db")
cur = con.cursor()

#Customer and product table creation

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

# Creating the orders database

con = sqlite3.connect("store.db")
cur = con.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        status TEXT NOT NULL CHECK(status IN('OPEN', 'PAID', 'VOID')),
        subtotal_cents INTEGER NOT NULL DEFAULT 0,
        tax_cents INTEGER NOT NULL DEFAULT 0,
        total_cents INTEGER NOT NULL DEFAULT 0
    )
""")

con = sqlite3.connect("store.db")
cur = con.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS order_item (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        sku TEXT,
        name TEXT,
        unit_price_cents INTEGER NOT NULL,
        qty INTEGER NOT NULL CHECK(qty > 0),
        tax_rate FLOAT NOT NULL,
        line_subtotal_cents INTEGER NOT NULL,
        line_tax_cents INTEGER NOT NULL,
        line_total_cents INTEGER NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id)
    )
""")
con.commit()
con.close()

# Inserting products in to the database

cur.execute("""
INSERT INTO products (sku, name, price_cents, tax_rate)
VALUES (?, ?, ?, ?)
""", ("Appl001", "Apple", 79, 0.07))
con.commit()

cur.execute("""
INSERT INTO products (sku, name, price_cents, tax_rate)
VALUES (?, ?, ?, ?)
""", ("Milk001", "Milk", 450, 0.07))
con.commit()

cur.execute("""
INSERT INTO products (sku, name, price_cents, tax_rate)
VALUES (?, ?, ?, ?)
""", ("BACO001", "Bacon", 600, 0.07))
con.commit()

cur.execute("""
INSERT INTO products (sku, name, price_cents, tax_rate)
VALUES (?, ?, ?, ?)
""", ("Chee001", "Cheese", 179, 0.07))
con.commit()

cur.execute("""
INSERT INTO products (sku, name, price_cents, tax_rate)
VALUES (?, ?, ?, ?)
""", ("Past001", "Pasta", 55, 0.07))
con.commit()

cur.execute("""
INSERT INTO products (sku, name, price_cents, tax_rate)
VALUES (?, ?, ?, ?)
""", ("Yogu001", "Yogurt", 132, 0.07))
con.commit()
con.close()