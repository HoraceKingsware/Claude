/**
 * Zustand global state management
 */
import { create } from 'zustand';
import type { Document, ChatMessage } from '@/types';

interface AppState {
  // Documents
  documents: Document[];
  setDocuments: (documents: Document[]) => void;
  addDocument: (document: Document) => void;
  removeDocument: (id: number) => void;

  // Chat
  chatMessages: ChatMessage[];
  addChatMessage: (message: ChatMessage) => void;
  clearChatMessages: () => void;

  // UI State
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  currentTab: string;
  setCurrentTab: (tab: string) => void;

  // Settings
  useRAG: boolean;
  setUseRAG: (value: boolean) => void;
  topK: number;
  setTopK: (value: number) => void;
  selectedModel: string | undefined;
  setSelectedModel: (model: string | undefined) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Documents
  documents: [],
  setDocuments: (documents) => set({ documents }),
  addDocument: (document) =>
    set((state) => ({ documents: [...state.documents, document] })),
  removeDocument: (id) =>
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== id),
    })),

  // Chat
  chatMessages: [],
  addChatMessage: (message) =>
    set((state) => ({ chatMessages: [...state.chatMessages, message] })),
  clearChatMessages: () => set({ chatMessages: [] }),

  // UI State
  sidebarCollapsed: false,
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  currentTab: 'upload',
  setCurrentTab: (tab) => set({ currentTab: tab }),

  // Settings
  useRAG: true,
  setUseRAG: (value) => set({ useRAG: value }),
  topK: 5,
  setTopK: (value) => set({ topK: value }),
  selectedModel: undefined,
  setSelectedModel: (model) => set({ selectedModel: model }),
}));
