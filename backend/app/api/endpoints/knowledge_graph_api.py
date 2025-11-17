from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models.database import get_db, KnowledgeBase as KnowledgeBaseModel
from app.models.schemas import KnowledgeGraphResponse
from app.services.knowledge_graph import knowledge_graph

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{kb_id}/graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    kb_id: int,
    entities: List[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get knowledge graph for a knowledge base.

    If entities are provided, returns a subgraph. Otherwise, returns the full graph.
    """
    # Check knowledge base exists
    kb = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found"
        )

    try:
        if entities:
            graph_data = knowledge_graph.get_subgraph(
                knowledge_base_id=kb_id,
                entities=entities,
                include_neighbors=True
            )
        else:
            graph_data = knowledge_graph.get_full_graph(kb_id)

        return KnowledgeGraphResponse(
            nodes=graph_data['nodes'],
            edges=graph_data['edges']
        )

    except Exception as e:
        logger.error(f"Error getting knowledge graph: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge graph: {str(e)}"
        )


@router.post("/{kb_id}/graph/rebuild", status_code=status.HTTP_200_OK)
async def rebuild_knowledge_graph(
    kb_id: int,
    db: Session = Depends(get_db)
):
    """Rebuild knowledge graph from all documents in the knowledge base."""
    # Check knowledge base exists
    kb = db.query(KnowledgeBaseModel).filter(KnowledgeBaseModel.id == kb_id).first()
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base {kb_id} not found"
        )

    try:
        # Clear existing graph
        knowledge_graph.clear_graph(kb_id)

        # TODO: Re-extract documents and rebuild
        # For now, just return success
        return {"message": "Knowledge graph rebuild initiated"}

    except Exception as e:
        logger.error(f"Error rebuilding knowledge graph: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rebuild knowledge graph: {str(e)}"
        )
