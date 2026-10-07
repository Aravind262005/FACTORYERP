import pytest
from src.rag.generation import AnswerGenerator

class MockLLM:
    def with_structured_output(self, schema):
        return self
        
    def invoke(self, text):
        class MockResult:
            def __init__(self, answer, conf, citations):
                self.answer = answer
                self.confidence = conf
                self.citations = citations
                
        if "INSUFFICIENT_EVIDENCE" in text and "NO EVIDENCE" in text:
            # We intercept NO EVIDENCE in the generator before it hits LLM usually,
            # but if it hits here, simulate failure
            return MockResult("INSUFFICIENT_EVIDENCE", 0.0, [])
            
        if "USER QUERY: What is the maintenance schedule for M04?" in text:
            class Citation:
                def __init__(self):
                    self.document_id = "SOP-14"
                    self.page = "2"
            return MockResult("Machine M04 requires daily maintenance (SOP-14, Page 2).", 0.95, [Citation()])
            
        return MockResult("INSUFFICIENT_EVIDENCE", 0.0, [])

def test_generation_success():
    generator = AnswerGenerator(llm=MockLLM())
    
    query = "What is the maintenance schedule for M04?"
    evidence = "--- EVIDENCE ITEM 1 ---\n[Source: SOP-14 | Type: SOP | Authority: current | Page: 2]\nMachine M04 requires daily maintenance."
    
    result = generator.generate(query, evidence)
    
    assert "daily maintenance" in result["answer"]
    assert "(SOP-14, Page 2)" in result["answer"]
    assert result["confidence"] == 0.95
    assert len(result["sources"]) == 1
    assert result["sources"][0]["document_id"] == "SOP-14"

def test_generation_insufficient():
    generator = AnswerGenerator(llm=MockLLM())
    
    query = "What is the maintenance schedule for M05?"
    evidence = "--- EVIDENCE ITEM 1 ---\n[Source: SOP-14 | Type: SOP | Authority: current | Page: 2]\nMachine M04 requires daily maintenance."
    
    result = generator.generate(query, evidence)
    
    assert result["answer"] == "INSUFFICIENT_EVIDENCE"
    assert result["confidence"] == 0.0
    
def test_generation_no_evidence():
    generator = AnswerGenerator(llm=MockLLM())
    
    # Fast paths out without hitting LLM
    result = generator.generate("query", "NO EVIDENCE FOUND.")
    
    assert result["answer"] == "INSUFFICIENT_EVIDENCE"
    assert result["confidence"] == 0.0
