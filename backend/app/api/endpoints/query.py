from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
import logging

from app.models.database import (
    get_db,
    KnowledgeBase as KnowledgeBaseModel,
    Conversation as ConversationModel,
    Message as MessageModel
)
from app.models.schemas import QueryRequest, QueryResponse, SourceDocument
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=QueryResponse)
async def query_knowledge_base(
    query_req: QueryRequest,
    db: Session = Depends(get_db)
):
    """Query the knowledge base using RAG."""
    # Check knowledge base exists
    kb = db.query(KnowledgeBaseModel).filter(
        KnowledgeBaseModel.id == query_req.knowledge_base_id
    ).first()
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {query_req.knowledge_base_id} not found"
        )

    # Get or create conversation
    conversation_id = query_req.conversation_id
    if conversation_id:
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
    else:
        # Create new conversation
        conversation = ConversationModel(
            knowledge_base_id=query_req.knowledge_base_id,
            title=query_req.question[:100]  # Use first 100 chars as title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id

    # Save user message
    user_message = MessageModel(
        conversation_id=conversation_id,
        role="user",
        content=query_req.question
    )
    db.add(user_message)
    db.commit()

    # Retrieve relevant documents
    try:
        search_results = vector_store.search(
            knowledge_base_id=query_req.knowledge_base_id,
            query=query_req.question,
            top_k=query_req.top_k
        )
    except Exception as e:
        logger.error(f"Error searching vector store: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search knowledge base"
        )

    if not search_results:
        answer = "I couldn't find any relevant information in the knowledge base to answer your question."
        sources = []
    else:
        # Get conversation history
        conversation_history = []
        if conversation:
            messages = db.query(MessageModel).filter(
                MessageModel.conversation_id == conversation_id
            ).order_by(MessageModel.created_at).all()
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in messages[-10:]  # Last 10 messages
            ]

        # Generate answer using LLM
        try:
            answer_parts = []
            async for chunk in llm_service.generate_answer(
                question=query_req.question,
                context_docs=search_results,
                conversation_history=conversation_history,
                stream=False
            ):
                answer_parts.append(chunk)
            answer = "".join(answer_parts)
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate answer: {str(e)}"
            )

        # Format sources
        sources = [
            SourceDocument(
                content=doc['content'],
                metadata=doc['metadata'],
                score=doc['score']
            )
            for doc in search_results
        ]

    # Save assistant message
    assistant_message = MessageModel(
        conversation_id=conversation_id,
        role="assistant",
        content=answer,
        sources=json.dumps([s.dict() for s in sources]) if sources else None
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return QueryResponse(
        answer=answer,
        sources=sources,
        conversation_id=conversation_id,
        message_id=assistant_message.id
    )


@router.post("/stream")
async def query_knowledge_base_stream(
    query_req: QueryRequest,
    db: Session = Depends(get_db)
):
    """Query the knowledge base with streaming response."""
    # Check knowledge base exists
    kb = db.query(KnowledgeBaseModel).filter(
        KnowledgeBaseModel.id == query_req.knowledge_base_id
    ).first()
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {query_req.knowledge_base_id} not found"
        )

    # Get or create conversation
    conversation_id = query_req.conversation_id
    if conversation_id:
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
    else:
        # Create new conversation
        conversation = ConversationModel(
            knowledge_base_id=query_req.knowledge_base_id,
            title=query_req.question[:100]
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id

    # Save user message
    user_message = MessageModel(
        conversation_id=conversation_id,
        role="user",
        content=query_req.question
    )
    db.add(user_message)
    db.commit()

    # Retrieve relevant documents
    try:
        search_results = vector_store.search(
            knowledge_base_id=query_req.knowledge_base_id,
            query=query_req.question,
            top_k=query_req.top_k
        )
    except Exception as e:
        logger.error(f"Error searching vector store: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search knowledge base"
        )

    # Get conversation history
    conversation_history = []
    if conversation:
        messages = db.query(MessageModel).filter(
            MessageModel.conversation_id == conversation_id
        ).order_by(MessageModel.created_at).all()
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-10:]
        ]

    async def generate():
        """Stream generator."""
        try:
            # Send sources first
            sources_data = {
                "type": "sources",
                "data": [
                    {
                        "content": doc['content'],
                        "metadata": doc['metadata'],
                        "score": doc['score']
                    }
                    for doc in search_results
                ]
            }
            yield f"data: {json.dumps(sources_data)}\n\n"

            # Stream answer
            answer_parts = []
            async for chunk in llm_service.generate_answer(
                question=query_req.question,
                context_docs=search_results,
                conversation_history=conversation_history,
                stream=True
            ):
                answer_parts.append(chunk)
                chunk_data = {
                    "type": "chunk",
                    "data": chunk
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"

            # Save complete answer
            complete_answer = "".join(answer_parts)
            assistant_message = MessageModel(
                conversation_id=conversation_id,
                role="assistant",
                content=complete_answer,
                sources=json.dumps(sources_data["data"]) if search_results else None
            )
            db.add(assistant_message)
            db.commit()

            # Send completion
            done_data = {
                "type": "done",
                "data": {
                    "conversation_id": conversation_id,
                    "message_id": assistant_message.id
                }
            }
            yield f"data: {json.dumps(done_data)}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}")
            error_data = {
                "type": "error",
                "data": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
