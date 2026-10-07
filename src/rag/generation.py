from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os

class AnswerCitation(BaseModel):
    document_id: str = Field(description="The source document ID cited.")
    page: str = Field(description="The page number or section cited.")

class GroundedAnswer(BaseModel):
    answer: str = Field(description="The final answer to the user's query, including inline citations like (SOP-14, Page 2). If evidence is insufficient, this MUST be exactly 'INSUFFICIENT_EVIDENCE'.")
    confidence: float = Field(description="A confidence score between 0.0 and 1.0. If INSUFFICIENT_EVIDENCE, this should be 0.0.")
    citations: List[AnswerCitation] = Field(description="A list of specific documents and pages used to generate the answer.")

class AnswerGenerator:
    def __init__(self, llm=None):
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
                self.llm = self.llm.with_structured_output(GroundedAnswer)
            except Exception:
                self.llm = None
        elif self.llm is not None:
             if hasattr(self.llm, "with_structured_output"):
                 self.llm = self.llm.with_structured_output(GroundedAnswer)

        self.prompt = PromptTemplate.from_template(
            """You are a strict, policy-aware Manufacturing Knowledge Agent.
Your task is to answer the user's query using ONLY the provided evidence.

CRITICAL RULES:
1. You must NOT invent or hallucinate manufacturing policies, machine specs, or schedules.
2. General knowledge must NEVER override the provided authoritative evidence.
3. If the provided evidence does not contain enough information to fully and confidently answer the query, your answer MUST be exactly: INSUFFICIENT_EVIDENCE.
4. If you can answer the query, you MUST include inline citations in your answer using the format (DocID, Page X), matching the Source tags in the evidence.

EVIDENCE BLOCK:
{evidence}

USER QUERY: {query}
"""
        )

    def generate(self, query: str, evidence: str) -> Dict[str, Any]:
        """
        Generates a grounded answer from the evidence.
        Returns a dictionary matching the expected KnowledgeAgent interface.
        """
        if self.llm is None:
            # Fallback if no LLM configured
            return {
                "answer": "SYSTEM ERROR: LLM not configured.",
                "confidence": 0.0,
                "sources": []
            }
            
        if evidence == "NO EVIDENCE FOUND." or not evidence.strip():
            return {
                "answer": "INSUFFICIENT_EVIDENCE",
                "confidence": 0.0,
                "sources": []
            }
            
        try:
            prompt_text = self.prompt.format(query=query, evidence=evidence)
            result = self.llm.invoke(prompt_text)
            
            # Extract structured response
            if hasattr(result, "answer"):
                return {
                    "answer": result.answer,
                    "confidence": result.confidence,
                    "sources": [{"document_id": c.document_id, "page": c.page} for c in result.citations]
                }
            elif isinstance(result, dict) and "answer" in result:
                return {
                    "answer": result["answer"],
                    "confidence": result.get("confidence", 1.0),
                    "sources": result.get("citations", [])
                }
            else:
                return {
                    "answer": "INSUFFICIENT_EVIDENCE",
                    "confidence": 0.0,
                    "sources": []
                }
        except Exception as e:
            return {
                "answer": f"SYSTEM ERROR during generation: {str(e)}",
                "confidence": 0.0,
                "sources": []
            }

