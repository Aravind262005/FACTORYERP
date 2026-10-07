import pytest
from pydantic import ValidationError
from datetime import datetime
import sys
import os

# Add src to python path for testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from rag.schema import DocumentMetadata, ChunkMetadata

def test_document_metadata_valid():
    doc = DocumentMetadata(
        document_id="SOP-014",
        document_name="Alloy Steel Storage SOP",
        document_type="SOP",
        revision="Rev-3",
        authority_level="current",
        source_file="/docs/SOP-014.pdf",
        checksum="abcdef123456"
    )
    assert doc.document_id == "SOP-014"
    assert doc.authority_level == "current"
    assert doc.checksum == "abcdef123456"
    assert isinstance(doc.ingestion_timestamp, datetime)

def test_document_metadata_missing_required():
    with pytest.raises(ValidationError):
        DocumentMetadata(
            document_name="Test",
            document_type="SOP"
            # Missing document_id, source_file, checksum
        )

def test_chunk_metadata_valid():
    chunk = ChunkMetadata(
        document_id="SOP-014",
        chunk_id="SOP-014-C01",
        parent_id="SOP-014-S01",
        page=7,
        text="Store alloy steel at room temperature.",
        document_type="SOP",
        authority_level="current",
        revision="Rev-3",
        source_file="/docs/SOP-014.pdf"
    )
    assert chunk.chunk_id == "SOP-014-C01"
    assert chunk.parent_id == "SOP-014-S01"
    assert chunk.page == 7
    assert chunk.text == "Store alloy steel at room temperature."

def test_chunk_metadata_missing_required():
    with pytest.raises(ValidationError):
        ChunkMetadata(
            document_id="SOP-014",
            text="Missing stuff",
            # Missing chunk_id, document_type, authority_level, source_file
        )
