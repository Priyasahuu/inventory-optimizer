import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from models.demand_forecast import forecast_demand
from utils.risk_rules import stock_risk
from utils.reorder_logic import reorder_quantity

st.set_page_config(page_title="Inventory Intelligence Dashboard", layout="wide")

st.title("📊 Smart Inventory Optimization Dashboard")

# ---------------- LOAD DATA ----------------
sales, inventory, products, promotions = load_data()

# ---------------- STORE SELECT ----------------
store = st.selectbox("🏬 Select Store", sorted(sales["store_id"].unique()))

store_sales = sales[sales["store_id"] == store]
store_inventory = inventory[inventory["store_id"] == store]

# ---------------- PRODUCT SELECT ----------------
available_products = store_sales["product_id"].unique()

product = st.selectbox("🛒 Select Product", sorted(available_products))

product_sales = store_sales[store_sales["product_id"] == product]

prod_info = products[products["product_id"] == product].iloc[0]
inv_info = store_inventory[store_inventory["product_id"] == product].iloc[0]

# ---------------- STORE KPIs ----------------
total_sales = store_sales["quantity_sold"].sum()
avg_daily = store_sales.groupby("date")["quantity_sold"].sum().mean()
total_products = store_sales["product_id"].nunique()
stock_total = store_inventory["current_stock"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Units Sold", int(total_sales))
c2.metric("Avg Daily Sales", int(avg_daily))
c3.metric("Products Sold", total_products)
c4.metric("Current Stock", int(stock_total))

st.divider()

# ---------------- STORE SALES TREND ----------------
st.subheader("📈 Store Sales Trend")

daily = store_sales.groupby("date")["quantity_sold"].sum().reset_index()

fig_trend = px.line(daily, x="date", y="quantity_sold", markers=True)
st.plotly_chart(fig_trend, use_container_width=True)

# ---------------- PRODUCT INVENTORY TABLE ----------------
st.subheader("📋 Product Stock & Restock Analysis")

table_list = []

for _, row in store_inventory.iterrows():

    prod_id = row["product_id"]
    prod_sales = store_sales[store_sales["product_id"] == prod_id]

    if prod_sales.empty:
        continue

    predicted = forecast_demand(prod_sales, 7)
    shelf = products[products["product_id"] == prod_id]["shelf_life_days"].values[0]
    risk = stock_risk(row["current_stock"], predicted, shelf)
    reorder = reorder_quantity(predicted, row["lead_time_days"], row["current_stock"])

    table_list.append([
        prod_id,
        row["current_stock"],
        predicted,
        reorder,
        risk
    ])

table_df = pd.DataFrame(
    table_list,
    columns=["Product","Current Stock","Predicted Demand","Reorder Qty","Risk"]
)

def highlight(val):
    if "Stockout" in val:
        return "background-color:red;color:white"
    elif "Wastage" in val:
        return "background-color:orange"
    elif "Overstock" in val:
        return "background-color:gold"
    else:
        return "background-color:green;color:white"

styled = table_df.style.applymap(highlight, subset=["Risk"])

st.dataframe(styled, use_container_width=True)

# ---------------- TOP PRODUCTS ----------------
st.subheader("🏆 Top Performing Products")

top_products = (
    store_sales.groupby("product_id")["quantity_sold"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_top = px.bar(top_products, x="quantity_sold", y="product_id", orientation="h")
st.plotly_chart(fig_top, use_container_width=True)

# ---------------- CATEGORY PERFORMANCE ----------------
st.subheader("📦 Category Performance")

store_sales = store_sales.merge(products, on="product_id", how="left")

cat_perf = store_sales.groupby("category")["quantity_sold"].sum().reset_index()

fig_cat = px.pie(cat_perf, names="category", values="quantity_sold")
st.plotly_chart(fig_cat, use_container_width=True)

# ---------------- RISK DISTRIBUTION ----------------
st.subheader("⚠️ Inventory Risk Distribution")

risk_list = []

for _, row in store_inventory.iterrows():
    prod_id = row["product_id"]
    prod_sales = store_sales[store_sales["product_id"] == prod_id]

    if prod_sales.empty:
        continue

    predicted = forecast_demand(prod_sales, 7)
    shelf = products[products["product_id"] == prod_id]["shelf_life_days"].values[0]
    risk = stock_risk(row["current_stock"], predicted, shelf)

    risk_list.append([prod_id, risk])

risk_df = pd.DataFrame(risk_list, columns=["Product", "Risk"])

fig_risk = px.histogram(
    risk_df,
    x="Risk",
    color="Risk",
    hover_data=["Product"]
)

st.plotly_chart(fig_risk, use_container_width=True)

# ---------------- SCATTER ----------------
st.subheader("📊 Inventory Positioning")

scatter_list = []

for _, row in store_inventory.iterrows():
    prod_id = row["product_id"]
    prod_sales = store_sales[store_sales["product_id"] == prod_id]

    if prod_sales.empty:
        continue

    predicted = forecast_demand(prod_sales, 7)
    scatter_list.append([prod_id, row["current_stock"], predicted])

scatter_df = pd.DataFrame(scatter_list, columns=["Product", "Stock", "Predicted"])

fig_scatter = px.scatter(scatter_df, x="Stock", y="Predicted", hover_data=["Product"])
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ======================================================
# PRODUCT LEVEL ANALYTICS
# ======================================================

st.header("🔎 Selected Product Intelligence")

predicted = forecast_demand(product_sales, 7)

risk = stock_risk(
    inv_info["current_stock"],
    predicted,
    prod_info["shelf_life_days"]
)

reorder = reorder_quantity(
    predicted,
    inv_info["lead_time_days"],
    inv_info["current_stock"]
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Product", product)
c2.metric("Current Stock", inv_info["current_stock"])
c3.metric("Predicted Demand", predicted)
c4.metric("Risk Status", risk)

# ---------------- PRODUCT TREND ----------------
st.subheader("📈 Product Demand Trend")

fig_prod = px.line(
    product_sales,
    x="date",
    y="quantity_sold",
    markers=True,
    title=f"Demand Trend for {product}"
)
st.plotly_chart(fig_prod, use_container_width=True)

# ---------------- STOCK VS FORECAST ----------------
st.subheader("📊 Stock vs Forecast")

compare_df = pd.DataFrame({
    "Type": ["Current Stock", "Predicted Demand"],
    "Value": [inv_info["current_stock"], predicted]
})

fig_compare = px.bar(compare_df, x="Type", y="Value")
st.plotly_chart(fig_compare, use_container_width=True)

# ---------------- REORDER ----------------
st.subheader("🛒 Recommendation")

if reorder > 0:
    st.error(f"Reorder {reorder} units immediately")
else:
    st.success("Stock level is sufficient")