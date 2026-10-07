# Document Version and Authority Handling

## Overview
In a manufacturing context, operating on superseded or draft documents can be catastrophic. The RAG system must strictly enforce authority levels at the retrieval layer.

## Implementation
- **Metadata Field**: The `ChunkMetadata` schema includes an `authority_level` field, which can be `current`, `superseded`, `draft`, etc.
- **Default Censoring**: The `HybridRetriever.search()` method intercepts all query requests. If no explicit authority level is requested, it forcibly injects `{"authority_level": "current"}` into the strict constraints. This ensures that only active policies are retrieved for general queries.
- **Historical Query Detection**: The `QueryAnalyzer` uses keyword heuristics (e.g., "previous", "old", "superseded", "past") to detect if a user is explicitly asking for historical contexts (e.g., "What was the previous max temperature for M04 before the 2023 update?"). If detected, the strict `current` filter is lifted, and all authority levels are searched.
