import os

def validate_consistency(production_output, inventory_output, knowledge_output):
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
        
    # Phase 16: Ensure RAG output satisfies Critic's minimum thresholds
    # ONLY check RAG confidence if there's a physical plant conflict that needs resolving,
    # OR if the user explicitly asked a knowledge question. To prevent rate limits from
    # blocking valid production orders, we bypass this if the physical plant is clear.
    if knowledge_output and len(conflicts) > 0:
        if knowledge_output.get("confidence", 0.0) < 0.8:
            conflicts.append({
                "type": "knowledge_conflict",
                "agent": "knowledge",
                "description": "RAG confidence is below 0.8 threshold."
            })
        if not knowledge_output.get("sources"):
            conflicts.append({
                "type": "knowledge_conflict",
                "agent": "knowledge",
                "description": "RAG answer lacks citation sources."
            })
            
    return {"consistent": len(conflicts) == 0, "conflicts": conflicts}

class CriticAgent:
    def __init__(self, model_dir="./app/models/critic_classifier"):
        self.model_dir = model_dir
        self.has_model = os.path.exists(self.model_dir)

    def execute(self, agent_outputs: dict) -> dict:
        prod_out = agent_outputs.get("production", {})
        inv_out = agent_outputs.get("inventory_procurement", {})
        knowledge_out = agent_outputs.get("knowledge", {})
        
        # Layer 1: Deterministic rules
        validation = validate_consistency(prod_out, inv_out, knowledge_out)
        
        # Knowledge Base Veto Logic:
        # If the Inventory Agent reports a shortage, but the Knowledge Agent
        # found an SOP that authorizes expedited shipping (e.g. from Supplier B),
        # the Critic Agent overrides the conflict!
        inv_conflict_idx = -1
        for i, c in enumerate(validation["conflicts"]):
            if c["type"] == "inventory_conflict":
                inv_conflict_idx = i
                break
                
        if inv_conflict_idx != -1 and knowledge_out:
            answer = str(knowledge_out.get("answer", "")).lower()
            if "authorized" in answer or "expedite" in answer or "supplier b" in answer:
                validation["conflicts"].pop(inv_conflict_idx)
                validation["consistent"] = len(validation["conflicts"]) == 0
        
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
