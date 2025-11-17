from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models.database import get_db, KnowledgeBase as KnowledgeBaseModel
from app.models.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse
)
from app.services.vector_store import vector_store

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    kb_create: KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):
    """Create a new knowledge base."""
    # Check if name already exists
    existing = db.query(KnowledgeBaseModel).filter(
        KnowledgeBaseModel.name == kb_create.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Knowledge base with name '{kb_create.name}' already exists"
        )

    # Create knowledge base
    kb = KnowledgeBaseModel(
        name=kb_create.name,
        description=kb_create.description,
        embedding_model=kb_create.embedding_model or KnowledgeBaseModel.embedding_model.default.arg
    )

    db.add(kb)
    db.commit()
    db.refresh(kb)

    # Create vector store collection
    try:
        vector_store.create_collection(kb.id)
    except Exception as e:
        logger.error(f"Error creating vector store collection: {str(e)}")
        db.delete(kb)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create vector store collection"
        )

    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        embedding_model=kb.embedding_model,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
        document_count=0
    )


@router.get("/", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all knowledge bases."""
    kbs = db.query(KnowledgeBaseModel).offset(skip).limit(limit).all()

    return [
        KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            embedding_model=kb.embedding_model,
            created_at=kb.created_at,
            updated_at=kb.updated_at,
            document_count=len(kb.documents)
        )
        for kb in kbs
    ]


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific knowledge base."""
    kb = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found"
        )

    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        embedding_model=kb.embedding_model,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
        document_count=len(kb.documents)
    )


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: int,
    kb_update: KnowledgeBaseUpdate,
    db: Session = Depends(get_db)
):
    """Update a knowledge base."""
    kb = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found"
        )

    # Update fields
    if kb_update.name is not None:
        # Check if new name conflicts
        existing = db.query(KnowledgeBaseModel).filter(
            KnowledgeBaseModel.name == kb_update.name,
            KnowledgeBaseModel.id != kb_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Knowledge base with name '{kb_update.name}' already exists"
            )
        kb.name = kb_update.name

    if kb_update.description is not None:
        kb.description = kb_update.description

    db.commit()
    db.refresh(kb)

    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        embedding_model=kb.embedding_model,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
        document_count=len(kb.documents)
    )


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db)
):
    """Delete a knowledge base."""
    kb = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found"
        )

    # Delete vector store collection
    try:
        vector_store.delete_collection(kb_id)
    except Exception as e:
        logger.warning(f"Error deleting vector store collection: {str(e)}")

    # Delete from database (cascades to documents)
    db.delete(kb)
    db.commit()

    return None
