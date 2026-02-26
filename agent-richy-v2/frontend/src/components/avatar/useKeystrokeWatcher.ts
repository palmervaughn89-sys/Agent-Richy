'use client';

import { useCallback, useRef, useEffect } from 'react';
import { useAvatarStore } from '@/hooks/useAvatar';
import { KEYSTROKE_TRIGGERS, REACTION_BUBBLES } from './expressions';
import type { AvatarExpression } from '@/lib/types';

const DEBOUNCE_MS = 150;
const REACTION_COOLDOWN_MS = 3000;
const IDLE_TIMEOUT_MS = 4000;

/**
 * Watches keystrokes from the chat input, debounces them,
 * then matches keywords → avatar expression + reaction bubble.
 * Also calls the backend /api/keystroke endpoint for server-side
 * emotion mapping (for agent-specific reactions).
 */
export function useKeystrokeWatcher() {
  const { setExpression, setBubble, setIsTyping, goIdle } = useAvatarStore();

  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const idleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastReactionRef = useRef<number>(0);
  const lastExpressionRef = useRef<AvatarExpression>('idle');

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    };
  }, []);

  /** Locally evaluate keystroke against trigger keywords */
  const localMatch = useCallback((text: string): AvatarExpression | null => {
    const lower = text.toLowerCase();
    let best: { expression: AvatarExpression; priority: number } | null = null;

    for (const trigger of KEYSTROKE_TRIGGERS) {
      for (const kw of trigger.keywords) {
        if (lower.includes(kw)) {
          if (!best || trigger.priority > best.priority) {
            best = { expression: trigger.expression, priority: trigger.priority };
          }
        }
      }
    }
    return best?.expression ?? null;
  }, []);

  /** Pick a random reaction bubble for a given expression */
  const pickBubble = useCallback((expression: AvatarExpression): string | null => {
    const pool = REACTION_BUBBLES[expression];
    if (!pool || pool.length === 0) return null;
    return pool[Math.floor(Math.random() * pool.length)];
  }, []);

  /** Core handler called on every input change */
  const onInputChange = useCallback(
    (text: string) => {
      // Always set typing state immediately
      setIsTyping(true);

      // Reset idle timer
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
      idleTimerRef.current = setTimeout(() => {
        setIsTyping(false);
        goIdle();
      }, IDLE_TIMEOUT_MS);

      // Debounce the keyword analysis
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = setTimeout(() => {
        if (!text.trim()) {
          setExpression('watching');
          return;
        }

        // 1) Local keyword match (instant)
        const matched = localMatch(text);
        if (matched && matched !== lastExpressionRef.current) {
          lastExpressionRef.current = matched;
          setExpression(matched);

          // Reaction bubble (with cooldown so we don't spam)
          const now = Date.now();
          if (now - lastReactionRef.current > REACTION_COOLDOWN_MS) {
            const bubble = pickBubble(matched);
            if (bubble) {
              setBubble(bubble);
              lastReactionRef.current = now;
            }
          }
        } else if (!matched && lastExpressionRef.current !== 'watching') {
          lastExpressionRef.current = 'watching';
          setExpression('watching');
        }

        // 2) Fire-and-forget backend keystroke analysis
        // (for agent-specific reactions; result applied asynchronously)
        fetch('/api/keystroke', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text,
            current_agent: 'coach_richy',
            session_id: 'default',
          }),
        })
          .then((res) => res.json())
          .then((data) => {
            if (data.expression && data.expression !== lastExpressionRef.current) {
              lastExpressionRef.current = data.expression;
              setExpression(data.expression);
              if (data.bubble) setBubble(data.bubble);
            }
          })
          .catch(() => {
            // Backend down — local match is already applied, no-op
          });
      }, DEBOUNCE_MS);
    },
    [setExpression, setBubble, setIsTyping, goIdle, localMatch, pickBubble]
  );

  /** Call this when user sends a message to reset to idle */
  const onMessageSent = useCallback(() => {
    setIsTyping(false);
    lastExpressionRef.current = 'thinking';
    setExpression('thinking');
    setBubble('Let me think about that... 🤔');
  }, [setExpression, setBubble, setIsTyping]);

  return { onInputChange, onMessageSent };
}
