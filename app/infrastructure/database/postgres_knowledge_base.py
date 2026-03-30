from typing import List
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker
from app.core.interfaces import IKnowledgeBaseReader, IKnowledgeBaseWriter
from app.core.domain_models import Chunk
from app.infrastructure.database.models import Base, ChunkModel, DocumentModel, KnowledgeBaseModel
from app.infrastructure.config import settings


class PostgresKnowledgeBase(IKnowledgeBaseReader, IKnowledgeBaseWriter):
    """
    Concrete Specialist for PostgreSQL + pgvector.
    Matches SRS Class Diagram: PostgresKnowledgeBase.
    """

    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Ensure tables and extension exist (Imperative Shell setup)
        self._init_db()

    def _init_db(self):
        with self.engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(bind=self.engine)

    def upsert(self, chunks: List[Chunk]) -> None:
        """
        Implementation of IKnowledgeBaseWriter.
        Handles hierarchy: KB -> Document -> Chunks
        """
        if not chunks:
            return

        session = self.SessionLocal()
        try:
            # Group chunks by document to minimize DB queries
            # (Simplified logic for V1.0: We assume chunks come from one doc in the pipeline)
            first_chunk = chunks[0]
            kb_id = first_chunk.knowledge_base_id
            doc_uri = first_chunk.parent_document_uri

            # 1. Ensure Knowledge Base exists
            kb = session.get(KnowledgeBaseModel, kb_id)
            if not kb:
                kb = KnowledgeBaseModel(knowledge_base_id=kb_id)
                session.add(kb)
                session.flush()  # Flush to ensure ID exists for FKs

            # 2. Ensure Document exists (Upsert logic)
            # We use the URI as a unique identifier for the document logic here
            # In a real app, we might hash the URI to get the ID.
            # For now, let's generate a deterministic ID or use the one passed if available.
            # To keep it simple and robust: We assume the pipeline handles ID generation or we create one.
            # Let's assume document_id is derived from the URI hash in the domain model or passed in metadata.
            # For this implementation, we will query by URI.

            stmt = select(DocumentModel).where(DocumentModel.source_uri == doc_uri)
            doc = session.execute(stmt).scalar_one_or_none()

            if not doc:
                doc = DocumentModel(
                    document_id=first_chunk.metadata.get("content_hash", "unknown"),  # Use hash as ID
                    knowledge_base_id=kb_id,
                    source_uri=doc_uri,
                    content_hash=first_chunk.metadata.get("content_hash", ""),
                    metadata_=first_chunk.metadata
                )
                session.add(doc)
                session.flush()

            # 3. Insert Chunks
            # We delete existing chunks for this doc to avoid duplicates (Overwrite strategy)
            session.execute(
                text("DELETE FROM chunks WHERE document_id = :doc_id"),
                {"doc_id": doc.document_id}
            )

            for chunk in chunks:
                db_chunk = ChunkModel(
                    chunk_id=chunk.chunk_id,
                    document_id=doc.document_id,
                    content=chunk.content,
                    embedding=chunk.embedding
                )
                session.add(db_chunk)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def search(self, vector: List[float], k: int, knowledge_base_id: str) -> List[Chunk]:
        """
        Implementation of IKnowledgeBaseReader.
        Uses pgvector cosine distance (<=> operator).
        """
        session = self.SessionLocal()
        try:
            # Semantic Search Query
            # We join with Document to filter by Knowledge Base ID
            stmt = (
                select(ChunkModel)
                .join(DocumentModel)
                .where(DocumentModel.knowledge_base_id == knowledge_base_id)
                .order_by(ChunkModel.embedding.cosine_distance(vector))
                .limit(k)
            )

            results = session.execute(stmt).scalars().all()

            # Map back to Domain Model
            domain_chunks = []
            for db_chunk in results:
                domain_chunks.append(Chunk(
                    chunk_id=db_chunk.chunk_id,
                    parent_document_uri=db_chunk.document.source_uri,
                    knowledge_base_id=knowledge_base_id,
                    content=db_chunk.content,
                    embedding=db_chunk.embedding.tolist(),  # Convert numpy/vector to list
                    metadata=db_chunk.document.metadata_
                ))

            return domain_chunks
        finally:
            session.close()