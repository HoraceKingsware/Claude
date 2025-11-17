/**
 * Knowledge graph service API calls
 */
import apiClient from './api';
import type { GraphResponse, GraphNode, GraphEdge } from '@/types';

export const graphService = {
  /**
   * Get knowledge graph
   */
  getGraph: async (nodeIds?: string[], includeNeighbors = false): Promise<GraphResponse> => {
    const params: any = {};
    if (nodeIds && nodeIds.length > 0) {
      params.node_ids = nodeIds.join(',');
    }
    if (includeNeighbors) {
      params.include_neighbors = true;
    }

    const response = await apiClient.get<GraphResponse>('/api/graph/', { params });
    return response.data;
  },

  /**
   * Create a node
   */
  createNode: async (node: {
    node_id: string;
    label: string;
    node_type: string;
    properties?: Record<string, any>;
  }): Promise<{ status: string; node_id: string }> => {
    const response = await apiClient.post('/api/graph/nodes', node);
    return response.data;
  },

  /**
   * Create an edge
   */
  createEdge: async (edge: {
    source: string;
    target: string;
    relation: string;
    weight?: number;
    properties?: Record<string, any>;
  }): Promise<{ status: string; edge: string }> => {
    const response = await apiClient.post('/api/graph/edges', edge);
    return response.data;
  },

  /**
   * Get node by ID
   */
  getNode: async (nodeId: string): Promise<GraphNode> => {
    const response = await apiClient.get<GraphNode>(`/api/graph/nodes/${nodeId}`);
    return response.data;
  },

  /**
   * Get node neighbors
   */
  getNeighbors: async (
    nodeId: string,
    maxDepth = 1
  ): Promise<{ node_id: string; neighbors: GraphNode[] }> => {
    const response = await apiClient.get(`/api/graph/nodes/${nodeId}/neighbors`, {
      params: { max_depth: maxDepth },
    });
    return response.data;
  },

  /**
   * Search nodes
   */
  searchNodes: async (
    query: string,
    nodeType?: string,
    limit = 10
  ): Promise<{ query: string; results: GraphNode[] }> => {
    const response = await apiClient.get('/api/graph/search', {
      params: { query, node_type: nodeType, limit },
    });
    return response.data;
  },

  /**
   * Get graph statistics
   */
  getStats: async (): Promise<{
    total_nodes: number;
    total_edges: number;
    is_directed: boolean;
    density: number;
  }> => {
    const response = await apiClient.get('/api/graph/stats');
    return response.data;
  },

  /**
   * Delete a node
   */
  deleteNode: async (nodeId: string): Promise<void> => {
    await apiClient.delete(`/api/graph/nodes/${nodeId}`);
  },

  /**
   * Clear entire graph
   */
  clear: async (): Promise<void> => {
    await apiClient.delete('/api/graph/clear');
  },
};
