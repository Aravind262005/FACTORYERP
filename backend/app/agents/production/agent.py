from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.models import Product, Machine, BomHeader, BomItem
from app.tools.calculations import calculate_estimated_wastage

class ProductionAgent:
    def __init__(self):
        pass

    def execute(self, entities: dict) -> dict:
        product_name = entities.get("product")
        required_quantity = entities.get("quantity", 0)
        
        db: Session = SessionLocal()
        try:
            # For simplicity in this demo, we'll fetch all active machines 
            # and sum their rated capacities (as a proxy for capacity available)
            # In a real app we'd consider schedules, work orders, maintenance.
            machines = db.query(Machine).filter(Machine.status == "active").all()
            capacity_available = sum(m.rated_capacity_per_hour for m in machines)
            
            # Fetch the BOM item for the product to get scrap percentage
            # Assuming product name matches "Gearbox Assembly" mapping to "GB-001"
            # In real system, proper product name matching is needed.
            product = db.query(Product).first() # Fallback to first product
            scrap_percentage = 0.0
            if product:
                bom_header = db.query(BomHeader).filter(BomHeader.product_id == product.product_id).first()
                if bom_header:
                    bom_item = db.query(BomItem).filter(BomItem.bom_id == bom_header.bom_id).first()
                    if bom_item:
                        scrap_percentage = bom_item.scrap_percentage

            estimated_wastage = calculate_estimated_wastage(required_quantity, scrap_percentage)
            
            utilization_pct = 0.0
            if machines:
                utilization_pct = sum(m.utilization_percentage for m in machines) / len(machines)
            
            can_meet = capacity_available >= required_quantity
            
            return {
                "status": "success",
                "capacity_available": float(capacity_available),
                "required_quantity": required_quantity,
                "utilization_pct": round(utilization_pct, 1),
                "estimated_wastage_pct": scrap_percentage,
                "can_meet_schedule": can_meet,
                "bottlenecks": [] if can_meet else ["Insufficient capacity"],
                "evidence": [f"{int(capacity_available)} units capacity available across {len(machines)} active machines"]
            }
        except Exception as e:
            return {
                "status": "error",
                "capacity_available": 0,
                "required_quantity": required_quantity,
                "utilization_pct": 0,
                "estimated_wastage_pct": 0,
                "can_meet_schedule": False,
                "bottlenecks": [str(e)],
                "evidence": []
            }
        finally:
            db.close()
