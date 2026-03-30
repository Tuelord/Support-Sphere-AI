import google.generativeai as genai
from typing import List
from app.core.interfaces import IEmbeddingModel

class GeminiEmbeddingModel(IEmbeddingModel):
    """
    Concrete implementation of IEmbeddingModel using Google Gemini.
    Replaces 'SentenceTransformerModel' from diagram as the chosen strategy.
    """
    def __init__(self, api_key: str, model_name: str):
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def embed(self, text: str) -> List[float]:
        # Gemini API call
        result = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']