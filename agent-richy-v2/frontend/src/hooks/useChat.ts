/* ── Chat state management + API calls ───────────────────────────────── */

import { create } from 'zustand';
import type { ChatMessage, StructuredResponse, AgentKey } from '@/lib/types';
import { streamChatMessage } from '@/lib/api';

interface ChatStore {
  messages: ChatMessage[];
  activeAgent: AgentKey;
  isLoading: boolean;
  streamingContent: string;

  setActiveAgent: (agent: AgentKey) => void;
  sendMessage: (text: string, sessionId?: string) => Promise<void>;
  clearMessages: () => void;
}

let messageCounter = 0;

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  activeAgent: 'coach_richy',
  isLoading: false,
  streamingContent: '',

  setActiveAgent: (agent) => set({ activeAgent: agent }),

  sendMessage: async (text: string, sessionId = 'default') => {
    const userMsg: ChatMessage = {
      id: `msg_${++messageCounter}`,
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };

    set((state) => ({
      messages: [...state.messages, userMsg],
      isLoading: true,
      streamingContent: '',
    }));

    const { activeAgent } = get();

    try {
      await streamChatMessage(
        { message: text, agent: activeAgent, session_id: sessionId },
        // onToken
        (token) => {
          set((state) => ({
            streamingContent: state.streamingContent + token,
          }));
        },
        // onComplete
        (response: StructuredResponse) => {
          const assistantMsg: ChatMessage = {
            id: `msg_${++messageCounter}`,
            role: 'assistant',
            content: response.message,
            agent: response.agent,
            structured: response,
            timestamp: Date.now(),
          };

          set((state) => ({
            messages: [...state.messages, assistantMsg],
            isLoading: false,
            streamingContent: '',
          }));
        },
        // onError
        (error) => {
          console.error('Chat stream error:', error);
          const errorMsg: ChatMessage = {
            id: `msg_${++messageCounter}`,
            role: 'assistant',
            content: 'Sorry, something went wrong. Please try again.',
            agent: activeAgent,
            timestamp: Date.now(),
          };

          set((state) => ({
            messages: [...state.messages, errorMsg],
            isLoading: false,
            streamingContent: '',
          }));
        },
      );
    } catch {
      set({ isLoading: false, streamingContent: '' });
    }
  },

  clearMessages: () => set({ messages: [], streamingContent: '' }),
}));
