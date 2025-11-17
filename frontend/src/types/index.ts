/**
 * Type definitions for the RAG Knowledge System
 */

export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  file_type: string;
  mime_type?: string;
  title?: string;
  content_preview?: string;
  chunk_count: number;
  status: 'uploaded' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentList {
  total: number;
  documents: Document[];
}

export interface VectorSearchRequest {
  query: string;
  top_k?: number;
  threshold?: number;
}

export interface VectorSearchResult {
  document_id: number;
  filename: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
}

export interface VectorSearchResponse {
  query: string;
  results: VectorSearchResult[];
  total: number;
}

export interface ChatRequest {
  message: string;
  use_rag?: boolean;
  top_k?: number;
  model?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
  weight?: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_nodes: number;
  total_edges: number;
}

export interface SSEEvent {
  type: 'retrieval' | 'text' | 'done' | 'error';
  data: any;
}

export interface RetrievalData {
  count: number;
  documents: Array<{
    filename: string;
    score: number;
    preview: string;
  }>;
}
