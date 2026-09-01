import os
import sys
from datetime import datetime, timedelta

# Ensure the backend directory is in the python path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../..')))

from app.db.database import SessionLocal, engine
from app.models.models import (
    Base, Product, Material, BomHeader, BomItem, Machine, ProductionLine,
    WorkOrder, ProductionSchedule, MachineMaintenance, Warehouse, InventoryStock,
    Supplier, SupplierMaterial
)

def seed_data():
    db = SessionLocal()

    # 1. Product
    existing_gearbox = db.query(Product).filter(Product.product_code == "GB-001").first()
    if existing_gearbox:
        print("Seed data already exists.")
        db.close()
        return

    gearbox = Product(product_code="GB-001", standard_cycle_time_min=12.0)
    db.add(gearbox)
    db.commit()
    db.refresh(gearbox)

    # 2. Materials
    aluminum = Material(
        lead_time_days=3,
        safety_stock_level=100,
        reorder_point=150,
        holding_cost_per_unit=2.0,
        ordering_cost=300.0 # EOQ = sqrt(2 * D * S / H). Let's say annual demand D=75, EOQ = sqrt(2*75*300/2) = sqrt(22500) = 150.
    )
    db.add(aluminum)
    db.commit()
    db.refresh(aluminum)

    # 3. BOM
    bom = BomHeader(product_id=gearbox.product_id)
    db.add(bom)
    db.commit()
    db.refresh(bom)

    bom_item = BomItem(bom_id=bom.bom_id, material_id=aluminum.material_id, quantity_required=1.0, scrap_percentage=3.5)
    db.add(bom_item)
    db.commit()

    # 4. Suppliers
    supplier_a = Supplier(name="AlphaCorp", lead_time_days=5, reliability_score=0.9, quality_score=0.95)
    supplier_b = Supplier(name="Supplier B", lead_time_days=2, reliability_score=0.98, quality_score=0.99)
    db.add_all([supplier_a, supplier_b])
    db.commit()
    db.refresh(supplier_a)
    db.refresh(supplier_b)

    db.add(SupplierMaterial(supplier_id=supplier_b.supplier_id, material_id=aluminum.material_id, unit_price=10.0, lead_time_days=2, minimum_order_quantity=50))
    db.add(SupplierMaterial(supplier_id=supplier_a.supplier_id, material_id=aluminum.material_id, unit_price=9.0, lead_time_days=5, minimum_order_quantity=100))
    db.commit()

    # 5. Machines
    line1 = ProductionLine(name="Line 1")
    db.add(line1)
    db.commit()

    m1 = Machine(rated_capacity_per_hour=310.0, status="active", utilization_percentage=82.4)
    m2 = Machine(rated_capacity_per_hour=310.0, status="active", utilization_percentage=82.4)
    m3 = Machine(rated_capacity_per_hour=200.0, status="maintenance", utilization_percentage=0.0)
    db.add_all([m1, m2, m3])
    db.commit()

    # 6. Inventory
    warehouse = Warehouse(name="Main WH", location="Site A")
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)

    # We want ATP to be 480.
    # ATP = quantity_on_hand - quantity_reserved - safety_stock
    # 480 = quantity_on_hand - 20 - 100 => quantity_on_hand = 600
    stock = InventoryStock(
        material_id=aluminum.material_id,
        warehouse_id=warehouse.warehouse_id,
        quantity_on_hand=600,
        quantity_reserved=20,
        safety_stock=100
    )
    db.add(stock)
    db.commit()

    print("Seed data inserted successfully.")
    db.close()

if __name__ == "__main__":
    seed_data()
