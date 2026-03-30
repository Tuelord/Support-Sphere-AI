from datetime import datetime
from typing import List
from sqlalchemy import String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.infrastructure.config import settings

class Base(DeclarativeBase):
    pass

class KnowledgeBaseModel(Base):
    """
    Table: KNOWLEDGE_BASES
    Matches SRS ERD exactly.
    """
    __tablename__ = "knowledge_bases"

    knowledge_base_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    documents: Mapped[List["DocumentModel"]] = relationship(back_populates="knowledge_base")

class DocumentModel(Base):
    """
    Table: DOCUMENTS
    Matches SRS ERD exactly.
    """
    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(String(50), primary_key=True) # We will use Hash or UUID
    knowledge_base_id: Mapped[str] = mapped_column(ForeignKey("knowledge_bases.knowledge_base_id"))
    source_uri: Mapped[str] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(64))
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default={}) # 'metadata' is reserved in SQLAlchemy
    last_ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    knowledge_base: Mapped["KnowledgeBaseModel"] = relationship(back_populates="documents")
    chunks: Mapped[List["ChunkModel"]] = relationship(back_populates="document")

class ChunkModel(Base):
    """
    Table: CHUNKS
    Matches SRS ERD exactly.
    """
    __tablename__ = "chunks"

    chunk_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.document_id"))
    content: Mapped[str] = mapped_column(Text)
    # Vector column from pgvector extension
    embedding: Mapped[List[float]] = mapped_column(Vector(settings.embedding_dimension))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    document: Mapped["DocumentModel"] = relationship(back_populates="chunks")