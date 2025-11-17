/**
 * Document service API calls
 */
import apiClient from './api';
import type { Document, DocumentList } from '@/types';

export const documentService = {
  /**
   * Upload a document
   */
  upload: async (file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<Document>('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Get all documents
   */
  list: async (skip = 0, limit = 100): Promise<DocumentList> => {
    const response = await apiClient.get<DocumentList>('/api/documents/', {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Get document by ID
   */
  get: async (id: number): Promise<Document> => {
    const response = await apiClient.get<Document>(`/api/documents/${id}`);
    return response.data;
  },

  /**
   * Update document
   */
  update: async (id: number, data: Partial<Document>): Promise<Document> => {
    const response = await apiClient.put<Document>(`/api/documents/${id}`, data);
    return response.data;
  },

  /**
   * Delete document
   */
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/documents/${id}`);
  },
};
