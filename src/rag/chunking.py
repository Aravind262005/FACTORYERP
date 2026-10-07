from typing import List, Dict, Any
from .schema import ChunkMetadata
from .ingestion.models import ParsedDocument, ParsedSection, ParsedElement
import uuid

class HierarchicalChunker:
    def __init__(self, max_chunk_size: int = 500):
        self.max_chunk_size = max_chunk_size

    def _generate_chunk_id(self, doc_id: str, section_idx: str, chunk_idx: int) -> str:
        return f"{doc_id}-{section_idx}-C{chunk_idx:03d}"

    def chunk_document(self, doc: ParsedDocument) -> List[ChunkMetadata]:
        chunks = []
        global_chunk_idx = 1
        
        # Helper to process sections recursively
        def process_section(section: ParsedSection, parent_id: str = None, section_path: str = ""):
            nonlocal global_chunk_idx
            
            # The section path defines the heading hierarchy
            current_path = f"{section_path} > {section.title}".strip(" > ")
            
            # Create a parent chunk for this section's broader context
            # We aggregate all direct elements to form the parent context
            parent_text = f"Section: {current_path}\n"
            for el in section.elements:
                parent_text += f"{el.text}\n"
                
            sec_chunk_id = self._generate_chunk_id(doc.document_id, f"S{global_chunk_idx}", 0)
            
            # We only create a parent chunk if it has actual content or subsections
            if section.elements or section.subsections:
                parent_chunk = ChunkMetadata(
                    document_id=doc.document_id,
                    chunk_id=sec_chunk_id,
                    parent_id=parent_id,
                    page=section.page,
                    section=current_path,
                    text=parent_text.strip(),
                    document_type=doc.metadata.get("document_type", "UNKNOWN"),
                    department=doc.metadata.get("department"),
                    revision=doc.metadata.get("revision"),
                    effective_date=doc.metadata.get("effective_date"),
                    authority_level=doc.metadata.get("authority_level", "current"),
                    machine_id=doc.metadata.get("machine_id"),
                    product_id=doc.metadata.get("product_id"),
                    material_id=doc.metadata.get("material_id"),
                    topic=doc.metadata.get("topic"),
                    source_file=doc.metadata.get("source_file", "unknown")
                )
                chunks.append(parent_chunk)
            else:
                sec_chunk_id = parent_id # Inherit parent if empty
                
            # Now create child chunks for the elements
            current_child_text = ""
            current_child_page = section.page
            child_idx = 1
            
            for el in section.elements:
                # If an element is large (like a table or warning), it gets its own chunk
                if el.element_type in ["table", "warning"] or len(current_child_text) + len(el.text) > self.max_chunk_size:
                    if current_child_text:
                        chunks.append(ChunkMetadata(
                            document_id=doc.document_id,
                            chunk_id=self._generate_chunk_id(doc.document_id, f"S{global_chunk_idx}", child_idx),
                            parent_id=sec_chunk_id,
                            page=current_child_page,
                            section=current_path,
                            text=current_child_text.strip(),
                            document_type=doc.metadata.get("document_type", "UNKNOWN"),
                            department=doc.metadata.get("department"),
                            revision=doc.metadata.get("revision"),
                            effective_date=doc.metadata.get("effective_date"),
                            authority_level=doc.metadata.get("authority_level", "current"),
                            machine_id=doc.metadata.get("machine_id"),
                            product_id=doc.metadata.get("product_id"),
                            material_id=doc.metadata.get("material_id"),
                            topic=doc.metadata.get("topic"),
                            source_file=doc.metadata.get("source_file", "unknown")
                        ))
                        current_child_text = ""
                        child_idx += 1
                        
                    # Add the special element as its own chunk
                    chunks.append(ChunkMetadata(
                        document_id=doc.document_id,
                        chunk_id=self._generate_chunk_id(doc.document_id, f"S{global_chunk_idx}", child_idx),
                        parent_id=sec_chunk_id,
                        page=el.page,
                        section=current_path,
                        text=el.text.strip(),
                        document_type=doc.metadata.get("document_type", "UNKNOWN"),
                        department=doc.metadata.get("department"),
                        revision=doc.metadata.get("revision"),
                        effective_date=doc.metadata.get("effective_date"),
                        authority_level=doc.metadata.get("authority_level", "current"),
                        machine_id=doc.metadata.get("machine_id"),
                        product_id=doc.metadata.get("product_id"),
                        material_id=doc.metadata.get("material_id"),
                        topic=doc.metadata.get("topic"),
                        source_file=doc.metadata.get("source_file", "unknown")
                    ))
                    child_idx += 1
                else:
                    if not current_child_text:
                        current_child_page = el.page
                    current_child_text += el.text + "\n"
                    
            if current_child_text:
                chunks.append(ChunkMetadata(
                    document_id=doc.document_id,
                    chunk_id=self._generate_chunk_id(doc.document_id, f"S{global_chunk_idx}", child_idx),
                    parent_id=sec_chunk_id,
                    page=current_child_page,
                    section=current_path,
                    text=current_child_text.strip(),
                    document_type=doc.metadata.get("document_type", "UNKNOWN"),
                    department=doc.metadata.get("department"),
                    revision=doc.metadata.get("revision"),
                    effective_date=doc.metadata.get("effective_date"),
                    authority_level=doc.metadata.get("authority_level", "current"),
                    machine_id=doc.metadata.get("machine_id"),
                    product_id=doc.metadata.get("product_id"),
                    material_id=doc.metadata.get("material_id"),
                    topic=doc.metadata.get("topic"),
                    source_file=doc.metadata.get("source_file", "unknown")
                ))

            global_chunk_idx += 1
            
            # Process subsections recursively
            for subsec in section.subsections:
                process_section(subsec, parent_id=sec_chunk_id, section_path=current_path)

        for sec in doc.sections:
            process_section(sec)
            
        return chunks
