'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Props {
  text: string | null;
  /** Position relative to avatar: 'top' | 'right' | 'left' */
  position?: 'top' | 'right' | 'left';
  /** Auto-dismiss after ms (0 = manual dismiss) */
  autoDismissMs?: number;
  /** Accent color for the bubble border */
  accentColor?: string;
}

/**
 * Premium animated speech bubble with:
 * - Typewriter text reveal
 * - Spring entrance/exit
 * - Decorative pointer tail
 * - Gradient accent border
 * - Auto-dismiss with fade
 */
export default function SpeechBubble({
  text,
  position = 'top',
  autoDismissMs = 4000,
  accentColor = '#f59e0b',
}: Props) {
  const [displayText, setDisplayText] = useState('');
  const [visible, setVisible] = useState(false);

  // Typewriter effect
  useEffect(() => {
    if (!text) {
      setVisible(false);
      setDisplayText('');
      return;
    }

    setVisible(true);
    setDisplayText('');

    let i = 0;
    const chars = Array.from(text); // handle emoji correctly
    const speed = Math.max(15, Math.min(40, 800 / chars.length)); // adaptive speed

    const timer = setInterval(() => {
      i += 1;
      if (i <= chars.length) {
        setDisplayText(chars.slice(0, i).join(''));
      } else {
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text]);

  // Auto-dismiss
  useEffect(() => {
    if (!text || autoDismissMs <= 0) return;

    const timer = setTimeout(() => {
      setVisible(false);
    }, autoDismissMs);

    return () => clearTimeout(timer);
  }, [text, autoDismissMs]);

  // Position-dependent classes
  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-3',
    right: 'left-full top-1/2 -translate-y-1/2 ml-4',
    left: 'right-full top-1/2 -translate-y-1/2 mr-4',
  };

  // Pointer/tail SVG per position
  const renderTail = () => {
    const tailColor = 'var(--bubble-bg, #111D32)';
    switch (position) {
      case 'top':
        return (
          <svg
            className="absolute -bottom-2 left-1/2 -translate-x-1/2"
            width="16" height="8" viewBox="0 0 16 8"
          >
            <path d="M0,0 L8,8 L16,0" fill={tailColor} />
          </svg>
        );
      case 'right':
        return (
          <svg
            className="absolute top-1/2 -left-2 -translate-y-1/2"
            width="8" height="16" viewBox="0 0 8 16"
          >
            <path d="M8,0 L0,8 L8,16" fill={tailColor} />
          </svg>
        );
      case 'left':
        return (
          <svg
            className="absolute top-1/2 -right-2 -translate-y-1/2"
            width="8" height="16" viewBox="0 0 8 16"
          >
            <path d="M0,0 L8,8 L0,16" fill={tailColor} />
          </svg>
        );
    }
  };

  // Entry animation direction
  const entryVariant = {
    top: { initial: { y: 8, opacity: 0, scale: 0.92 }, animate: { y: 0, opacity: 1, scale: 1 } },
    right: { initial: { x: -8, opacity: 0, scale: 0.92 }, animate: { x: 0, opacity: 1, scale: 1 } },
    left: { initial: { x: 8, opacity: 0, scale: 0.92 }, animate: { x: 0, opacity: 1, scale: 1 } },
  };

  return (
    <AnimatePresence>
      {visible && text && (
        <motion.div
          key={text}
          initial={entryVariant[position].initial}
          animate={entryVariant[position].animate}
          exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
          transition={{ type: 'spring', stiffness: 400, damping: 28 }}
          className={`absolute z-30 ${positionClasses[position]}`}
        >
          {/* Bubble body */}
          <div
            className="relative rounded-xl px-3.5 py-2 shadow-xl backdrop-blur-sm
                       max-w-[220px] text-[13px] leading-snug"
            style={{
              // @ts-ignore -- CSS custom property
              '--bubble-bg': '#111D32',
              background: '#111D32',
              border: `1.5px solid ${accentColor}33`,
              boxShadow: `0 4px 20px ${accentColor}15, 0 0 0 1px ${accentColor}10`,
              color: '#e2e8f0',
            }}
          >
            {/* Top gradient accent line */}
            <div
              className="absolute top-0 left-3 right-3 h-[2px] rounded-full"
              style={{
                background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`,
              }}
            />

            {/* Text with blinking cursor */}
            <span className="whitespace-pre-wrap">{displayText}</span>
            {displayText.length < (text?.length ?? 0) && (
              <motion.span
                animate={{ opacity: [1, 0] }}
                transition={{ duration: 0.5, repeat: Infinity }}
                className="inline-block w-[2px] h-[14px] ml-0.5 align-text-bottom rounded-full"
                style={{ backgroundColor: accentColor }}
              />
            )}

            {/* Tail */}
            {renderTail()}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
