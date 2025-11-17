import axios from 'axios';
import type {
  KnowledgeBase,
  Document,
  Conversation,
  Message,
  QueryRequest,
  QueryResponse,
  KnowledgeGraph,
} from '@/types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Knowledge Base APIs
export const knowledgeBaseAPI = {
  list: async (): Promise<KnowledgeBase[]> => {
    const response = await api.get('/knowledge-bases/');
    return response.data;
  },

  get: async (id: number): Promise<KnowledgeBase> => {
    const response = await api.get(`/knowledge-bases/${id}`);
    return response.data;
  },

  create: async (data: { name: string; description?: string }): Promise<KnowledgeBase> => {
    const response = await api.post('/knowledge-bases/', data);
    return response.data;
  },

  update: async (id: number, data: { name?: string; description?: string }): Promise<KnowledgeBase> => {
    const response = await api.put(`/knowledge-bases/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/knowledge-bases/${id}`);
  },
};

// Document APIs
export const documentAPI = {
  list: async (knowledgeBaseId: number): Promise<Document[]> => {
    const response = await api.get(`/knowledge-bases/${knowledgeBaseId}/documents`);
    return response.data;
  },

  upload: async (knowledgeBaseId: number, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post(
      `/knowledge-bases/${knowledgeBaseId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  delete: async (knowledgeBaseId: number, documentId: number): Promise<void> => {
    await api.delete(`/knowledge-bases/${knowledgeBaseId}/documents/${documentId}`);
  },
};

// Query APIs
export const queryAPI = {
  query: async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await api.post('/query/', request);
    return response.data;
  },

  queryStream: async (
    request: QueryRequest,
    onChunk: (chunk: any) => void,
    onDone: (data: any) => void,
    onError: (error: string) => void
  ): Promise<void> => {
    const response = await fetch('/api/query/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('Failed to query');
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No reader available');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));

            switch (data.type) {
              case 'sources':
                onChunk({ type: 'sources', data: data.data });
                break;
              case 'chunk':
                onChunk({ type: 'chunk', data: data.data });
                break;
              case 'done':
                onDone(data.data);
                break;
              case 'error':
                onError(data.data);
                break;
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e);
          }
        }
      }
    }
  },
};

// Conversation APIs
export const conversationAPI = {
  list: async (knowledgeBaseId: number): Promise<Conversation[]> => {
    const response = await api.get(`/knowledge-bases/${knowledgeBaseId}/conversations`);
    return response.data;
  },

  get: async (conversationId: number): Promise<Conversation & { messages: Message[] }> => {
    const response = await api.get(`/knowledge-bases/conversations/${conversationId}`);
    return response.data;
  },

  create: async (data: { knowledge_base_id: number; title?: string }): Promise<Conversation> => {
    const response = await api.post('/knowledge-bases/', data);
    return response.data;
  },

  delete: async (conversationId: number): Promise<void> => {
    await api.delete(`/knowledge-bases/conversations/${conversationId}`);
  },
};

// Knowledge Graph APIs
export const knowledgeGraphAPI = {
  get: async (knowledgeBaseId: number, entities?: string[]): Promise<KnowledgeGraph> => {
    const params = entities ? { entities: entities.join(',') } : {};
    const response = await api.get(`/knowledge-bases/${knowledgeBaseId}/graph`, { params });
    return response.data;
  },

  rebuild: async (knowledgeBaseId: number): Promise<any> => {
    const response = await api.post(`/knowledge-bases/${knowledgeBaseId}/graph/rebuild`);
    return response.data;
  },
};

export default api;
