"""
Vector search API routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.document import Document
from ...schemas.document import VectorSearchRequest, VectorSearchResponse, VectorSearchResult
from ...services.vector_store import VectorStore

router = APIRouter(prefix="/api/vectors", tags=["vectors"])

# Initialize vector store
vector_store = VectorStore()


@router.post("/search", response_model=VectorSearchResponse)
async def search_vectors(
    request: VectorSearchRequest,
    db: Session = Depends(get_db)
):
    """Search for similar document chunks using vector similarity"""

    try:
        # Perform vector search
        results = vector_store.search(
            query=request.query,
            top_k=request.top_k
        )

        # Filter by threshold and format results
        formatted_results = []
        for result in results:
            score = result.get('score', 0)
            if score >= request.threshold:
                metadata = result.get('metadata', {})
                document_id = metadata.get('document_id')

                # Get document info from database
                document = None
                filename = metadata.get('filename', 'Unknown')
                if document_id:
                    document = db.query(Document).filter(
                        Document.id == document_id
                    ).first()
                    if document:
                        filename = document.original_filename

                formatted_results.append(
                    VectorSearchResult(
                        document_id=document_id or 0,
                        filename=filename,
                        content=result.get('document', ''),
                        score=score,
                        metadata=metadata
                    )
                )

        return VectorSearchResponse(
            query=request.query,
            results=formatted_results,
            total=len(formatted_results)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector search failed: {str(e)}"
        )


@router.get("/stats")
async def get_vector_stats():
    """Get vector store statistics"""
    try:
        stats = vector_store.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_vectors():
    """Clear all vectors from the store (use with caution)"""
    try:
        vector_store.clear()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear vectors: {str(e)}"
        )
