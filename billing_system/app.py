from pathlib import Path
DB_PATH = str((Path(__file__).resolve().parent / "store.db"))

import sqlite3
from datetime import datetime

def connect():
    con = sqlite3.connect("store.db")
    con.execute("PRAGMA foreign_keys = ON")
    return con

# Retrieve or create a customer file 
def get_or_create_customer(name, phone):
    with connect() as con:
        cur = con.cursor()

        name = (name or "").strip()

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
            (customer_id, "OPEN", 0, 0, 0))
        con.commit()
        return cur.lastrowid

def add_item(order_id, sku, qty): 
    with connect() as con:
        cur = con.cursor()

        if qty <= 0:
            raise ValueError("Quantity must be > 1")
        
        cur.execute(
            "SELECT id, name, price_cents, tax_rate FROM products WHERE sku = ?",
            (sku,)
        )
        product = cur.fetchone()

        if product is None:
            raise ValueError("Unknown SKU")
        product_id, name, price_cents, tax_rate = product

        cur.execute(
            "SELECT id, qty FROM order_item WHERE order_id = ? AND product_id = ?",
            (order_id, product_id) 
        )
        item = cur.fetchone()

        if item:
            item_id, old_qty = item
            new_qty = old_qty + qty
            new_sub = new_qty * price_cents
            new_tax = round(new_sub * tax_rate)
            new_total = new_sub + new_tax

            cur.execute(
                """
                UPDATE order_item 
                SET qty=?,
                    line_subtotal_cents =?, 
                    line_tax_cents      =?, 
                    line_total_cents    =?
                WHERE id=?
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
                    price_cents,
                    qty,
                    tax_rate,
                    sub,
                    tax,
                    total
                )
            )
            con.commit()
    _recalc_totals(order_id)
        
def remove_item(order_id, sku, qty):
    with connect() as con:
        cur = con.cursor()

        if qty <= 0:
            raise ValueError("Quantity must be > 0")
            
        cur.execute(
            """
            SELECT id, qty, unit_price_cents, tax_rate
            FROM order_item
            WHERE order_id = ? AND sku = ?
            """,
            (order_id, sku)
        )
        row = cur.fetchone()

        if row is None:
            return
        item_id, old_qty, unit_price_cents, tax_rate = row
        new_qty = old_qty - qty 

        if new_qty > 0:
            new_sub = new_qty * unit_price_cents
            new_tax = round(new_sub * tax_rate)
            new_total = new_sub + new_tax

            cur.execute(
                """
                UPDATE order_item
                SET qty = ?,
                    line_subtotal_cents = ?,
                    line_tax_cents      = ?,
                    line_total_cents    = ?
                WHERE id = ?
                """,
                (new_qty, new_sub, new_tax, new_total, item_id)
            )
        else:
            cur.execute("DELETE FROM order_item WHERE id = ?", (item_id,))

        con.commit()

    _recalc_totals(order_id)

def _recalc_totals(order_id,):
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
        (order_id,)
    )
    subtotal_cents, tax_cents, total_cents = cur.fetchone()

    cur.execute(
        """
        UPDATE orders
        SET subtotal_cents = ?,
            tax_cents      = ?,
            total_cents    = ?
        WHERE id           = ?
        """,
        (subtotal_cents, tax_cents, total_cents, order_id)
        )
    con.commit()

def _format_cents(cents: int) -> str:
    dollars = cents // 100 
    remainder = cents % 100
    return f"${dollars}.{remainder:02d}"

def calculate_total(order_id: int) -> None:
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            SELECT subtotal_cents, tax_cents, total_cents
            FROM orders
            WHERE id = ?
            """,
            (order_id,)
        )

        row = cur.fetchone()

        if row is None:
            raise ValueError(f"Order {order_id} not found")
        
        subtotal_cents, tax_cents, total_cents = row

        print("\n" + "=" * 32)
        print(f"{'Subtotal:':<16}{_format_cents(subtotal_cents):>16}")
        print(f"{'Tax:':<16}{_format_cents(tax_cents):>16}")
        print(f"-" * 32)
        print(f"{'TOTAL:':<16}{_format_cents(total_cents):>16}")
        print("\n" + "=" * 32)




