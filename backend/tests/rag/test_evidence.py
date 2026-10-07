import pytest
from src.rag.evidence import EvidencePackager

def test_evidence_packager():
    packager = EvidencePackager()
    
    chunks = [
        {
            "chunk_id": "C1",
            "text": "Machine M04 requires daily maintenance.",
            "metadata": {
                "document_id": "SOP-14",
                "document_type": "SOP",
                "authority_level": "current",
                "page": 2
            }
        },
        {
            "chunk_id": "C2",
            "text": "If maintenance is missed, capacity drops 20%.",
            "metadata": {
                "document_id": "MAN-05",
                "document_type": "MANUAL"
                # Missing authority and page to test defaults
            }
        }
    ]
    
    output = packager.package(chunks)
    
    # Check headers and tags
    assert "--- EVIDENCE ITEM 1 ---" in output
    assert "[Source: SOP-14 | Type: SOP | Authority: current | Page: 2]" in output
    assert "Machine M04 requires daily maintenance." in output
    
    # Check defaults for missing metadata
    assert "--- EVIDENCE ITEM 2 ---" in output
    assert "[Source: MAN-05 | Type: MANUAL | Authority: UNKNOWN_AUTH | Page: N/A]" in output
    assert "capacity drops 20%" in output
    
def test_evidence_packager_empty():
    packager = EvidencePackager()
    output = packager.package([])
    assert output == "NO EVIDENCE FOUND."
