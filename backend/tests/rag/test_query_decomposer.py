import pytest
from src.rag.query.decomposer import QueryDecomposer

class MockLLM:
    def with_structured_output(self, schema):
        return self
        
    def invoke(self, text):
        class MockResult:
            def __init__(self, queries):
                self.queries = queries
                
        if "Raw Query: Compare" in text:
            return MockResult(["maintenance schedule for M04", "maintenance schedule for M05"])
        else:
            return MockResult(["What is the max temperature of M04?"])

def test_query_decomposer_with_mock():
    # Pass the mock LLM
    decomposer = QueryDecomposer(llm=MockLLM())
    
    # Multi-hop query
    raw_query = "Compare the maintenance schedule of M04 and M05"
    sub_queries = decomposer.decompose(raw_query)
    
    assert len(sub_queries) == 2
    assert sub_queries[0] == "maintenance schedule for M04"
    assert sub_queries[1] == "maintenance schedule for M05"
    
    # Simple query
    simple_query = "What is the max temperature of M04?"
    sub_queries2 = decomposer.decompose(simple_query)
    
    assert len(sub_queries2) == 1
    assert sub_queries2[0] == simple_query

def test_query_decomposer_fallback():
    # Fallback to pass-through
    decomposer = QueryDecomposer(llm=None)
    decomposer.llm = None
    
    raw_query = "Compare the maintenance schedule of M04 and M05"
    sub_queries = decomposer.decompose(raw_query)
    
    assert len(sub_queries) == 1
    assert sub_queries[0] == raw_query
