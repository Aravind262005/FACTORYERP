# Metadata Schema

This document outlines the formal schema for documents and chunks within the RAG pipeline.

## Document Metadata
Every ingested document MUST support the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `document_id` | str | Yes | Unique identifier (e.g., SOP-014) |
| `document_name` | str | Yes | Name of the document |
| `document_type` | str | Yes | e.g., SOP, MANUAL, SAFETY POLICY |
| `title` | str | No | Formal title |
| `department` | str | No | Relevant department |
| `machine_id` | str | No | Associated machine |
| `product_id` | str | No | Associated product |
| `material_id` | str | No | Associated material |
| `topic` | str | No | General topic |
| `revision` | str | No | Revision string (e.g., Rev-3) |
| `version` | str | No | Semantic versioning if applicable |
| `effective_date`| str | No | ISO-8601 date |
| `expiry_date` | str | No | ISO-8601 date |
| `authority_level`| str | Yes | e.g., current, superseded (default: current) |
| `source_file` | str | Yes | File path or URI |
| `page_count` | int | No | Total pages |
| `ingestion_timestamp`| datetime | Yes | Time of ingestion |
| `checksum` | str | Yes | SHA-256 hash for duplicate detection |

## Chunk Metadata
Every retrieval chunk MUST contain:

| Field | Type | Required | Description |
|---|---|---|---|
| `document_id` | str | Yes | Inherited from Document |
| `chunk_id` | str | Yes | Unique ID for the chunk (e.g., SOP-014-S05-C01) |
| `parent_id` | str | No | ID of the parent section chunk |
| `page` | int | No | Page number where text resides |
| `section` | str | No | Section heading or number |
| `text` | str | Yes | The textual content |
| `document_type` | str | Yes | Inherited |
| `department` | str | No | Inherited |
| `revision` | str | No | Inherited |
| `effective_date`| str | No | Inherited |
| `authority_level`| str | Yes | Inherited |
| `machine_id` | str | No | Inherited |
| `product_id` | str | No | Inherited |
| `material_id` | str | No | Inherited |
| `topic` | str | No | Inherited |
| `source_file` | str | Yes | Inherited |

## Rationale
- **Traceability:** `document_id`, `chunk_id`, `page` ensure we can cite the exact location of the evidence.
- **Hierarchy:** `parent_id` allows expanding context after retrieving a child chunk.
- **Authority:** `revision`, `effective_date`, `authority_level` support policy-aware resolution of conflicts.
- **Filtering:** `machine_id`, `material_id`, `department` allow precise constraint application when queries specify them.
