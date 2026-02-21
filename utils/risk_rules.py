def stock_risk(current_stock, predicted_demand, shelf_life):
    if current_stock < predicted_demand:
        return "🔴 Stockout Risk"
    elif shelf_life <= 7 and current_stock > predicted_demand * 1.5:
        return "🟠 Wastage Risk"
    elif current_stock > predicted_demand * 1.5:
        return "🟡 Overstock Risk"
    else:
        return "🟢 Healthy"