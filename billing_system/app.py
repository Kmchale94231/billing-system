import sqlite3
from datetime import datetime

def connect():
    con = sqlite3.connect("store.db")
    con.execute("PRAGMA foreign_keys = ON")
    cur = con.cursor()
    return con

# Retrieve or create a customer file 

def get_or_create_customer(name, phone):
    with connect() as con:
        cur = con.cursor()

        name = name.strip()

        if not name:
            raise ValueError("Name is required")

        if phone is not None:
            phone = phone.strip()
            
            if phone == "":
                phone = None

        if phone is not None:
            cur.execute("SELECT id FROM customers WHERE name = ? and phone = ?", (name, phone))
        else:
            cur.execute("SELECT id FROM customers WHERE name = ? AND phone IS NULL", (name,))
        row = cur.fetchone()

        if row:
            return row[0]
    
        cur.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
        con.commit()
        return cur.lastrowid

def start_checkout(customer_id):
    with connect() as con:
        cur = con.cursor()

        cur.execute("""
            INSERT INTO orders (
            customer_id, 
            status, 
            subtotal_cents, 
            tax_cents, 
            total_cents
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (customer_id, "OPEN", 0, 0, 0),
        )

def add_item(order_id, sku, qty): 
    with connect() as con:
        cur = con.cursor()

        if qty <= 0:
            raise ValueError("Quantity must be more than 1")
        
        cur.execute(
            "SELECT id, name, price_cents, tax_rate FROM PRODUCTS WHERE sku = ?",
            (sku,)
        )
        product = cur.fetchone()

        if product is None:
            raise ValueError("Unknown SKU")
        product_id, price_cents, tax_rate = row

        cur.execute(
            "SELECT id, qty FROM order_item WHERE order_id = ? AND product_id = ?",
            (order_id, product_id) 
        )
        item = cur.fetchone()

        if item:
            item_id, old_qty = item
            new_qty = old_qty + item
            new_sub = new_qty * price_cents
            new_tax = round(new_sub * tax_rate)
            new_total = new_sub + new_tax

            cur.execute(
                """
                UPDATE order_item 
                SET qty=?,
                    line_subtotal_cents =?, 
                    line_tax_cents      =?, 
                    line_total_cents    =?,
                "WHERE id=?"
                """,
                (new_qty, new_sub, new_tax, new_total, item_id)
            )
        else:

            sub = qty * price_cents
            tax = round(sub * tax_rate)
            total = sub + tax

            cur.execute(
                """
                INSERT INTO order_item (
                    order_id,
                    product_id,
                    sku,
                    name,
                    unit_price_cents,
                    qty,
                    tax_rate,
                    line_subtotal_cents,
                    line_tax_cents,
                    line_total_cents
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    product_id,
                    sku,
                    name,
                    unit_price_cents,
                    qty,
                    tax_rate,
                    line_subtotal_cents,
                    line_tax_cents,
                    line_total_cents
                )
            )

def remove_item(order_id, sku, qty):
    with connect() as con:
        cur = con.cursor()

        if qty <= 0:
            raise ValueError("Quantity must be > 0")
            
        cur.execute(
            """
            SELECT id, qty, unit_price_cents, tax_rate,
            FROM order_item,
            WHERE order_id = ? AND sku = ?
            """,
            (order_id, sku)
        )

        row.fetchone()

        if row is None():
            return
        item_id, old_qty, unit_price_cents, tax_rate = row
        new_qty = old_qty - qty 

        if new_qty > 0:
            new_sub = new_qty * unit_price_cents
            

            cur.execute(
                """
                UPDATE order_item
                SET qty             = ?,
                line_subtotal_cents = ?,
                line_tax_cents      = ?,
                line_total_cents    = ?,
                WHERE id            = ?
                """,
                "UPDATE SET qty = ?, line_subtotal_cents=?, line_tax_cents=?, line_total_cents=?, WHERE id=?"
                (new_qty, new_sub, new_tax, new_total, item_id)
            )
        else:
            cur.execute(
                "DELETE FROM order_item WHERE id = ?", 
                (item_id,)
            )

def _recalc_totals(order_id):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
        """
        SELECT
            COALESCE(SUM(line_subtotal_cents), 0),
            COALESCE(SUM(line_tax_cents), 0),
            COALESCE(SUM(line_total_cents), 0)
            FROM order_item
            WHERE order_id = ?
        """,
        (order_id)
    )
    line_subtotal_cents, line_tax_cents, line_total_cents = cur.fetchone()

    cur.execute(
        """
        UPDATE orders
        SET subtotal_cents = ?,
            tax_cents      = ?,
            total_cents    = ?
        WHERE id = ?
        """,
        (subtotal_cents, tax_cents, total_cents, order_id)
        )





def calculate_total():
    """
    Calculate and update the subtotal, tax, and total value for a single order
    """

    with connect() as con:
        cur = con.cursor()

        "SELECT FROM "


        

