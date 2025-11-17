from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import logging
import aiofiles
from datetime import datetime

from app.models.database import (
    get_db,
    KnowledgeBase as KnowledgeBaseModel,
    Document as DocumentModel
)
from app.models.schemas import DocumentResponse, DocumentUploadResponse
from app.services.document_parser import DocumentParser, TextChunker
from app.services.vector_store import vector_store
from app.services.knowledge_graph import knowledge_graph
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

document_parser = DocumentParser()
text_chunker = TextChunker()


@router.post("/{kb_id}/upload", response_model=DocumentUploadResponse)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document."""
    # Check knowledge base exists
    kb = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found"
        )

    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )

    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.txt', '.md', '.markdown', '.html', '.htm']
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not supported. Allowed types: {', '.join(allowed_extensions)}"
        )

    # Save file
    kb_upload_dir = os.path.join(settings.UPLOAD_DIR, f"kb_{kb_id}")
    os.makedirs(kb_upload_dir, exist_ok=True)

    file_path = os.path.join(kb_upload_dir, file.filename)

    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )

    # Create document record
    document = DocumentModel(
        knowledge_base_id=kb_id,
        filename=file.filename,
        file_path=file_path,
        file_type=file_ext,
        file_size=file_size,
        status="processing"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Process document asynchronously
    try:
        # Parse document
        text_content = document_parser.parse(file_path)

        # Chunk text
        chunks = text_chunker.chunk_text(
            text_content,
            metadata={
                'filename': file.filename,
                'document_id': document.id,
                'file_type': file_ext
            }
        )

        # Add to vector store
        chunk_count = vector_store.add_documents(kb_id, document.id, chunks)

        # Update knowledge graph if enabled
        if settings.ENABLE_KNOWLEDGE_GRAPH:
            try:
                knowledge_graph.build_from_documents(kb_id, chunks)
            except Exception as e:
                logger.warning(f"Error building knowledge graph: {str(e)}")

        # Update document status
        document.status = "completed"
        document.chunk_count = chunk_count
        document.processed_at = datetime.utcnow()

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        document.status = "failed"
        document.error_message = str(e)

    db.commit()

    return DocumentUploadResponse(
        document_id=document.id,
        filename=document.filename,
        status=document.status,
        message="Document processed successfully" if document.status == "completed" else f"Processing failed: {document.error_message}"
    )


@router.get("/{kb_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    kb_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List documents in a knowledge base."""
    # Check knowledge base exists
    kb = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found"
        )

    documents = db.query(DocumentModel).filter(
        DocumentModel.knowledge_base_id == kb_id
    ).offset(skip).limit(limit).all()

    return documents


@router.delete("/{kb_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    kb_id: int,
    doc_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document."""
    document = db.query(DocumentModel).filter(
        DocumentModel.id == doc_id,
        DocumentModel.knowledge_base_id == kb_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found in knowledge base {kb_id}"
        )

    # Delete from vector store
    try:
        vector_store.delete_document(kb_id, doc_id)
    except Exception as e:
        logger.warning(f"Error deleting from vector store: {str(e)}")

    # Delete file
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        logger.warning(f"Error deleting file: {str(e)}")

    # Delete from database
    db.delete(document)
    db.commit()

    return None
