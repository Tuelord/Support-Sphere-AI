import hashlib
from pypdf import PdfReader
from app.core.domain_models import Document
from app.core.interfaces import IContentExtractor


class PdfExtractor(IContentExtractor):
    """
    Concrete Strategy for extracting text from PDFs.
    Matches SRS Class Diagram: PdfExtractor.
    """

    def extract(self, uri: str) -> Document:
        # uri is expected to be a local file path for V1.0
        reader = PdfReader(uri)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

        return Document(
            source_uri=uri,
            content_hash=content_hash,
            raw_content=text,
            metadata={
                "source_type": "pdf",
                "content_hash": content_hash
            }
        )