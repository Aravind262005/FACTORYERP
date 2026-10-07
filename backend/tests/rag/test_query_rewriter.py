import pytest
from src.rag.query.rewriter import QueryRewriter

class MockLLM:
    def with_structured_output(self, schema):
        return self
        
    def invoke(self, text):
        class MockResult:
            def __init__(self):
                self.query = "preventive maintenance schedule for M04"
        return MockResult()

def test_query_rewriter_with_mock():
    # Pass the mock LLM to avoid real API calls
    rewriter = QueryRewriter(llm=MockLLM())
    
    raw_query = "Hey, what is the PM sched for M04?"
    rewritten = rewriter.rewrite(raw_query)
    
    assert rewritten == "preventive maintenance schedule for M04"

def test_query_rewriter_fallback():
    # If no LLM is provided and no API key, it should fallback to pass-through
    rewriter = QueryRewriter(llm=None)
    
    # We forcefully set llm to None in case the environment has an API key
    rewriter.llm = None
    
    raw_query = "Hey, what is the PM sched for M04?"
    rewritten = rewriter.rewrite(raw_query)
    
    assert rewritten == raw_query
