from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
import logging

from app.models.database import (
    get_db,
    Conversation as ConversationModel,
    Message as MessageModel
)
from app.models.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conv_create: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    conversation = ConversationModel(
        knowledge_base_id=conv_create.knowledge_base_id,
        title=conv_create.title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return ConversationResponse(
        id=conversation.id,
        knowledge_base_id=conversation.knowledge_base_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=0
    )


@router.get("/{kb_id}/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    kb_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List conversations for a knowledge base."""
    conversations = db.query(ConversationModel).filter(
        ConversationModel.knowledge_base_id == kb_id
    ).order_by(ConversationModel.updated_at.desc()).offset(skip).limit(limit).all()

    return [
        ConversationResponse(
            id=conv.id,
            knowledge_base_id=conv.knowledge_base_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages)
        )
        for conv in conversations
    ]


@router.get("/conversations/{conv_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conv_id: int,
    db: Session = Depends(get_db)
):
    """Get conversation details with messages."""
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conv_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conv_id} not found"
        )

    messages = db.query(MessageModel).filter(
        MessageModel.conversation_id == conv_id
    ).order_by(MessageModel.created_at).all()

    message_responses = []
    for msg in messages:
        sources = None
        if msg.sources:
            try:
                sources = json.loads(msg.sources)
            except:
                pass

        message_responses.append(
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                sources=sources,
                created_at=msg.created_at
            )
        )

    return ConversationDetailResponse(
        id=conversation.id,
        knowledge_base_id=conversation.knowledge_base_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=len(messages),
        messages=message_responses
    )


@router.delete("/conversations/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conv_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation."""
    conversation = db.query(ConversationModel).filter(
        ConversationModel.id == conv_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conv_id} not found"
        )

    db.delete(conversation)
    db.commit()

    return None
