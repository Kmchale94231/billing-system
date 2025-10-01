import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import get_or_create_customer, start_checkout, add_item, remove_item, calculate_total

# 1) Customer
cust_id  = get_or_create_customer("Jane Doe", "555-0101")

# 2) Start an order
order_id = start_checkout(cust_id)

# 3) Add items by SKU (must match db.py seed SKUs exactly)
add_item(order_id, "Appl001", 3)
add_item(order_id, "Milk001", 1)

# 4) Try removing 1 apple
remove_item(order_id, "Appl001", 1)

# 5) Print totals
calculate_total(order_id)
