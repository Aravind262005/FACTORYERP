import os

def validate_consistency(production_output, inventory_output):
    conflicts = []
    if production_output.get("required_quantity", 0) > production_output.get("capacity_available", 0):
        conflicts.append({
            "type": "capacity_conflict", 
            "agent": "production",
            "description": "Required quantity exceeds capacity available"
        })
    if inventory_output.get("required_material", 0) > inventory_output.get("available_to_promise", 0):
        conflicts.append({
            "type": "inventory_conflict", 
            "agent": "inventory_procurement",
            "description": "Required material exceeds available-to-promise"
        })
    return {"consistent": len(conflicts) == 0, "conflicts": conflicts}

class CriticAgent:
    def __init__(self, model_dir="./app/models/critic_classifier"):
        self.model_dir = model_dir
        self.has_model = os.path.exists(self.model_dir)

    def execute(self, agent_outputs: dict) -> dict:
        prod_out = agent_outputs.get("production", {})
        inv_out = agent_outputs.get("inventory_procurement", {})
        
        # Layer 1: Deterministic rules
        validation = validate_consistency(prod_out, inv_out)
        
        if validation["consistent"]:
            return {
                "consistent": True,
                "conflicts": [],
                "confidence": 1.0,
                "retry_agent": None
            }
        
        # Layer 2: Fine-tuned classifier (fallback to rule-based if missing)
        # If we had the trained LoRA model, we would load and run it here.
        # Since Phase 5 runs later, we fallback to logic.
        
        first_conflict = validation["conflicts"][0]
        return {
            "consistent": False,
            "conflicts": validation["conflicts"],
            "confidence": 0.97, # Mock confidence for now
            "retry_agent": first_conflict["agent"]
        }
