from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from dependency_injector.wiring import inject, Provide
from app.container import Container
from app.application.conversational_api_handler import ConversationalAPIHandler

router = APIRouter()


# --- DTOs (Data Transfer Objects) ---
# Matches SRS REQ-CQA-01
class ChatRequest(BaseModel):
    query: str
    knowledge_base_id: str


class SourceDTO(BaseModel):
    chunk_id: str
    source: str


# Matches SRS REQ-CQA-07
class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDTO]
    status: str


# --- Route Handler ---
@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Conversational Question Answering"
)
@inject
async def chat_endpoint(
        request: ChatRequest,
        # Dependency Injection: The Container provides the initialized Handler
        handler: ConversationalAPIHandler = Depends(Provide[Container.conversational_handler])
):
    """
    Entry point for the Chat Widget.
    Delegates logic to the Application Layer.
    """
    try:
        result = await handler.handle_query(
            query=request.query,
            knowledge_base_id=request.knowledge_base_id
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            status=result["status"]
        )
    except Exception as e:
        # In a real app, we would log this and return a generic error
        raise HTTPException(status_code=500, detail=str(e))