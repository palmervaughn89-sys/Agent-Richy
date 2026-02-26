'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

interface UseBlinkingOptions {
  /** Min ms between blinks (default 2000) */
  minInterval?: number;
  /** Max ms between blinks (default 6000) */
  maxInterval?: number;
  /** Blink duration in ms (default 150) */
  blinkDuration?: number;
  /** Whether blinking is enabled */
  enabled?: boolean;
}

/**
 * Returns a boolean `isBlinking` that flips true for a short duration
 * at randomized intervals, simulating natural blinking.
 *
 * Can also be manually triggered (e.g. on expression change).
 */
export function useBlinking({
  minInterval = 2000,
  maxInterval = 6000,
  blinkDuration = 150,
  enabled = true,
}: UseBlinkingOptions = {}) {
  const [isBlinking, setIsBlinking] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const blinkTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearTimers = useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (blinkTimeoutRef.current) clearTimeout(blinkTimeoutRef.current);
  }, []);

  const scheduleBlink = useCallback(() => {
    if (!enabled) return;

    const interval = minInterval + Math.random() * (maxInterval - minInterval);

    timeoutRef.current = setTimeout(() => {
      setIsBlinking(true);

      blinkTimeoutRef.current = setTimeout(() => {
        setIsBlinking(false);
        scheduleBlink(); // Schedule the next blink
      }, blinkDuration);
    }, interval);
  }, [enabled, minInterval, maxInterval, blinkDuration]);

  /** Force a blink right now (useful on expression change) */
  const triggerBlink = useCallback(() => {
    clearTimers();
    setIsBlinking(true);

    blinkTimeoutRef.current = setTimeout(() => {
      setIsBlinking(false);
      scheduleBlink();
    }, blinkDuration);
  }, [clearTimers, blinkDuration, scheduleBlink]);

  /** Double-blink — two quick blinks (on surprise) */
  const triggerDoubleBlink = useCallback(() => {
    clearTimers();
    setIsBlinking(true);

    blinkTimeoutRef.current = setTimeout(() => {
      setIsBlinking(false);

      setTimeout(() => {
        setIsBlinking(true);
        blinkTimeoutRef.current = setTimeout(() => {
          setIsBlinking(false);
          scheduleBlink();
        }, blinkDuration);
      }, 100); // gap between double-blinks
    }, blinkDuration);
  }, [clearTimers, blinkDuration, scheduleBlink]);

  useEffect(() => {
    if (enabled) {
      scheduleBlink();
    }
    return clearTimers;
  }, [enabled, scheduleBlink, clearTimers]);

  return { isBlinking, triggerBlink, triggerDoubleBlink };
}
