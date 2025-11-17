/**
 * Vector search service API calls
 */
import apiClient from './api';
import type { VectorSearchRequest, VectorSearchResponse } from '@/types';

export const vectorService = {
  /**
   * Search vectors
   */
  search: async (request: VectorSearchRequest): Promise<VectorSearchResponse> => {
    const response = await apiClient.post<VectorSearchResponse>(
      '/api/vectors/search',
      request
    );
    return response.data;
  },

  /**
   * Get vector store statistics
   */
  getStats: async (): Promise<{ total_chunks: number; collection_name: string }> => {
    const response = await apiClient.get('/api/vectors/stats');
    return response.data;
  },

  /**
   * Clear all vectors
   */
  clear: async (): Promise<void> => {
    await apiClient.delete('/api/vectors/clear');
  },
};
