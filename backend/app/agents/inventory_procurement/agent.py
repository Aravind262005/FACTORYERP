from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.models import Material, InventoryStock, SupplierMaterial, BomHeader, BomItem, Product
from app.tools.calculations import calculate_atp, calculate_required_material, calculate_eoq
from datetime import datetime, timedelta

class InventoryProcurementAgent:
    def __init__(self):
        pass

    def execute(self, entities: dict) -> dict:
        product_name = entities.get("product")
        production_quantity = entities.get("quantity", 0)
        
        db: Session = SessionLocal()
        try:
            # Get the BOM and Materials
            product = db.query(Product).first() # Simplify: get first product
            if not product:
                raise ValueError("Product not found")
                
            bom_header = db.query(BomHeader).filter(BomHeader.product_id == product.product_id).first()
            bom_item = db.query(BomItem).filter(BomItem.bom_id == bom_header.bom_id).first()
            material = db.query(Material).filter(Material.material_id == bom_item.material_id).first()
            
            # Required material
            required_material = calculate_required_material(production_quantity, bom_item.quantity_required)
            
            # ATP
            stock = db.query(InventoryStock).filter(InventoryStock.material_id == material.material_id).first()
            atp = calculate_atp(stock.quantity_on_hand, stock.quantity_reserved, stock.safety_stock)
            
            shortage_quantity = 0
            if required_material > atp:
                shortage_quantity = required_material - atp
            
            reorder_required = shortage_quantity > 0
            
            eoq_recommendation = 0
            supplier_eta = None
            if reorder_required:
                # We need an annual demand proxy. Assuming 75 per year.
                eoq_recommendation = calculate_eoq(75, material.ordering_cost, material.holding_cost_per_unit)
                
                # Best supplier
                supplier_mat = db.query(SupplierMaterial).filter(SupplierMaterial.material_id == material.material_id).order_by(SupplierMaterial.lead_time_days).first()
                if supplier_mat:
                    eta_date = datetime.utcnow() + timedelta(days=supplier_mat.lead_time_days)
                    supplier_eta = eta_date.strftime("%Y-%m-%d")
            
            return {
                "status": "success",
                "material_available": not reorder_required,
                "required_material": required_material,
                "available_to_promise": atp,
                "shortage_quantity": shortage_quantity,
                "reorder_required": reorder_required,
                "eoq_recommendation": round(eoq_recommendation),
                "supplier_eta": supplier_eta,
                "evidence": [f"Stock ATP is {atp}"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "material_available": False,
                "required_material": 0,
                "available_to_promise": 0,
                "shortage_quantity": 0,
                "reorder_required": False,
                "eoq_recommendation": 0,
                "supplier_eta": None,
                "evidence": [str(e)]
            }
        finally:
            db.close()
