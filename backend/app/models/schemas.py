from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Knowledge Base Schemas
class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    embedding_model: Optional[str] = None


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    embedding_model: str
    created_at: datetime
    updated_at: datetime
    document_count: int = 0

    class Config:
        from_attributes = True


# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    knowledge_base_id: int
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    error_message: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    status: str
    message: str


# Query Schemas
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    knowledge_base_id: int
    conversation_id: Optional[int] = None
    top_k: int = Field(default=5, ge=1, le=20)
    use_knowledge_graph: bool = False
    stream: bool = False


class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    conversation_id: int
    message_id: int


# Conversation Schemas
class ConversationCreate(BaseModel):
    knowledge_base_id: int
    title: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    knowledge_base_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse]


# Knowledge Graph Schemas
class KnowledgeGraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = {}


class KnowledgeGraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    properties: Dict[str, Any] = {}


class KnowledgeGraphResponse(BaseModel):
    nodes: List[KnowledgeGraphNode]
    edges: List[KnowledgeGraphEdge]


# Statistics
class StatisticsResponse(BaseModel):
    total_knowledge_bases: int
    total_documents: int
    total_conversations: int
    total_messages: int
