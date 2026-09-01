import math

def calculate_atp(quantity_on_hand, quantity_reserved, safety_stock):
    """Available-to-Promise. This is THE only definition used anywhere 
    in this system for inventory availability — never call it 
    'available_stock' or 'available' alone anywhere in code or API 
    responses; always use 'atp' or 'available_to_promise'."""
    return quantity_on_hand - quantity_reserved - safety_stock

def calculate_required_material(production_quantity, bom_quantity_required):
    return production_quantity * bom_quantity_required

def calculate_eoq(annual_demand, ordering_cost, holding_cost_per_unit):
    return math.sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit)

def calculate_estimated_wastage(production_quantity, scrap_percentage):
    return production_quantity * (scrap_percentage / 100)
