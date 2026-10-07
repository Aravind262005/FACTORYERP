# Hierarchical Chunking

## Overview
The `HierarchicalChunker` takes the structured `ParsedDocument` from the ingestion pipeline and converts it into a list of retrieval-ready `ChunkMetadata` objects while preserving parent-child relationships.

## Parent-Child Relationship
Documents are NOT blindly split by an arbitrary token count. The hierarchy is:
```
Document -> Section -> Subsection -> Child Chunk
```
- **Parent Chunks (Section/Subsection context):**
  Each section generates a "Parent Chunk" containing the section title and all direct element text. It has `chunk_id` ending in `-C000`.
- **Child Chunks (Specific elements):**
  Each element inside a section generates one or more "Child Chunks".
  A child chunk explicitly stores the `parent_id` referencing its parent section chunk.

## Special Element Handling
- **Tables and Warnings:**
  Are never arbitrarily split in half by character counts. They are isolated into their own dedicated child chunks to maintain their semantic boundaries.
- **Normal Text:**
  Is grouped together until `max_chunk_size` is reached to form a reasonably sized child chunk.

## Metadata Propagation
When a child chunk is created, it inherits **all** document-level metadata (e.g., `document_type`, `revision`, `authority_level`, `machine_id`) to ensure it can be filtered accurately during retrieval without needing to join back to the document record.
