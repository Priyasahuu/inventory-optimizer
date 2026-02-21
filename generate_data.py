import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

os.makedirs("data", exist_ok=True)

# ---------------- BASIC SETUP ----------------
num_stores = 50
num_products = 100
num_days = 30

stores = [f"S{i}" for i in range(1, num_stores + 1)]
products = [f"P{i}" for i in range(1, num_products + 1)]

categories = {
    "Dairy": 7,
    "Fresh": 5,
    "Grocery": 180,
    "Frozen": 365,
    "Personal Care": 730
}

category_list = list(categories.keys())

start_date = datetime(2024, 1, 1)

# ---------------- PRODUCTS ----------------
product_rows = []
for p in products:
    cat = random.choice(category_list)
    product_rows.append([
        p,
        f"Product_{p}",
        cat,
        categories[cat]
    ])

products_df = pd.DataFrame(
    product_rows,
    columns=["product_id", "product_name", "category", "shelf_life_days"]
)

products_df.to_csv("data/products.csv", index=False)

# ---------------- INVENTORY ----------------
inventory_rows = []
for s in stores:
    for p in products:
        inventory_rows.append([
            s,
            p,
            random.randint(50, 300),
            random.randint(2, 7)
        ])

inventory_df = pd.DataFrame(
    inventory_rows,
    columns=["store_id", "product_id", "current_stock", "lead_time_days"]
)

inventory_df.to_csv("data/inventory.csv", index=False)

# ---------------- SALES ----------------
sales_rows = []
for s in stores:
    for p in products:
        base_demand = random.randint(5, 30)
        price = random.randint(20, 200)

        for d in range(num_days):
            date = start_date + timedelta(days=d)
            is_promo = random.choice([0, 0, 0, 1])  # ~25% promo days

            qty = base_demand + random.randint(-3, 10)
            if is_promo:
                qty = int(qty * random.uniform(1.3, 1.8))
                price = int(price * 0.8)

            sales_rows.append([
                date.strftime("%Y-%m-%d"),
                s,
                p,
                max(qty, 0),
                price,
                is_promo
            ])

sales_df = pd.DataFrame(
    sales_rows,
    columns=["date", "store_id", "product_id", "quantity_sold", "price", "is_promo"]
)

sales_df.to_csv("data/sales.csv", index=False)

# ---------------- PROMOTIONS ----------------
promo_rows = []
for p in products:
    for _ in range(random.randint(1, 3)):
        promo_start = start_date + timedelta(days=random.randint(0, 20))
        promo_end = promo_start + timedelta(days=random.randint(2, 5))

        promo_rows.append([
            p,
            promo_start.strftime("%Y-%m-%d"),
            promo_end.strftime("%Y-%m-%d"),
            random.choice([10, 15, 20, 30])
        ])

promotions_df = pd.DataFrame(
    promo_rows,
    columns=["product_id", "promo_start", "promo_end", "discount_percent"]
)

promotions_df.to_csv("data/promotions.csv", index=False)

print("✅ LARGE DATASETS GENERATED SUCCESSFULLY")