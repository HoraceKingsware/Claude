from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.models.database import init_db
from app.api.endpoints import (
    knowledge_base,
    documents,
    query,
    conversations,
    knowledge_graph_api
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Knowledge Base RAG API with Vector Search and Knowledge Graph"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Application started successfully")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(
    knowledge_base.router,
    prefix="/api/knowledge-bases",
    tags=["Knowledge Bases"]
)

app.include_router(
    documents.router,
    prefix="/api/knowledge-bases",
    tags=["Documents"]
)

app.include_router(
    query.router,
    prefix="/api/query",
    tags=["Query"]
)

app.include_router(
    conversations.router,
    prefix="/api/knowledge-bases",
    tags=["Conversations"]
)

app.include_router(
    knowledge_graph_api.router,
    prefix="/api/knowledge-bases",
    tags=["Knowledge Graph"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
