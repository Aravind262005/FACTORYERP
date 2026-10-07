# Document Ingestion Pipeline

## Overview
The ingestion pipeline converts raw source documents into a structured, hierarchical `ParsedDocument` representation, explicitly avoiding flattening the text prematurely.

## Components

1. **DocumentLoader** (`loader.py`): Reads raw bytes and validates file existence.
2. **DocumentCleaner** (`loader.py`): Removes OCR noise, normalizes line breaks, and standardizes text.
3. **MarkdownExtractor** (`extractor.py`): Identifies document layout elements from the text (simulating advanced PDF layout extraction). It detects:
   - Pages (`---PAGE X---`)
   - Headings (`#`, `##`)
   - Tables (Markdown pipe format)
   - Warnings (`**WARNING**:`)
   - List items
4. **StructureParser** (`structure_parser.py`): Takes the linear stream of `ParsedElement` objects and builds a hierarchical tree of `ParsedSection`s.

## Tables
Tables are preserved rather than flattened into unstructured text. `parse_markdown_table` converts grid formats into explicit row statements:
```
Table: Material Limits
Row 1: Material = Alloy Steel, Temperature = 50°C, Humidity = 30%
```
This ensures the LLM and vector database preserve the explicit relationship between row and column headers.

## Traceability
Each `ParsedElement` maintains its `page` number and `metadata` to ensure all generated chunks will trace perfectly back to the original source location.
