from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LlmApiConfig(BaseSettings):
    """
    Configuration object for LLM Client.
    Matches SRS Class Diagram: HttpLlmClient dependency.
    """
    api_endpoint_url: str = "https://api.openai.com/v1/chat/completions"  # Default for OpenAI
    api_key: str = Field(alias="OPENAI_API_KEY")
    model_name: str = "gpt-4o-mini"

    # Additional config for Embedding (Gemini)
    embedding_api_key: str = Field(alias="GOOGLE_API_KEY")
    embedding_model_name: str = "models/gemini-embedding-exp-03-07"
    embedding_dimension: int = 3072  # Gemini uses 768 dimensions
    chunk_size: int = 1000
    chunk_overlap: int = 100
    # Database
    database_url: str = "postgresql+psycopg://admin:secretpassword@localhost:5432/supportsphere"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Global instance
settings = LlmApiConfig()