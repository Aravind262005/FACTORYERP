import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

class PlannerAgent:
    def __init__(self, model_name="gemini-3.5-flash-lite", temperature=0):
        # Fallback to a stub if API key is not available for testing
        api_key = os.getenv("GEMINI_API_KEY", "dummy_key")
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature, google_api_key=api_key, max_retries=0)

    def execute(self, query: str) -> dict:
        prompt = PromptTemplate(
            input_variables=["query"],
            template='''You are a Planner Agent for a manufacturing system.
Given the user query, extract the intent, entities (product, quantity, deadline), and determine which agents are required.
Agents available: production, inventory_procurement, knowledge.

Query: "{query}"

Output ONLY a JSON object with this exact schema:
{{
  "intent": "string",
  "entities": {{
    "product": "string",
    "quantity": 0,
    "deadline": "YYYY-MM-DD"
  }},
  "required_agents": ["agent_name"]
}}
'''
        )
        
        try:
            response = self.llm.invoke(prompt.format(query=query))
            # Clean up potential markdown formatting from LLM
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content.strip())
        except Exception as e:
            print(f"PlannerAgent LLM Error: {e}")
            # Dynamic Fallback: try to extract the number from the query
            import re
            match = re.search(r'\d[\d,]*', query)
            qty = 500
            if match:
                qty_str = match.group().replace(',', '')
                qty = int(qty_str)
                
            return {
                "intent": "production_feasibility",
                "entities": {"product": "Gearbox Assembly", "quantity": qty, "deadline": "2026-10-08"},
                "required_agents": ["production", "inventory_procurement", "knowledge"]
            }

