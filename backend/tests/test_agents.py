import sys
import os

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.planner.agent import PlannerAgent
from app.agents.production.agent import ProductionAgent
from app.agents.inventory_procurement.agent import InventoryProcurementAgent
from app.agents.knowledge.agent import KnowledgeAgent
from app.agents.critic.agent import CriticAgent

def test_planner():
    agent = PlannerAgent()
    out = agent.execute("Can we complete 500 gearbox assemblies by Friday?")
    assert out["intent"] == "production_feasibility"
    assert out["entities"]["quantity"] == 500
    assert "production" in out["required_agents"]
    print("Planner OK")

def test_production():
    agent = ProductionAgent()
    out = agent.execute({"product": "Gearbox Assembly", "quantity": 500})
    assert out["status"] == "success"
    assert out["capacity_available"] == 620.0
    assert out["required_quantity"] == 500
    assert out["can_meet_schedule"] is True
    print("Production OK")

def test_inventory():
    agent = InventoryProcurementAgent()
    out = agent.execute({"product": "Gearbox Assembly", "quantity": 500})
    assert out["status"] == "success"
    assert out["available_to_promise"] == 480
    assert out["shortage_quantity"] == 20
    assert out["reorder_required"] is True
    assert out["eoq_recommendation"] == 150
    print("Inventory OK")

def test_knowledge():
    agent = KnowledgeAgent()
    out = agent.execute("Expedited shipping for Aluminum Alloy")
    assert out["status"] == "success"
    assert "SOP-14" in out["answer"]
    print("Knowledge OK")

def test_critic():
    agent = CriticAgent()
    # Mocking outputs that have a conflict
    prod_out = {"capacity_available": 620, "required_quantity": 500}
    inv_out = {"available_to_promise": 480, "required_material": 500}
    
    out = agent.execute({"production": prod_out, "inventory_procurement": inv_out})
    assert out["consistent"] is False
    assert out["retry_agent"] == "inventory_procurement"
    print("Critic OK")

if __name__ == "__main__":
    test_planner()
    test_production()
    test_inventory()
    test_knowledge()
    test_critic()
    print("All agent tests passed!")
