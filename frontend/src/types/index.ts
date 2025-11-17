export interface KnowledgeBase {
  id: number;
  name: string;
  description: string | null;
  embedding_model: string;
  created_at: string;
  updated_at: string;
  document_count: number;
}

export interface Document {
  id: number;
  knowledge_base_id: number;
  filename: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message: string | null;
  created_at: string;
  processed_at: string | null;
}

export interface Conversation {
  id: number;
  knowledge_base_id: number;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: SourceDocument[];
  created_at: string;
}

export interface SourceDocument {
  content: string;
  metadata: Record<string, any>;
  score: number;
}

export interface QueryRequest {
  question: string;
  knowledge_base_id: number;
  conversation_id?: number;
  top_k?: number;
  use_knowledge_graph?: boolean;
  stream?: boolean;
}

export interface QueryResponse {
  answer: string;
  sources: SourceDocument[];
  conversation_id: number;
  message_id: number;
}

export interface KnowledgeGraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, any>;
}

export interface KnowledgeGraphEdge {
  source: string;
  target: string;
  relationship: string;
  properties: Record<string, any>;
}

export interface KnowledgeGraph {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}
