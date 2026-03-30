from typing import List
from app.core.domain_models import Document, Chunk
from app.core.interfaces import ITextProcessor
from app.infrastructure.config import settings
import uuid


class RecursiveTextProcessor(ITextProcessor):
    """
    Concrete Specialist for cleaning and chunking text.
    Matches SRS Class Diagram: RecursiveTextProcessor.
    """

    def process(self, doc: Document) -> List[Chunk]:
        text = self._clean_text(doc.raw_content)
        chunks = self._chunk_text(text)

        return [
            Chunk(
                chunk_id=str(uuid.uuid4()),
                parent_document_uri=doc.source_uri,
                knowledge_base_id=doc.metadata.get("knowledge_base_id", "default"),
                content=chunk_text,
                embedding=[],  # To be filled by the Embedding Model later
                metadata=doc.metadata
            )
            for chunk_text in chunks
        ]

    def _clean_text(self, text: str) -> str:
        # Basic normalization
        return " ".join(text.split())

    def _chunk_text(self, text: str) -> List[str]:
        # Recursive character splitting logic
        chunk_size = settings.chunk_size
        overlap = settings.chunk_overlap

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            if end >= text_len:
                chunks.append(text[start:])
                break

            # Try to find a space to break at
            # (This is a simplified recursive split for clarity)
            chunk = text[start:end]
            chunks.append(chunk)
            start += (chunk_size - overlap)

        return chunks