from typing import Dict, List, Optional
from app.core.interfaces import (
    IKnowledgeBaseReader,
    IEmbeddingModel,
    ILLMGenerator
)
from app.infrastructure.config import settings


class ConversationalAPIHandler:
    """
    Orchestrator for the real-time RAG workflow.
    Matches SRS Class Diagram: ConversationalAPIHandler.
    """

    def __init__(
            self,
            kb_reader: IKnowledgeBaseReader,
            embedding_model: IEmbeddingModel,
            llm_generator: ILLMGenerator
    ):
        self.reader = kb_reader
        self.embedder = embedding_model
        self.llm = llm_generator

        # Triage Configuration (Feature 4.3)
        # In a real app, this might come from a DB, but config is fine for V1.0
        self.escalation_keywords = [
            "refund", "angry", "lawsuit", "human", "agent", "speak to someone",
            "cancel subscription", "emergency"
        ]
        self.escalation_message = (
            "I understand this is important. I'm escalating this to a human agent immediately. "
            "Please contact us at support@example.com or call 1-800-555-0199."
        )

    async def handle_query(self, query: str, knowledge_base_id: str) -> Dict:
        """
        Main entry point for processing a user query.
        """
        # 1. Intelligent Triage (Feature 4.3)
        if self._should_escalate(query):
            return {
                "answer": self.escalation_message,
                "sources": [],
                "status": "escalated"
            }

        # 2. Generate Query Embedding
        query_vector = self.embedder.embed(query)

        # 3. Semantic Search (Feature 4.1)
        # We fetch top-3 chunks for context
        relevant_chunks = self.reader.search(
            vector=query_vector,
            k=3,
            knowledge_base_id=knowledge_base_id
        )

        # 4. Check Relevance (Fallback)
        if not relevant_chunks:
            return {
                "answer": "I'm sorry, I couldn't find any information in my knowledge base about that. Could you try rephrasing?",
                "sources": [],
                "status": "no_content"
            }

        # 5. Augment Prompt
        context_text = "\n\n".join([c.content for c in relevant_chunks])
        augmented_prompt = self._build_prompt(query, context_text)

        # 6. Generate Response (LLM)
        answer = self.llm.generate(augmented_prompt)

        # 7. Return Response
        return {
            "answer": answer,
            "sources": [
                {"chunk_id": c.chunk_id, "source": c.parent_document_uri}
                for c in relevant_chunks
            ],
            "status": "success"
        }

    def _should_escalate(self, query: str) -> bool:
        """Checks if the query triggers any escalation keywords."""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.escalation_keywords)

    def _build_prompt(self, query: str, context: str) -> str:
        """Constructs the system prompt for the LLM."""
        return (
            "You are a helpful customer support agent for SupportSphere AI.\n"
            "Use the following pieces of retrieved context to answer the user's question.\n"
            "If the answer is not in the context, say that you don't know.\n"
            "Keep the answer concise and professional.\n\n"
            f"Context:\n{context}\n\n"
            f"User Question: {query}"
        )