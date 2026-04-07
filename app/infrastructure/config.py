from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LlmApiConfig(BaseSettings):
    """
    Configuration object for LLM Client.
    Matches SRS Class Diagram: HttpLlmClient dependency.
    """
    model_name: str = "gemini-3-flash-preview"

    # Additional config for Embedding (Gemini)
    embedding_api_key: str = Field(alias="GOOGLE_API_KEY")
    embedding_model_name: str = "gemini-embedding-001"
    embedding_dimension: int = 3072  # gemini-embedding-001 uses 3072 dimensions
    chunk_size: int = 1000
    chunk_overlap: int = 100
    # Database
    database_url: str = "postgresql+psycopg://admin:secretpassword@localhost:5432/supportsphere"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Global instance
settings = LlmApiConfig()