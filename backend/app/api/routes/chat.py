"""
Chat API routes with RAG support
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import AsyncIterator
import json
import logging

from ...schemas.document import ChatRequest, ChatMessage
from ...services.rag_engine import RAGEngine

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# Initialize RAG engine
rag_engine = RAGEngine()


async def event_generator(
    request: ChatRequest
) -> AsyncIterator[str]:
    """
    Generate Server-Sent Events for streaming chat response

    Yields:
        SSE formatted strings
    """
    try:
        # Stream RAG response
        response_stream = rag_engine.chat_stream(
            query=request.message,
            use_rag=request.use_rag,
            top_k=request.top_k,
            model=request.model
        )

        for chunk in response_stream:
            # Format as SSE
            data = json.dumps(chunk, ensure_ascii=False)
            yield f"data: {data}\n\n"

    except Exception as e:
        logger.error(f"Chat error: {e}")
        error_data = {
            "type": "error",
            "data": {"message": str(e)}
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Chat with streaming response using Server-Sent Events

    This endpoint returns a stream of events:
    1. retrieval: Retrieved document information (if use_rag=True)
    2. text: Streaming text chunks from LLM
    3. done: Completion signal
    4. error: Error information (if any)
    """
    return StreamingResponse(
        event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.post("/message")
async def chat_message(request: ChatRequest):
    """
    Chat without streaming (returns complete response)
    """
    try:
        # Get non-streaming response
        response = rag_engine.chat(
            query=request.message,
            use_rag=request.use_rag,
            top_k=request.top_k,
            model=request.model,
            stream=False
        )

        return {
            "message": request.message,
            "response": response,
            "model": request.model or "default"
        }

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@router.get("/models")
async def get_models():
    """Get available LLM models"""
    try:
        models = rag_engine.llm_client.get_available_models()
        return models
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get models: {str(e)}"
        )
