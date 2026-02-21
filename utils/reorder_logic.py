def reorder_quantity(predicted_demand, lead_time, current_stock):
    safety_stock = int(0.2 * predicted_demand)
    reorder_qty = (predicted_demand + safety_stock) - current_stock
    return max(reorder_qty, 0)