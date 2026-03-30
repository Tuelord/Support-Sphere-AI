from abc import ABC, abstractmethod
from typing import List
from app.core.domain_models import Document, Chunk

class IContentExtractor(ABC):
    """
    Contract for extracting content from a source URI.
    Matches SRS Class Diagram: Interfaces.
    """
    @abstractmethod
    def extract(self, uri: str) -> Document:
        pass

class ITextProcessor(ABC):
    """
    Contract for cleaning and chunking text.
    Matches SRS Class Diagram: Interfaces.
    """
    @abstractmethod
    def process(self, doc: Document) -> List[Chunk]:
        pass

class IEmbeddingModel(ABC):
    """
    Contract for generating vector embeddings.
    Matches SRS Class Diagram: Interfaces.
    """
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass

class IKnowledgeBaseWriter(ABC):
    """
    Contract for writing chunks to the database (ISP applied).
    Matches SRS Class Diagram: Interfaces.
    """
    @abstractmethod
    def upsert(self, chunks: List[Chunk]) -> None:
        pass

class IKnowledgeBaseReader(ABC):
    """
    Contract for reading/searching chunks from the database (ISP applied).
    Matches SRS Class Diagram: Interfaces.
    """
    @abstractmethod
    def search(self, vector: List[float], k: int, knowledge_base_id: str) -> List[Chunk]:
        pass

class ILLMGenerator(ABC):
    """
    Contract for generating text from a prompt.
    Matches SRS Class Diagram: Interfaces.
    """
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass