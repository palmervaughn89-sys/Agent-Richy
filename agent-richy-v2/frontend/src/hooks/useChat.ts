/* ── Chat state management + API calls ───────────────────────────────── */

import { create } from 'zustand';
import type { ChatMessage, StructuredResponse } from '@/lib/types';
import { streamChatMessage } from '@/lib/api';
import { detectSkill } from '@/lib/skillDetection';
import type { DetectedSkill } from '@/lib/skillDetection';

interface ChatStore {
  messages: ChatMessage[];
  isLoading: boolean;
  streamingContent: string;
  /** Currently active skill (persists across messages until cleared). */
  activeSkill: DetectedSkill;
  /** Optimizer expense summary carried across messages. */
  optimizerExpenses: string;

  sendMessage: (text: string, sessionId?: string) => Promise<void>;
  clearMessages: () => void;
  setOptimizerExpenses: (summary: string) => void;
}

let messageCounter = 0;

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  isLoading: false,
  streamingContent: '',
  activeSkill: null,
  optimizerExpenses: '',

  setOptimizerExpenses: (summary) => set({ optimizerExpenses: summary }),

  sendMessage: async (text: string, sessionId = 'default') => {
    const userMsg: ChatMessage = {
      id: `msg_${++messageCounter}`,
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };

    // ── Skill detection ──────────────────────────────────────────
    const detected = detectSkill(text);
    const { activeSkill, optimizerExpenses } = get();
    const skill = detected ?? activeSkill; // persist until cleared

    if (detected) {
      console.log(`[skill-detection] Triggered: ${detected}`);
    }

    set((state) => ({
      messages: [...state.messages, userMsg],
      isLoading: true,
      streamingContent: '',
      activeSkill: skill,
    }));

    try {
      await streamChatMessage(
        {
          message: text,
          agent: 'coach_richy',
          session_id: sessionId,
          skill,
          optimizer_expenses: skill === 'optimizer' ? optimizerExpenses : undefined,
        },
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
            agent: 'coach_richy',
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

  clearMessages: () => set({ messages: [], streamingContent: '', activeSkill: null, optimizerExpenses: '' }),
}));
