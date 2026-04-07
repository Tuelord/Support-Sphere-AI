from google import genai
from google.genai import types
from typing import List
from app.core.interfaces import IEmbeddingModel

class GeminiEmbeddingModel(IEmbeddingModel):
    """
    Concrete implementation of IEmbeddingModel using Google Gemini.
    Replaces 'SentenceTransformerModel' from diagram as the chosen strategy.
    """
    def __init__(self, api_key: str, model_name: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def embed(self, text: str) -> List[float]:
        # Gemini API call
        result = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )
        return result.embeddings[0].values