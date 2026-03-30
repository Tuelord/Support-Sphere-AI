from dependency_injector import containers, providers
from app.infrastructure.config import settings
from app.infrastructure.llm.http_llm_client import HttpLlmClient
from app.infrastructure.llm.gemini_embedding_model import GeminiEmbeddingModel
from app.infrastructure.database.postgres_knowledge_base import PostgresKnowledgeBase
from app.infrastructure.processors.recursive_text_processor import RecursiveTextProcessor
from app.application.ingestion_pipeline import IngestionPipeline
from app.application.conversational_api_handler import ConversationalAPIHandler


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.interface.api.routes", "app.interface.cli.ingest"]
    )

    # Configuration
    config = providers.Configuration(pydantic_settings=[settings])

    # --- Infrastructure Layer (Specialists) ---

    # LLM Generator (Adapter)
    llm_client = providers.Singleton(
        HttpLlmClient,
        config=providers.Object(settings)  # Passes the LlmApiConfig object
    )

    # Embedding Model (Gemini)
    embedding_model = providers.Singleton(
        GeminiEmbeddingModel,
        api_key=config.embedding_api_key,
        model_name=config.embedding_model_name
    )

    # Database (Postgres + pgvector)
    knowledge_base = providers.Singleton(
        PostgresKnowledgeBase
    )

    # Text Processor
    text_processor = providers.Singleton(
        RecursiveTextProcessor
    )

    # --- Application Layer (Orchestrators) ---

    # Ingestion Pipeline
    ingestion_pipeline = providers.Factory(
        IngestionPipeline,
        text_processor=text_processor,
        embedding_model=embedding_model,
        kb_writer=knowledge_base
    )

    # Conversational API Handler
    conversational_handler = providers.Factory(
        ConversationalAPIHandler,
        kb_reader=knowledge_base,
        embedding_model=embedding_model,
        llm_generator=llm_client
    )