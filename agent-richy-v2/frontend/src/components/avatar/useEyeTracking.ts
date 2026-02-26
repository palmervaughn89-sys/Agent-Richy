'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

interface GazeOffset {
  /** Horizontal offset in SVG units (−maxOffset … +maxOffset) */
  x: number;
  /** Vertical offset in SVG units (−maxOffset … +maxOffset) */
  y: number;
}

interface UseEyeTrackingOptions {
  /** Maximum pixel offset for the pupil (default 3) */
  maxOffset?: number;
  /** Smoothing factor 0-1 — higher = snappier, lower = more lag (default 0.15) */
  smoothing?: number;
  /** Whether tracking is currently enabled */
  enabled?: boolean;
}

/**
 * Tracks the mouse cursor position relative to the avatar container and
 * returns a smoothed (x, y) gaze offset for pupil positioning.
 *
 * Uses requestAnimationFrame for butter-smooth 60fps interpolation.
 */
export function useEyeTracking({
  maxOffset = 3,
  smoothing = 0.15,
  enabled = true,
}: UseEyeTrackingOptions = {}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const targetRef = useRef<GazeOffset>({ x: 0, y: 0 });
  const currentRef = useRef<GazeOffset>({ x: 0, y: 0 });
  const rafRef = useRef<number>(0);

  const [gaze, setGaze] = useState<GazeOffset>({ x: 0, y: 0 });

  // Mouse move → calculate target gaze
  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      const el = containerRef.current;
      if (!el || !enabled) return;

      const rect = el.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;

      // Direction from avatar center to cursor
      const dx = e.clientX - cx;
      const dy = e.clientY - cy;

      // Distance (capped so far-away cursor doesn't over-drive)
      const dist = Math.sqrt(dx * dx + dy * dy);
      const maxDist = Math.max(window.innerWidth, window.innerHeight) * 0.5;
      const factor = Math.min(dist / maxDist, 1);

      // Normalize direction and scale by maxOffset
      const angle = Math.atan2(dy, dx);
      targetRef.current = {
        x: Math.cos(angle) * factor * maxOffset,
        y: Math.sin(angle) * factor * maxOffset,
      };
    },
    [maxOffset, enabled]
  );

  // Smooth interpolation loop
  useEffect(() => {
    if (!enabled) {
      setGaze({ x: 0, y: 0 });
      return;
    }

    let running = true;

    const tick = () => {
      if (!running) return;

      const cur = currentRef.current;
      const tgt = targetRef.current;

      // Lerp
      cur.x += (tgt.x - cur.x) * smoothing;
      cur.y += (tgt.y - cur.y) * smoothing;

      // Only update React state when the change is perceptible
      const dx = Math.abs(cur.x - gaze.x);
      const dy = Math.abs(cur.y - gaze.y);
      if (dx > 0.01 || dy > 0.01) {
        setGaze({ x: cur.x, y: cur.y });
      }

      rafRef.current = requestAnimationFrame(tick);
    };

    rafRef.current = requestAnimationFrame(tick);

    return () => {
      running = false;
      cancelAnimationFrame(rafRef.current);
    };
    // We intentionally omit `gaze` from deps — it's read inside the rAF loop
    // to avoid re-creating the loop on every state change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [smoothing, enabled]);

  // Attach global mousemove listener
  useEffect(() => {
    if (!enabled) return;
    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [handleMouseMove, enabled]);

  return { containerRef, gaze };
}
