import pandas as pd

def load_data():
    sales = pd.read_csv("data/sales.csv", parse_dates=["date"])
    inventory = pd.read_csv("data/inventory.csv")
    products = pd.read_csv("data/products.csv")
    promotions = pd.read_csv("data/promotions.csv")
    return sales, inventory, products, promotions