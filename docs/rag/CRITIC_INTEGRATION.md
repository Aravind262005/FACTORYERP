# Critic Integration

## Overview
The "Agentic Manufacturing Decision Support Platform" uses a multi-agent orchestration architecture managed by LangGraph. Before any decision is returned to the user, a `CriticAgent` evaluates the outputs of all reasoning agents (Production, Inventory, Knowledge) to ensure cross-agent consistency and high reliability.

## Implementation Details
- **Module:** `backend/app/agents/critic/agent.py`
- **Validation Logic:** I updated the `CriticAgent` to explicitly validate the dictionary payload emitted by the `KnowledgeAgent` during Phase 15.
- **Minimum Thresholds Enforced:**
  1. **Confidence Threshold:** If the Knowledge Agent's self-assigned confidence score is `< 0.8`, the Critic rejects the output and triggers a `knowledge_conflict`. (This catches `INSUFFICIENT_EVIDENCE` states which are strictly hardcoded to `0.0` confidence).
  2. **Citation Requirement:** If the `sources` array in the RAG payload is empty, the Critic immediately rejects the output, ensuring no ungrounded LLM hallucinations can leak into the final recommendation.
- **Workflow Interoperability:** Because the `KnowledgeAgent` payload perfectly matches the dictionary schemas expected by the other agents, the LangGraph workflow seamlessly routes the data without requiring any node modifications.
