from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List
import os

class SubQueries(BaseModel):
    queries: List[str] = Field(description="A list of distinct search queries. If the original query is simple, this list should contain just one query.")

class QueryDecomposer:
    def __init__(self, llm=None):
        """
        Initializes the query decomposer.
        If no LLM is provided, it attempts to initialize ChatGoogleGenerativeAI.
        """
        self.llm = llm
        
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if self.llm is None and api_key:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-3.5-flash-lite",
                    temperature=0.0,
                    api_key=api_key,
                    max_retries=0
                )
                self.llm = self.llm.with_structured_output(SubQueries)
            except Exception:
                self.llm = None
        elif self.llm is not None:
             if hasattr(self.llm, "with_structured_output"):
                 self.llm = self.llm.with_structured_output(SubQueries)

        self.prompt = PromptTemplate.from_template(
            """You are a manufacturing retrieval assistant.
Your task is to analyze a user's query and determine if it requires multiple distinct searches (multi-hop or comparative).

Examples:
- "Compare the maintenance schedule of M04 and M05" -> ["maintenance schedule for M04", "maintenance schedule for M05"]
- "What is the max temperature of M04?" -> ["max temperature of M04"]
- "What materials are needed for Product X and Product Y?" -> ["materials needed for Product X", "materials needed for Product Y"]

Output a list of simple, direct search queries. If the query is simple, just return the original query in a list of size 1.

Raw Query: {raw_query}
"""
        )

    def decompose(self, query: str) -> List[str]:
        if self.llm is None:
            # Fallback pass-through
            return [query]
            
        try:
            prompt_text = self.prompt.format(raw_query=query)
            result = self.llm.invoke(prompt_text)
            
            if hasattr(result, "queries"):
                return result.queries
            elif isinstance(result, dict) and "queries" in result:
                return result["queries"]
            else:
                return [query]
        except Exception:
            # Safe fallback on failure
            return [query]

