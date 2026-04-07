from google import genai
from google.genai import types
from app.core.interfaces import ILLMGenerator
from app.infrastructure.config import LlmApiConfig


class HttpLlmClient(ILLMGenerator):
    """
    Adapter for external HTTP-based LLMs.
    Matches SRS Class Diagram: Specialists.
    """
    def __init__(self, config: LlmApiConfig):
        # Use the config's embedding_api_key since we're using Google Gemini for everything now
        self.client = genai.Client(api_key=config.embedding_api_key)
        self.model_name = config.model_name  # Set to a Gemini text model

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful support assistant.",
                temperature=0.3
            )
        )
        return response.text