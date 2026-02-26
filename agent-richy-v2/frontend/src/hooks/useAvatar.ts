/* ── Avatar state management ─────────────────────────────────────────── */

import { create } from 'zustand';
import type { AvatarExpression } from '@/lib/types';

interface AvatarStore {
  expression: AvatarExpression;
  bubble: string | null;
  isTyping: boolean;
  lastActivity: number;

  setExpression: (expression: AvatarExpression, bubble?: string | null) => void;
  setBubble: (bubble: string | null) => void;
  setTyping: (isTyping: boolean) => void;
  /** Alias used by useKeystrokeWatcher */
  setIsTyping: (isTyping: boolean) => void;
  goIdle: () => void;
}

export const useAvatarStore = create<AvatarStore>((set, get) => ({
  expression: 'idle',
  bubble: null,
  isTyping: false,
  lastActivity: Date.now(),

  setExpression: (expression, bubble = null) =>
    set({ expression, bubble, lastActivity: Date.now() }),

  setBubble: (bubble) =>
    set({ bubble, lastActivity: Date.now() }),

  setTyping: (isTyping) =>
    set({
      isTyping,
      expression: isTyping ? 'watching' : 'idle',
      lastActivity: Date.now(),
    }),

  // Alias so useKeystrokeWatcher can destructure either name
  setIsTyping: (isTyping) =>
    get().setTyping(isTyping),

  goIdle: () =>
    set({ expression: 'idle', bubble: null, isTyping: false }),
}));
