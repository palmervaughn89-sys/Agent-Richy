'use client';

import React from 'react';
import { motion } from 'framer-motion';
import type { AvatarExpression } from '@/lib/types';
import { EXPRESSION_PALETTES } from './faceShapes';

interface Props {
  expression: AvatarExpression;
  /** Diameter of the avatar circle in px */
  diameter: number;
  /** Whether to show the pulsing ring */
  active?: boolean;
}

/**
 * Multi-layered ambient glow that surrounds the avatar.
 * - Inner soft glow (box-shadow)
 * - Outer pulsing ring
 * - Radial gradient backdrop
 *
 * Colors shift smoothly based on expression.
 */
export default function AmbientGlow({ expression, diameter, active = true }: Props) {
  const palette = EXPRESSION_PALETTES[expression] ?? EXPRESSION_PALETTES.idle;

  return (
    <>
      {/* Layer 1: Large soft radial glow behind everything */}
      <motion.div
        animate={{
          background: `radial-gradient(circle, ${palette.glow}18 0%, transparent 70%)`,
        }}
        transition={{ duration: 0.8 }}
        className="absolute inset-0 -m-8 rounded-full pointer-events-none"
        style={{ width: diameter + 64, height: diameter + 64, left: -32, top: -32 }}
      />

      {/* Layer 2: Pulsing ring */}
      {active && (
        <motion.div
          animate={{
            borderColor: `${palette.ring}60`,
            scale: [1, 1.08, 1],
            opacity: [0.5, 0.8, 0.5],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute inset-0 rounded-full border-2 pointer-events-none"
          style={{
            width: diameter + 12,
            height: diameter + 12,
            left: -6,
            top: -6,
          }}
        />
      )}

      {/* Layer 3: Inner glow ring (tighter) */}
      <motion.div
        animate={{
          boxShadow: `0 0 ${diameter * 0.3}px ${diameter * 0.08}px ${palette.glow}25,
                      inset 0 0 ${diameter * 0.15}px ${palette.glow}10`,
        }}
        transition={{ duration: 0.6 }}
        className="absolute inset-0 rounded-full pointer-events-none"
        style={{ width: diameter, height: diameter }}
      />
    </>
  );
}
