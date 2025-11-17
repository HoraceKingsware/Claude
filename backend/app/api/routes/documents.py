"""
Document API routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path
from datetime import datetime

from ...core.database import get_db
from ...core.config import settings
from ...models.document import Document, DocumentType
from ...schemas.document import DocumentResponse, DocumentList, DocumentUpdate
from ...services.document_parser import DocumentParser
from ...services.vector_store import VectorStore

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Initialize services
vector_store = VectorStore()


def get_file_type(filename: str) -> DocumentType:
    """Get document type from filename"""
    ext = Path(filename).suffix.lower()
    type_mapping = {
        '.pdf': DocumentType.PDF,
        '.docx': DocumentType.DOCX,
        '.xlsx': DocumentType.XLSX,
        '.xls': DocumentType.XLSX,
        '.pptx': DocumentType.PPTX,
        '.html': DocumentType.HTML,
        '.htm': DocumentType.HTML,
        '.txt': DocumentType.TXT,
        '.md': DocumentType.MD,
    }
    return type_mapping.get(ext)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # Create upload directory if not exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Get file stats
    file_size = os.path.getsize(file_path)
    file_type = get_file_type(file.filename)

    # Create database record
    db_document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        mime_type=file.content_type,
        status="processing"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Process document
    try:
        # Parse document
        content = DocumentParser.parse(file_path, file_type.value)
        preview = DocumentParser.get_preview(content)

        # Add to vector store
        chunk_count = vector_store.add_document(
            document_id=db_document.id,
            content=content,
            metadata={
                "filename": file.filename,
                "file_type": file_type.value,
                "upload_date": db_document.created_at.isoformat()
            }
        )

        # Update database record
        db_document.content_preview = preview
        db_document.chunk_count = chunk_count
        db_document.status = "completed"
        db.commit()
        db.refresh(db_document)

    except Exception as e:
        db_document.status = "failed"
        db_document.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )

    return db_document


@router.get("/", response_model=DocumentList)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all documents"""
    total = db.query(Document).count()
    documents = db.query(Document).offset(skip).limit(limit).all()
    return DocumentList(total=total, documents=documents)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    update_data: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update document metadata"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(document, field, value)

    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete from vector store
    try:
        vector_store.delete_document(document_id)
    except Exception as e:
        print(f"Warning: Failed to delete from vector store: {e}")

    # Delete file
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        print(f"Warning: Failed to delete file: {e}")

    # Delete from database
    db.delete(document)
    db.commit()
