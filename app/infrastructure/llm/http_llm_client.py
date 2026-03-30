from openai import OpenAI
from app.core.interfaces import ILLMGenerator
from app.infrastructure.config import LlmApiConfig

class HttpLlmClient(ILLMGenerator):
    """
    Adapter for external HTTP-based LLMs.
    Matches SRS Class Diagram: Specialists.
    """
    def __init__(self, config: LlmApiConfig):
        self.client = OpenAI(api_key=config.api_key)
        self.model_name = config.model_name

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful support assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content