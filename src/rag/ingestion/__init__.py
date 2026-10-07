from .models import ParsedDocument
from .extractor import MarkdownExtractor
from .structure_parser import StructureParser
from .loader import DocumentLoader, DocumentCleaner, generate_checksum
import datetime

class IngestionPipeline:
    def __init__(self):
        self.loader = DocumentLoader()
        self.cleaner = DocumentCleaner()
        self.extractor = MarkdownExtractor()
        self.parser = StructureParser()
        
    def process(self, file_path: str, document_id: str, metadata: dict = None) -> ParsedDocument:
        """Runs the complete ingestion pipeline."""
        if metadata is None:
            metadata = {}
            
        raw_text = self.loader.load(file_path)
        cleaned_text = self.cleaner.clean(raw_text)
        
        checksum = generate_checksum(cleaned_text)
        metadata['checksum'] = checksum
        metadata['source_file'] = file_path
        metadata['ingestion_timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        elements = self.extractor.extract(cleaned_text)
        doc = self.parser.parse(elements, document_id, metadata)
        
        return doc
