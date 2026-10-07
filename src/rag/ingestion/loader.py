import hashlib
import os


def generate_checksum(content: str) -> str:
    """Generates a SHA-256 checksum for the document content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


class DocumentCleaner:
    """Cleans up OCR noise, weird whitespaces, and normalizes text."""
    def clean(self, text: str) -> str:
        # Simple cleanup logic for Phase 2
        text = text.replace('\r', '')
        # Remove excessive blank lines
        import re
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


class DocumentLoader:
    """Loads file bytes and routes to the appropriate parser."""
    def load(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")

        ext = file_path.lower().split('.')[-1]

        if ext == 'pdf':
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise ValueError('PDF parsing requires the pypdf package. Install backend requirements.') from exc

            reader = PdfReader(file_path)
            pages = []
            for page in reader.pages:
                text = page.extract_text() or ''
                if text:
                    pages.append(text)

            text = '\n'.join(pages).strip()
            if not text:
                raise ValueError('The uploaded PDF does not contain extractable text.')
            return text

        if ext == 'docx':
            try:
                from docx import Document
            except ImportError as exc:
                raise ValueError('DOCX parsing requires the python-docx package. Install backend requirements.') from exc

            doc = Document(file_path)
            paragraphs = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
            text = '\n'.join(paragraphs).strip()
            if not text:
                raise ValueError('The uploaded DOCX file does not contain readable text.')
            return text

        if ext == 'doc':
            raise ValueError('Legacy .doc files are not supported. Please upload .txt, .md, .pdf, or .docx files.')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            raise ValueError('Failed to read file as text. Supported text formats are .md and .txt.')
