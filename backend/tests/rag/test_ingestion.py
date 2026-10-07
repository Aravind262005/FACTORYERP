import os
import pytest
from src.rag.ingestion import IngestionPipeline

@pytest.fixture
def sample_markdown_file(tmp_path):
    content = """# Manufacturing Safety Policy
**WARNING**: Wear safety goggles.

## 1. Materials
Handle with care.

---PAGE 2---
## 2. Specifications
Table: Material Limits
Material | Temperature | Humidity
Alloy Steel | 50°C | 30%
Aluminum | 40°C | 40%

## 3. Maintenance
- Check fluids
- Clean gears
"""
    f_path = tmp_path / "mock_policy.md"
    f_path.write_text(content, encoding='utf-8')
    return str(f_path)

def test_ingestion_pipeline(sample_markdown_file):
    pipeline = IngestionPipeline()
    doc = pipeline.process(
        file_path=sample_markdown_file,
        document_id="POL-01",
        metadata={"document_type": "SAFETY POLICY", "revision": "v1"}
    )
    
    assert doc.document_id == "POL-01"
    assert doc.metadata["document_type"] == "SAFETY POLICY"
    assert "checksum" in doc.metadata
    
    # Check structure
    assert len(doc.sections) == 1
    root = doc.sections[0]
    assert root.title == "Manufacturing Safety Policy"
    
    # Check elements in root
    warnings = [e for e in root.elements if e.element_type == "warning"]
    assert len(warnings) == 1
    assert "Wear safety goggles" in warnings[0].text
    
    # Subsections
    assert len(root.subsections) == 3
    assert root.subsections[0].title == "1. Materials"
    assert root.subsections[1].title == "2. Specifications"
    assert root.subsections[2].title == "3. Maintenance"
    
    # Tables in specs
    spec_sec = root.subsections[1]
    assert spec_sec.page == 2
    tables = [e for e in spec_sec.elements if e.element_type == "table"]
    assert len(tables) == 1
    
    # Table should be flattened into rows
    table_text = tables[0].text
    assert "Table: Table: Material Limits" in table_text
    assert "Material = Alloy Steel, Temperature = 50°C, Humidity = 30%" in table_text
    
    # Lists in maintenance
    maint_sec = root.subsections[2]
    lists = [e for e in maint_sec.elements if e.element_type == "list_item"]
    assert len(lists) == 2
    assert "Check fluids" in lists[0].text
