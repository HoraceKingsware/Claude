import logging
import re
import json
from typing import List, Dict, Any, Tuple, Optional
import networkx as nx
from collections import defaultdict

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """Extract and manage knowledge graph from documents."""

    def __init__(self):
        self.graphs: Dict[int, nx.DiGraph] = {}

    def get_graph(self, knowledge_base_id: int) -> nx.DiGraph:
        """Get or create graph for a knowledge base."""
        if knowledge_base_id not in self.graphs:
            self.graphs[knowledge_base_id] = nx.DiGraph()
        return self.graphs[knowledge_base_id]

    def extract_entities_simple(self, text: str) -> List[str]:
        """
        Simple entity extraction using capitalized words and common patterns.
        For production, consider using spaCy or other NER models.
        """
        # Find capitalized words (potential entities)
        entities = set()

        # Pattern for capitalized words
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.update(capitalized)

        # Pattern for acronyms
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        entities.update(acronyms)

        return list(entities)

    def extract_relationships_simple(
        self,
        text: str,
        entities: List[str]
    ) -> List[Tuple[str, str, str]]:
        """
        Simple relationship extraction using patterns.
        For production, consider using dependency parsing or relation extraction models.
        """
        relationships = []

        # Common relationship patterns
        patterns = [
            (r'(\w+)\s+is\s+a\s+(\w+)', 'is_a'),
            (r'(\w+)\s+has\s+(\w+)', 'has'),
            (r'(\w+)\s+uses\s+(\w+)', 'uses'),
            (r'(\w+)\s+contains\s+(\w+)', 'contains'),
            (r'(\w+)\s+belongs\s+to\s+(\w+)', 'belongs_to'),
            (r'(\w+)\s+requires\s+(\w+)', 'requires'),
            (r'(\w+)\s+provides\s+(\w+)', 'provides'),
        ]

        for pattern, rel_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                source, target = match.groups()
                # Check if entities are in our extracted entities
                if source in entities and target in entities:
                    relationships.append((source, target, rel_type))

        return relationships

    def build_from_documents(
        self,
        knowledge_base_id: int,
        documents: List[Dict[str, Any]]
    ) -> None:
        """
        Build knowledge graph from documents.

        Args:
            knowledge_base_id: ID of the knowledge base
            documents: List of documents with content and metadata
        """
        graph = self.get_graph(knowledge_base_id)

        for doc in documents:
            content = doc.get('content', '')
            doc_id = doc.get('metadata', {}).get('document_id')

            # Extract entities
            entities = self.extract_entities_simple(content)

            # Add entities as nodes
            for entity in entities:
                if not graph.has_node(entity):
                    graph.add_node(
                        entity,
                        type='entity',
                        documents=[doc_id],
                        frequency=1
                    )
                else:
                    # Update existing node
                    node_data = graph.nodes[entity]
                    if doc_id not in node_data.get('documents', []):
                        node_data['documents'].append(doc_id)
                    node_data['frequency'] = node_data.get('frequency', 0) + 1

            # Extract relationships
            relationships = self.extract_relationships_simple(content, entities)

            # Add relationships as edges
            for source, target, rel_type in relationships:
                if graph.has_edge(source, target):
                    # Increment edge weight
                    graph[source][target]['weight'] = graph[source][target].get('weight', 0) + 1
                else:
                    graph.add_edge(
                        source,
                        target,
                        relationship=rel_type,
                        weight=1,
                        documents=[doc_id]
                    )

        logger.info(
            f"Knowledge graph built for KB {knowledge_base_id}: "
            f"{graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges"
        )

    def get_related_entities(
        self,
        knowledge_base_id: int,
        entity: str,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """Get entities related to a given entity within max_depth."""
        graph = self.get_graph(knowledge_base_id)

        if entity not in graph:
            return []

        related = []
        visited = {entity}

        def dfs(node: str, depth: int):
            if depth > max_depth:
                return

            for neighbor in graph.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    edge_data = graph[node][neighbor]
                    related.append({
                        'entity': neighbor,
                        'relationship': edge_data.get('relationship'),
                        'depth': depth,
                        'weight': edge_data.get('weight', 1)
                    })
                    dfs(neighbor, depth + 1)

        dfs(entity, 1)
        return related

    def get_subgraph(
        self,
        knowledge_base_id: int,
        entities: List[str],
        include_neighbors: bool = True
    ) -> Dict[str, Any]:
        """
        Get subgraph containing specified entities.

        Returns:
            Dictionary with nodes and edges for visualization
        """
        graph = self.get_graph(knowledge_base_id)

        nodes_to_include = set(entities)

        # Include neighbors if requested
        if include_neighbors:
            for entity in entities:
                if entity in graph:
                    nodes_to_include.update(graph.neighbors(entity))
                    nodes_to_include.update(graph.predecessors(entity))

        # Build subgraph
        subgraph = graph.subgraph(nodes_to_include)

        # Format for frontend
        nodes = [
            {
                'id': node,
                'label': node,
                'type': graph.nodes[node].get('type', 'entity'),
                'properties': {
                    'frequency': graph.nodes[node].get('frequency', 1),
                    'documents': graph.nodes[node].get('documents', [])
                }
            }
            for node in subgraph.nodes()
        ]

        edges = [
            {
                'source': source,
                'target': target,
                'relationship': graph[source][target].get('relationship', 'related_to'),
                'properties': {
                    'weight': graph[source][target].get('weight', 1)
                }
            }
            for source, target in subgraph.edges()
        ]

        return {
            'nodes': nodes,
            'edges': edges
        }

    def get_full_graph(self, knowledge_base_id: int) -> Dict[str, Any]:
        """Get the full knowledge graph."""
        graph = self.get_graph(knowledge_base_id)

        nodes = [
            {
                'id': node,
                'label': node,
                'type': graph.nodes[node].get('type', 'entity'),
                'properties': {
                    'frequency': graph.nodes[node].get('frequency', 1),
                    'documents': graph.nodes[node].get('documents', [])
                }
            }
            for node in graph.nodes()
        ]

        edges = [
            {
                'source': source,
                'target': target,
                'relationship': graph[source][target].get('relationship', 'related_to'),
                'properties': {
                    'weight': graph[source][target].get('weight', 1)
                }
            }
            for source, target in graph.edges()
        ]

        return {
            'nodes': nodes,
            'edges': edges
        }

    def clear_graph(self, knowledge_base_id: int) -> None:
        """Clear the knowledge graph for a knowledge base."""
        if knowledge_base_id in self.graphs:
            del self.graphs[knowledge_base_id]
            logger.info(f"Cleared knowledge graph for KB {knowledge_base_id}")


# Global instance
knowledge_graph = KnowledgeGraph()
