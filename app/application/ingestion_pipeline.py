import logging
import time
from tqdm import tqdm
from typing import List
from app.core.interfaces import (
    ITextProcessor,
    IEmbeddingModel,
    IKnowledgeBaseWriter
)
from app.core.factories import ExtractorFactory

# Configure logger
logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Orchestrator for the offline knowledge ingestion workflow.
    Matches SRS Class Diagram: IngestionPipeline.
    """

    def __init__(
            self,
            text_processor: ITextProcessor,
            embedding_model: IEmbeddingModel,
            kb_writer: IKnowledgeBaseWriter
    ):
        # Dependency Injection via Constructor (DIP)
        self.processor = text_processor
        self.embedder = embedding_model
        self.writer = kb_writer

    def run(self, source_uri: str, knowledge_base_id: str) -> dict:
        """
        Executes the pipeline for a single source.
        """
        logger.info(f"Starting ingestion for: {source_uri} into KB: {knowledge_base_id}")

        try:
            # 1. Extract (Strategy Pattern via Factory)
            extractor = ExtractorFactory.create_extractor(source_uri)
            document = extractor.extract(source_uri)

            # Enrich metadata
            document.metadata["knowledge_base_id"] = knowledge_base_id
            logger.info(f"Extracted {len(document.raw_content)} chars from document.")

            # 2. Process (Clean & Chunk)
            chunks = self.processor.process(document)
            logger.info(f"Generated {len(chunks)} text chunks.")

            # 3. Embed (Vectorize)
            # Note: In a production system, we would batch this.
            # For V1.0, simple iteration is fine as per SRS.
            for chunk in tqdm(chunks, desc="Embedding", unit="chunk"):
                chunk.embedding = self.embedder.embed(chunk.content)
                time.sleep(2)

            # 4. Load (Upsert to DB)
            self.writer.upsert(chunks)
            logger.info("Successfully loaded chunks to database.")

            return {
                "status": "success",
                "chunks_processed": len(chunks),
                "document_id": document.content_hash  # Using hash as ID for now
            }

        except Exception as e:
            logger.error(f"Ingestion failed: {str(e)}")
            raise e