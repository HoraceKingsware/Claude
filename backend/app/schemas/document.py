"""
Document Pydantic schemas for API validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentBase(BaseModel):
    """Base document schema"""
    filename: str
    title: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Document creation schema"""
    pass


class DocumentUpdate(BaseModel):
    """Document update schema"""
    title: Optional[str] = None
    status: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Document response schema"""
    id: int
    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    mime_type: Optional[str]
    content_preview: Optional[str]
    chunk_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str]

    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """Document list response"""
    total: int
    documents: list[DocumentResponse]


class VectorSearchRequest(BaseModel):
    """Vector search request"""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class VectorSearchResult(BaseModel):
    """Vector search result item"""
    document_id: int
    filename: str
    content: str
    score: float
    metadata: dict


class VectorSearchResponse(BaseModel):
    """Vector search response"""
    query: str
    results: list[VectorSearchResult]
    total: int


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., min_length=1, max_length=2000)
    use_rag: bool = Field(default=True)
    top_k: int = Field(default=5, ge=1, le=20)
    model: Optional[str] = None


class ChatMessage(BaseModel):
    """Chat message schema"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GraphNode(BaseModel):
    """Knowledge graph node"""
    id: str
    label: str
    type: str
    properties: dict = {}


class GraphEdge(BaseModel):
    """Knowledge graph edge"""
    source: str
    target: str
    relation: str
    weight: float = 1.0


class GraphResponse(BaseModel):
    """Knowledge graph response"""
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    total_nodes: int
    total_edges: int
