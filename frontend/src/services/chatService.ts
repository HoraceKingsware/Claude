/**
 * Chat service API calls with SSE support
 */
import apiClient from './api';
import type { ChatRequest, SSEEvent } from '@/types';

export const chatService = {
  /**
   * Chat with streaming response using Server-Sent Events
   */
  chatStream: async (
    request: ChatRequest,
    onEvent: (event: SSEEvent) => void,
    onError?: (error: Error) => void
  ): Promise<void> => {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const url = `${API_BASE_URL}/api/chat/stream`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Response body is null');
      }

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = line.slice(6); // Remove 'data: ' prefix
              const event: SSEEvent = JSON.parse(data);
              onEvent(event);
            } catch (e) {
              console.error('Failed to parse SSE event:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat stream error:', error);
      if (onError) {
        onError(error as Error);
      }
    }
  },

  /**
   * Chat without streaming (complete response)
   */
  chatMessage: async (
    request: ChatRequest
  ): Promise<{ message: string; response: string; model: string }> => {
    const response = await apiClient.post('/api/chat/message', request);
    return response.data;
  },

  /**
   * Get available models
   */
  getModels: async (): Promise<{ zhipu: string[]; anthropic: string[] }> => {
    const response = await apiClient.get('/api/chat/models');
    return response.data;
  },
};
