'use client';

import React, { useMemo, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence, useSpring, useTransform } from 'framer-motion';
import { useAvatarStore } from '@/hooks/useAvatar';
import { getExpressionConfig } from './AvatarExpressionEngine';
import { EXPRESSION_PALETTES, EXPRESSION_FACES } from './faceShapes';
import SVGFace from './SVGFace';
import AvatarParticles from './AvatarParticles';
import AmbientGlow from './AmbientGlow';
import SpeechBubble from './SpeechBubble';
import { useEyeTracking } from './useEyeTracking';
import { useBlinking } from './useBlinking';
import type { AvatarExpression } from '@/lib/types';

/* ───── Body animation variants (the whole circle) ───── */
const bodyVariants: Record<string, object> = {
  float: {
    y: [0, -6, 0],
    transition: { duration: 3, repeat: Infinity, ease: 'easeInOut' },
  },
  bounce: {
    y: [0, -14, 0],
    transition: { duration: 0.5, repeat: Infinity, ease: 'easeOut' },
  },
  shake: {
    x: [-3, 3, -3, 3, 0],
    transition: { duration: 0.4, repeat: 2 },
  },
  'lean-forward': {
    rotate: [0, 2, 0],
    transition: { duration: 1.5, repeat: Infinity, ease: 'easeInOut' },
  },
  nod: {
    y: [0, 4, 0],
    transition: { duration: 0.6, repeat: 2 },
  },
  wave: {
    rotate: [0, 10, -5, 10, 0],
    transition: { duration: 1 },
  },
  gesture: {
    scale: [1, 1.03, 1],
    transition: { duration: 1.5, repeat: Infinity },
  },
  point: {
    x: [0, 4, 0],
    transition: { duration: 1, repeat: Infinity },
  },
  'fist-pump': {
    y: [0, -20, 0],
    rotate: [0, -5, 0],
    transition: { duration: 0.6 },
  },
  'head-scratch': {
    rotate: [0, -3, 3, 0],
    transition: { duration: 1.2, repeat: Infinity },
  },
  'chin-tap': {
    y: [0, 2, 0],
    transition: { duration: 1.5, repeat: Infinity },
  },
  still: {},
};

/* ───── Typing indicator dots ───── */
const TypingDots: React.FC = () => (
  <motion.div
    initial={{ opacity: 0, y: 4 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0 }}
    className="absolute -bottom-6 left-1/2 -translate-x-1/2 flex gap-1"
  >
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        className="w-1.5 h-1.5 rounded-full bg-brand-gold"
        animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }}
        transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
      />
    ))}
  </motion.div>
);

/* ───── Size config ───── */
interface SizeConfig {
  diameter: number;
  containerClass: string;
  showParticles: boolean;
  showLabel: boolean;
  bubblePosition: 'top' | 'right';
}

const SIZES: Record<string, SizeConfig> = {
  sm: {
    diameter: 56,
    containerClass: 'w-14 h-14',
    showParticles: false,
    showLabel: false,
    bubblePosition: 'right',
  },
  md: {
    diameter: 96,
    containerClass: 'w-24 h-24',
    showParticles: true,
    showLabel: true,
    bubblePosition: 'top',
  },
  lg: {
    diameter: 140,
    containerClass: 'w-[140px] h-[140px]',
    showParticles: true,
    showLabel: true,
    bubblePosition: 'top',
  },
  xl: {
    diameter: 192,
    containerClass: 'w-48 h-48',
    showParticles: true,
    showLabel: true,
    bubblePosition: 'right',
  },
};

/* ═══════════════════════════════════════════════════════════════════════
   MAIN AVATAR COMPONENT
   - SVG vector face with morphing paths
   - Eye tracking (follows cursor)
   - Natural blinking (randomized interval)
   - Ambient glow that shifts with expression
   - Particle effects (floating emoji)
   - Premium speech bubble with typewriter reveal
   - Breathing animation (subtle scale pulse)
   - Confetti burst on celebrating
   ═══════════════════════════════════════════════════════════════════════ */

export default function RichyAvatar({
  size = 'md',
}: {
  size?: 'sm' | 'md' | 'lg' | 'xl';
}) {
  const { expression, bubble, isTyping } = useAvatarStore();
  const cfg = useMemo(() => getExpressionConfig(expression), [expression]);
  const palette = EXPRESSION_PALETTES[expression] ?? EXPRESSION_PALETTES.idle;
  const sizeConfig = SIZES[size] ?? SIZES.md;

  // Hooks
  const { containerRef, gaze } = useEyeTracking({
    maxOffset: 3,
    smoothing: 0.12,
    enabled: sizeConfig.diameter >= 80, // only track eyes on md+
  });

  const { isBlinking, triggerBlink, triggerDoubleBlink } = useBlinking({
    enabled: true,
    minInterval: 2500,
    maxInterval: 5500,
  });

  // Blink on expression change
  const prevExpressionRef = useRef<AvatarExpression>(expression);
  useEffect(() => {
    if (expression !== prevExpressionRef.current) {
      // Surprise expressions get a double-blink
      if (expression === 'excited' || expression === 'celebrating' || expression === 'confused') {
        triggerDoubleBlink();
      } else {
        triggerBlink();
      }
      prevExpressionRef.current = expression;
    }
  }, [expression, triggerBlink, triggerDoubleBlink]);

  const bodyAnim = bodyVariants[cfg.bodyAnimation] ?? bodyVariants.float;

  // Breathing: subtle continuous scale pulse
  const breatheAnim = {
    scale: [1, 1.015, 1],
    transition: { duration: 4, repeat: Infinity, ease: 'easeInOut' as const },
  };

  return (
    <div
      ref={containerRef}
      className="relative inline-flex flex-col items-center select-none"
      style={{ width: sizeConfig.diameter + 80, height: sizeConfig.diameter + 80 }}
    >
      {/* ── Ambient glow layers ── */}
      <div
        className="absolute"
        style={{
          left: 40,
          top: sizeConfig.showLabel ? 20 : 40,
        }}
      >
        <AmbientGlow
          expression={expression}
          diameter={sizeConfig.diameter}
          active={!isTyping}
        />
      </div>

      {/* ── Particle system ── */}
      {sizeConfig.showParticles && (
        <div
          className="absolute"
          style={{
            left: 40,
            top: sizeConfig.showLabel ? 20 : 40,
            width: sizeConfig.diameter,
            height: sizeConfig.diameter,
          }}
        >
          <AvatarParticles expression={expression} />
        </div>
      )}

      {/* ── Speech bubble ── */}
      <div
        className="absolute"
        style={{
          left: 40,
          top: sizeConfig.showLabel ? 20 : 40,
          width: sizeConfig.diameter,
          height: sizeConfig.diameter,
        }}
      >
        <SpeechBubble
          text={bubble}
          position={sizeConfig.bubblePosition}
          accentColor={palette.accent}
          autoDismissMs={4500}
        />
      </div>

      {/* ── Main avatar body ── */}
      <motion.div
        animate={{ ...bodyAnim, ...breatheAnim }}
        whileHover={{ scale: 1.06 }}
        transition={{ type: 'spring', stiffness: 280, damping: 20 }}
        className={`relative ${sizeConfig.containerClass} rounded-full cursor-default overflow-hidden`}
        style={{
          marginTop: sizeConfig.showLabel ? 20 : 40,
          marginLeft: 40,
          marginRight: 40,
          background: `linear-gradient(135deg, ${palette.bgGradient[0]}, ${palette.bgGradient[1]})`,
          boxShadow: `
            0 0 ${sizeConfig.diameter * 0.25}px ${palette.glow}30,
            0 4px 16px rgba(0,0,0,0.15),
            inset 0 -4px 12px rgba(0,0,0,0.06)
          `,
        }}
      >
        {/* Inner highlight (top-left gloss) */}
        <div
          className="absolute rounded-full pointer-events-none"
          style={{
            top: '8%',
            left: '12%',
            width: '30%',
            height: '30%',
            background: 'radial-gradient(circle, rgba(255,255,255,0.5) 0%, transparent 70%)',
          }}
        />

        {/* Shadow at bottom for depth */}
        <div
          className="absolute bottom-0 left-0 right-0 h-1/4 pointer-events-none rounded-b-full"
          style={{
            background: 'linear-gradient(to top, rgba(0,0,0,0.08), transparent)',
          }}
        />

        {/* Ring border */}
        <div
          className="absolute inset-0 rounded-full pointer-events-none"
          style={{
            border: `2.5px solid ${palette.ring}70`,
            boxShadow: `inset 0 0 0 1px ${palette.ring}25`,
          }}
        />

        {/* SVG Face — the core rendering */}
        <div className="absolute inset-0 p-[12%]">
          <SVGFace
            expression={expression}
            gazeX={gaze.x}
            gazeY={gaze.y}
            isBlinking={isBlinking}
          />
        </div>
      </motion.div>

      {/* ── Typing indicator ── */}
      <AnimatePresence>
        {isTyping && <TypingDots />}
      </AnimatePresence>

      {/* ── Expression label ── */}
      {sizeConfig.showLabel && (
        <motion.span
          key={cfg.label}
          initial={{ opacity: 0, y: -2 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 text-[10px] font-semibold tracking-widest uppercase"
          style={{ color: palette.glow }}
        >
          {cfg.label}
        </motion.span>
      )}
    </div>
  );
}
