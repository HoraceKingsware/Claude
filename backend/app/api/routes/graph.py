"""
Knowledge graph API routes
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from ...schemas.document import GraphNode, GraphEdge, GraphResponse
from ...services.knowledge_graph import KnowledgeGraph

router = APIRouter(prefix="/api/graph", tags=["graph"])

# Initialize knowledge graph
kg = KnowledgeGraph()


class NodeCreate(BaseModel):
    """Node creation request"""
    node_id: str
    label: str
    node_type: str = "entity"
    properties: dict = {}


class EdgeCreate(BaseModel):
    """Edge creation request"""
    source: str
    target: str
    relation: str
    weight: float = 1.0
    properties: dict = {}


@router.get("/", response_model=GraphResponse)
async def get_graph(
    node_ids: Optional[str] = None,
    include_neighbors: bool = False
):
    """
    Get knowledge graph

    Args:
        node_ids: Comma-separated node IDs (optional, returns all if not provided)
        include_neighbors: Include direct neighbors of specified nodes
    """
    try:
        if node_ids:
            # Get subgraph
            node_id_list = [nid.strip() for nid in node_ids.split(',')]
            nodes, edges = kg.get_subgraph(node_id_list, include_neighbors)
        else:
            # Get entire graph
            nodes, edges = kg.get_all_graph()

        # Convert to response format
        graph_nodes = [
            GraphNode(
                id=node['id'],
                label=node.get('label', ''),
                type=node.get('type', 'entity'),
                properties={k: v for k, v in node.items() if k not in ['id', 'label', 'type']}
            )
            for node in nodes
        ]

        graph_edges = [
            GraphEdge(
                source=edge['source'],
                target=edge['target'],
                relation=edge.get('relation', 'related'),
                weight=edge.get('weight', 1.0)
            )
            for edge in edges
        ]

        return GraphResponse(
            nodes=graph_nodes,
            edges=graph_edges,
            total_nodes=len(graph_nodes),
            total_edges=len(graph_edges)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph: {str(e)}"
        )


@router.post("/nodes", status_code=status.HTTP_201_CREATED)
async def create_node(node: NodeCreate):
    """Create a new node in the graph"""
    try:
        kg.add_node(
            node_id=node.node_id,
            label=node.label,
            node_type=node.node_type,
            **node.properties
        )
        return {"status": "success", "node_id": node.node_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create node: {str(e)}"
        )


@router.post("/edges", status_code=status.HTTP_201_CREATED)
async def create_edge(edge: EdgeCreate):
    """Create a new edge in the graph"""
    try:
        kg.add_edge(
            source=edge.source,
            target=edge.target,
            relation=edge.relation,
            weight=edge.weight,
            **edge.properties
        )
        return {
            "status": "success",
            "edge": f"{edge.source} -> {edge.target}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create edge: {str(e)}"
        )


@router.get("/nodes/{node_id}")
async def get_node(node_id: str):
    """Get node by ID"""
    try:
        node = kg.get_node(node_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )
        return node
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get node: {str(e)}"
        )


@router.get("/nodes/{node_id}/neighbors")
async def get_neighbors(node_id: str, max_depth: int = 1):
    """Get neighboring nodes"""
    try:
        neighbors = kg.get_neighbors(node_id, max_depth)
        return {"node_id": node_id, "neighbors": neighbors}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get neighbors: {str(e)}"
        )


@router.get("/search")
async def search_nodes(
    query: str,
    node_type: Optional[str] = None,
    limit: int = 10
):
    """Search nodes by label"""
    try:
        results = kg.search_nodes(query, node_type, limit)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search nodes: {str(e)}"
        )


@router.get("/stats")
async def get_stats():
    """Get graph statistics"""
    try:
        stats = kg.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.delete("/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(node_id: str):
    """Delete a node"""
    try:
        kg.delete_node(node_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete node: {str(e)}"
        )


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_graph():
    """Clear entire graph (use with caution)"""
    try:
        kg.clear()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear graph: {str(e)}"
        )
