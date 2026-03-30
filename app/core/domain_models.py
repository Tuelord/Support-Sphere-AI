from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Document:
    """
    Represents the raw data extracted from a source.
    Matches SRS Class Diagram: Domain Models.
    """
    source_uri: str
    content_hash: str
    raw_content: str
    metadata: Dict = field(default_factory=dict)

@dataclass
class Chunk:
    """
    The final, atomic unit of knowledge.
    Matches SRS Class Diagram: Domain Models.
    """
    chunk_id: str
    parent_document_uri: str
    knowledge_base_id: str
    content: str
    embedding: List[float]
    metadata: Dict = field(default_factory=dict)