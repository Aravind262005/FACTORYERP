from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import os
import json

class RewrittenQuery(BaseModel):
    query: str = Field(description="The optimized search query for vector retrieval")

class QueryRewriter:
    def __init__(self, llm=None):
        """
        Initializes the query rewriter.
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
                self.llm = self.llm.with_structured_output(RewrittenQuery)
            except Exception:
                self.llm = None
        elif self.llm is not None:
             # Assume if user provided LLM, it's already configured or mock
             # For structured output if it's a raw ChatGoogleGenerativeAI:
             if hasattr(self.llm, "with_structured_output"):
                 self.llm = self.llm.with_structured_output(RewrittenQuery)

        self.prompt = PromptTemplate.from_template(
            """You are a manufacturing retrieval assistant.
Your task is to rewrite the user's raw query into an optimized search query for a vector database.

Instructions:
1. Fix any spelling mistakes.
2. Expand acronyms if they are standard manufacturing terms (e.g. 'PM' -> 'Preventive Maintenance').
3. Remove conversational filler (e.g. 'Hi, can you tell me...').
4. Preserve specific identifiers exactly (e.g. M04, SOP-14).
5. Only output the optimized query string.

Raw Query: {raw_query}
"""
        )

    def rewrite(self, query: str) -> str:
        if self.llm is None:
            # Fallback pass-through if no LLM/API key is configured
            return query
            
        try:
            prompt_text = self.prompt.format(raw_query=query)
            result = self.llm.invoke(prompt_text)
            
            # Depending on how structured output returns it (BaseModel or dict)
            if hasattr(result, "query"):
                return result.query
            elif isinstance(result, dict) and "query" in result:
                return result["query"]
            else:
                # Fallback if structure parsing fails
                return str(result)
        except Exception as e:
            # Safe fallback on failure
            return query

