"""
Document database models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from datetime import datetime
import enum
from ..core.database import Base


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    HTML = "html"
    TXT = "txt"
    MD = "md"


class Document(Base):
    """Document metadata model"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(Enum(DocumentType), nullable=False)
    mime_type = Column(String(100))

    # Content metadata
    title = Column(String(255))
    content_preview = Column(Text)
    chunk_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Processing status
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename})>"
