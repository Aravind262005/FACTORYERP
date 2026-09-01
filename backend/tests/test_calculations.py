import sys
import os
import math

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.tools.calculations import (
    calculate_atp,
    calculate_required_material,
    calculate_eoq,
    calculate_estimated_wastage
)

def test_calculate_atp():
    # From example: quantity_on_hand=600, reserved=20, safety=100 -> ATP=480
    atp = calculate_atp(quantity_on_hand=600, quantity_reserved=20, safety_stock=100)
    assert atp == 480, f"Expected 480, got {atp}"

def test_calculate_required_material():
    # From example: required 500
    req = calculate_required_material(production_quantity=500, bom_quantity_required=1.0)
    assert req == 500, f"Expected 500, got {req}"

def test_calculate_eoq():
    # EOQ reorder 150 units
    # Example annual_demand=75, ordering=300, holding=2 => 150
    eoq = calculate_eoq(annual_demand=75, ordering_cost=300, holding_cost_per_unit=2)
    assert math.isclose(eoq, 150.0), f"Expected 150, got {eoq}"

def test_calculate_estimated_wastage():
    # Capacity 620, let's say 3.5% scrap
    wastage = calculate_estimated_wastage(production_quantity=620, scrap_percentage=3.5)
    assert math.isclose(wastage, 21.7), f"Expected 21.7, got {wastage}"

if __name__ == "__main__":
    test_calculate_atp()
    test_calculate_required_material()
    test_calculate_eoq()
    test_calculate_estimated_wastage()
    print("All tests passed!")
