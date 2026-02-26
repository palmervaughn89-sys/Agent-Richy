'use client';

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  EYE_SHAPES,
  MOUTH_SHAPES,
  BROW_SHAPES,
  EXPRESSION_FACES,
  type FaceConfig,
} from './faceShapes';

interface Props {
  expression: string;
  /** Pupil gaze offset from useEyeTracking */
  gazeX: number;
  gazeY: number;
  /** Whether the avatar is currently blinking */
  isBlinking: boolean;
  /** Size of the SVG viewBox (rendered into parent) */
  size?: number;
}

const SPRING = { type: 'spring' as const, stiffness: 200, damping: 18 };
const MORPH = { duration: 0.35, ease: 'easeInOut' as const };

/**
 * Pure SVG renderer for the avatar's face.
 * All features are vector paths that morph smoothly between expressions.
 */
export default function SVGFace({
  expression,
  gazeX,
  gazeY,
  isBlinking,
  size = 100,
}: Props) {
  const face: FaceConfig = EXPRESSION_FACES[expression] ?? EXPRESSION_FACES.idle;

  const eyeShape = isBlinking ? EYE_SHAPES.closed : (EYE_SHAPES[face.eyes] ?? EYE_SHAPES.normal);
  const mouthShape = MOUTH_SHAPES[face.mouth] ?? MOUTH_SHAPES.smile;
  const browShape = BROW_SHAPES[face.brows] ?? BROW_SHAPES.normal;

  // Clamp gaze
  const gx = Math.max(-3, Math.min(3, gazeX));
  const gy = Math.max(-3, Math.min(3, gazeY));

  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      width="100%"
      height="100%"
      className="overflow-visible"
    >
      <defs>
        {/* Blush gradient */}
        <radialGradient id="blush-l" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#f87171" stopOpacity={face.blushIntensity} />
          <stop offset="100%" stopColor="#f87171" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="blush-r" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#f87171" stopOpacity={face.blushIntensity} />
          <stop offset="100%" stopColor="#f87171" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* ── BROWS ── */}
      <g>
        {/* Left brow (positioned around left eye) */}
        <motion.path
          d={browShape.left}
          animate={{ d: browShape.left }}
          transition={MORPH}
          fill="none"
          stroke="#78350f"
          strokeWidth="2"
          strokeLinecap="round"
          transform="translate(20, 26) scale(1.1)"
        />
        {/* Right brow */}
        <motion.path
          d={browShape.right}
          animate={{ d: browShape.right }}
          transition={MORPH}
          fill="none"
          stroke="#78350f"
          strokeWidth="2"
          strokeLinecap="round"
          transform="translate(56, 26) scale(1.1)"
        />
      </g>

      {/* ── LEFT EYE ── */}
      <g transform="translate(20, 38)">
        {/* Eye white / outline */}
        <motion.path
          d={eyeShape.outline}
          animate={{ d: eyeShape.outline }}
          transition={MORPH}
          fill={isBlinking || face.eyes === 'happy' ? 'none' : 'white'}
          stroke="#451a03"
          strokeWidth={isBlinking || face.eyes === 'happy' ? 2 : 1.2}
          strokeLinecap="round"
        />

        {/* Pupil (with gaze tracking) */}
        {eyeShape.pupil && !isBlinking && (
          <motion.path
            d={eyeShape.pupil}
            animate={{
              d: eyeShape.pupil,
              x: gx,
              y: gy,
            }}
            transition={SPRING}
            fill="#1c1917"
          />
        )}

        {/* Highlight sparkle */}
        {eyeShape.highlight && !isBlinking && (
          <motion.path
            d={eyeShape.highlight}
            animate={{
              d: eyeShape.highlight,
              x: gx * 0.5,
              y: gy * 0.5,
            }}
            transition={SPRING}
            fill="white"
            opacity={0.9}
          />
        )}

        {/* Star eyes for celebrating */}
        {face.stars && !isBlinking && (
          <motion.text
            x="12"
            y="13"
            textAnchor="middle"
            dominantBaseline="central"
            fontSize="16"
            animate={{ rotate: [0, 15, -15, 0], scale: [1, 1.1, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            ⭐
          </motion.text>
        )}
      </g>

      {/* ── RIGHT EYE ── */}
      <g transform="translate(56, 38)">
        <motion.path
          d={eyeShape.outline}
          animate={{ d: eyeShape.outline }}
          transition={MORPH}
          fill={isBlinking || face.eyes === 'happy' ? 'none' : 'white'}
          stroke="#451a03"
          strokeWidth={isBlinking || face.eyes === 'happy' ? 2 : 1.2}
          strokeLinecap="round"
        />

        {eyeShape.pupil && !isBlinking && (
          <motion.path
            d={eyeShape.pupil}
            animate={{
              d: eyeShape.pupil,
              x: gx,
              y: gy,
            }}
            transition={SPRING}
            fill="#1c1917"
          />
        )}

        {eyeShape.highlight && !isBlinking && (
          <motion.path
            d={eyeShape.highlight}
            animate={{
              d: eyeShape.highlight,
              x: gx * 0.5,
              y: gy * 0.5,
            }}
            transition={SPRING}
            fill="white"
            opacity={0.9}
          />
        )}

        {face.stars && !isBlinking && (
          <motion.text
            x="12"
            y="13"
            textAnchor="middle"
            dominantBaseline="central"
            fontSize="16"
            animate={{ rotate: [0, -15, 15, 0], scale: [1, 1.1, 1] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
          >
            ⭐
          </motion.text>
        )}
      </g>

      {/* ── BLUSH ── */}
      {face.blushIntensity > 0 && (
        <>
          <circle cx="18" cy="55" r="8" fill="url(#blush-l)" />
          <circle cx="82" cy="55" r="8" fill="url(#blush-r)" />
        </>
      )}

      {/* ── MOUTH ── */}
      <g transform="translate(30, 60)">
        <motion.path
          d={mouthShape.path}
          animate={{ d: mouthShape.path }}
          transition={MORPH}
          fill={mouthShape.open ? (mouthShape.fill ?? '#dc2626') : 'none'}
          stroke={mouthShape.open ? 'none' : '#451a03'}
          strokeWidth={mouthShape.open ? 0 : 2.2}
          strokeLinecap="round"
        />

        {/* Tongue for open-laugh */}
        {face.mouth === 'open-laugh' && (
          <motion.ellipse
            cx="20"
            cy="14"
            rx="8"
            ry="5"
            fill="#f87171"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, ...SPRING }}
          />
        )}

        {/* Tooth for big-smile */}
        {face.mouth === 'big-smile' && (
          <motion.rect
            x="16"
            y="6"
            width="8"
            height="5"
            rx="1"
            fill="white"
            initial={{ scaleY: 0 }}
            animate={{ scaleY: 1 }}
            transition={{ delay: 0.15 }}
          />
        )}
      </g>

      {/* ── SWEATDROP (confused) ── */}
      {face.sweatdrop && (
        <motion.g
          transform="translate(82, 32)"
          initial={{ opacity: 0, y: -3 }}
          animate={{ opacity: [0, 1, 1, 0], y: [-3, 0, 5, 12] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
          <path
            d="M3,0 Q5,-2 5,3 A3,3 0 1,1 1,3 Q1,-2 3,0 Z"
            fill="#60a5fa"
            opacity={0.7}
          />
        </motion.g>
      )}

      {/* ── TEAR DROPS (laughing so hard) ── */}
      {face.teardrops && (
        <>
          <motion.circle
            cx="18"
            cy="52"
            r="2"
            fill="#60a5fa"
            animate={{ y: [0, 8, 16], opacity: [0.6, 0.8, 0] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: 0.3 }}
          />
          <motion.circle
            cx="82"
            cy="52"
            r="2"
            fill="#60a5fa"
            animate={{ y: [0, 8, 16], opacity: [0.6, 0.8, 0] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: 0.7 }}
          />
        </>
      )}
    </svg>
  );
}
