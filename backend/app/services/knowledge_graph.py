"""
Knowledge graph service using NetworkX
"""
import networkx as nx
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class KnowledgeGraph:
    """Knowledge graph operations using NetworkX"""

    def __init__(self, persist_path: str = "./knowledge_graph.json"):
        self.graph = nx.DiGraph()
        self.persist_path = persist_path
        self._load_graph()

    def _load_graph(self):
        """Load graph from JSON file"""
        if Path(self.persist_path).exists():
            try:
                with open(self.persist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
            except Exception as e:
                print(f"Failed to load graph: {e}")
                self.graph = nx.DiGraph()

    def _save_graph(self):
        """Save graph to JSON file"""
        try:
            data = nx.node_link_data(self.graph)
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save graph: {e}")

    def add_node(
        self,
        node_id: str,
        label: str,
        node_type: str = "entity",
        **properties
    ):
        """
        Add node to graph

        Args:
            node_id: Unique node identifier
            label: Node label/name
            node_type: Type of node (entity, concept, document, etc.)
            **properties: Additional node properties
        """
        self.graph.add_node(
            node_id,
            label=label,
            type=node_type,
            **properties
        )
        self._save_graph()

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        weight: float = 1.0,
        **properties
    ):
        """
        Add edge between nodes

        Args:
            source: Source node ID
            target: Target node ID
            relation: Relationship type
            weight: Edge weight
            **properties: Additional edge properties
        """
        self.graph.add_edge(
            source,
            target,
            relation=relation,
            weight=weight,
            **properties
        )
        self._save_graph()

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID"""
        if self.graph.has_node(node_id):
            data = self.graph.nodes[node_id].copy()
            data['id'] = node_id
            return data
        return None

    def get_neighbors(
        self,
        node_id: str,
        max_depth: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get neighboring nodes

        Args:
            node_id: Source node ID
            max_depth: Maximum depth to traverse

        Returns:
            List of neighbor nodes
        """
        if not self.graph.has_node(node_id):
            return []

        neighbors = []
        visited = set()

        def traverse(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)

            for neighbor in self.graph.neighbors(current_id):
                if neighbor not in visited:
                    node_data = self.graph.nodes[neighbor].copy()
                    node_data['id'] = neighbor
                    neighbors.append(node_data)
                    traverse(neighbor, depth + 1)

        traverse(node_id, 0)
        return neighbors

    def search_nodes(
        self,
        query: str,
        node_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search nodes by label

        Args:
            query: Search query
            node_type: Filter by node type
            limit: Maximum results

        Returns:
            List of matching nodes
        """
        results = []
        query_lower = query.lower()

        for node_id, data in self.graph.nodes(data=True):
            if node_type and data.get('type') != node_type:
                continue

            label = data.get('label', '').lower()
            if query_lower in label:
                node_data = data.copy()
                node_data['id'] = node_id
                results.append(node_data)

                if len(results) >= limit:
                    break

        return results

    def get_subgraph(
        self,
        node_ids: List[str],
        include_neighbors: bool = False
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Get subgraph containing specified nodes

        Args:
            node_ids: List of node IDs
            include_neighbors: Whether to include direct neighbors

        Returns:
            Tuple of (nodes, edges)
        """
        if include_neighbors:
            expanded_nodes = set(node_ids)
            for node_id in node_ids:
                if self.graph.has_node(node_id):
                    expanded_nodes.update(self.graph.neighbors(node_id))
                    expanded_nodes.update(self.graph.predecessors(node_id))
            node_ids = list(expanded_nodes)

        # Get nodes
        nodes = []
        for node_id in node_ids:
            if self.graph.has_node(node_id):
                node_data = self.graph.nodes[node_id].copy()
                node_data['id'] = node_id
                nodes.append(node_data)

        # Get edges
        edges = []
        subgraph = self.graph.subgraph(node_ids)
        for source, target, data in subgraph.edges(data=True):
            edge_data = data.copy()
            edge_data['source'] = source
            edge_data['target'] = target
            edges.append(edge_data)

        return nodes, edges

    def get_all_graph(self) -> Tuple[List[Dict], List[Dict]]:
        """Get entire graph"""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            node_data = data.copy()
            node_data['id'] = node_id
            nodes.append(node_data)

        edges = []
        for source, target, data in self.graph.edges(data=True):
            edge_data = data.copy()
            edge_data['source'] = source
            edge_data['target'] = target
            edges.append(edge_data)

        return nodes, edges

    def delete_node(self, node_id: str):
        """Delete node and its edges"""
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)
            self._save_graph()

    def clear(self):
        """Clear entire graph"""
        self.graph.clear()
        self._save_graph()

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "is_directed": self.graph.is_directed(),
            "density": nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0
        }

    def add_document_entities(
        self,
        document_id: int,
        entities: List[Dict[str, str]]
    ):
        """
        Add entities extracted from a document

        Args:
            document_id: Document ID
            entities: List of entities with 'text', 'type', etc.
        """
        doc_node_id = f"doc_{document_id}"

        # Add document node if not exists
        if not self.graph.has_node(doc_node_id):
            self.add_node(
                doc_node_id,
                label=f"Document {document_id}",
                node_type="document",
                document_id=document_id
            )

        # Add entity nodes and connect to document
        for i, entity in enumerate(entities):
            entity_id = f"entity_{document_id}_{i}"
            entity_text = entity.get('text', '')
            entity_type = entity.get('type', 'entity')

            self.add_node(
                entity_id,
                label=entity_text,
                node_type=entity_type,
                **entity
            )

            self.add_edge(
                doc_node_id,
                entity_id,
                relation="contains",
                weight=1.0
            )
