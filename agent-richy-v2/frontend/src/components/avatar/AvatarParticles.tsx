'use client';

import React, { useMemo, useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { AvatarExpression } from '@/lib/types';

/* ── Particle definitions per expression ─────────────────────────────── */

interface ParticleConfig {
  symbols: string[];
  count: number;
  /** Radius from center in px */
  radius: number;
  /** Duration of particle lifetime in seconds */
  lifetime: number;
  /** Whether to continuously spawn or just burst once */
  continuous: boolean;
  /** Spawn interval ms (only for continuous) */
  interval?: number;
}

const PARTICLE_CONFIGS: Partial<Record<AvatarExpression, ParticleConfig>> = {
  idle: {
    symbols: ['💰', '✨'],
    count: 3,
    radius: 50,
    lifetime: 4,
    continuous: true,
    interval: 2000,
  },
  excited: {
    symbols: ['🚀', '💰', '📈', '✨', '🎯'],
    count: 6,
    radius: 60,
    lifetime: 2.5,
    continuous: true,
    interval: 800,
  },
  celebrating: {
    symbols: ['🎉', '🎊', '⭐', '🏆', '💫', '✨'],
    count: 10,
    radius: 70,
    lifetime: 3,
    continuous: true,
    interval: 400,
  },
  thinking: {
    symbols: ['💭', '❓', '🔍'],
    count: 3,
    radius: 45,
    lifetime: 3,
    continuous: true,
    interval: 1500,
  },
  teaching: {
    symbols: ['📚', '💡', '📝', '✏️'],
    count: 4,
    radius: 50,
    lifetime: 3.5,
    continuous: true,
    interval: 1200,
  },
  laughing: {
    symbols: ['😂', '🤣', '😄'],
    count: 4,
    radius: 50,
    lifetime: 2,
    continuous: true,
    interval: 600,
  },
  empathetic: {
    symbols: ['💙', '🫂', '💜'],
    count: 3,
    radius: 45,
    lifetime: 4,
    continuous: true,
    interval: 2000,
  },
  presenting: {
    symbols: ['📊', '📈', '💹'],
    count: 3,
    radius: 48,
    lifetime: 3.5,
    continuous: true,
    interval: 1500,
  },
};

/* ── Individual particle ─────────────────────────────────────────────── */

interface ParticleData {
  id: number;
  symbol: string;
  angle: number;
  delay: number;
  radius: number;
  lifetime: number;
  scale: number;
}

const Particle: React.FC<{ p: ParticleData }> = ({ p }) => {
  // Start position: near center
  // End position: outward at angle
  const endX = Math.cos(p.angle) * p.radius;
  const endY = Math.sin(p.angle) * p.radius;

  // Add a slight curve by offsetting the mid-path
  const midX = Math.cos(p.angle + 0.3) * p.radius * 0.5;
  const midY = Math.sin(p.angle + 0.3) * p.radius * 0.5 - 15; // float upward

  return (
    <motion.span
      initial={{
        x: 0,
        y: 0,
        opacity: 0,
        scale: 0,
        rotate: 0,
      }}
      animate={{
        x: [0, midX, endX],
        y: [0, midY, endY - 20],
        opacity: [0, 1, 1, 0],
        scale: [0, p.scale, p.scale * 0.8, 0],
        rotate: [0, 15, -10],
      }}
      transition={{
        duration: p.lifetime,
        delay: p.delay,
        ease: 'easeOut',
        times: [0, 0.3, 0.7, 1],
      }}
      className="absolute pointer-events-none select-none"
      style={{
        fontSize: `${10 + p.scale * 6}px`,
        left: '50%',
        top: '50%',
        marginLeft: '-8px',
        marginTop: '-8px',
      }}
    >
      {p.symbol}
    </motion.span>
  );
};

/* ── Confetti burst (for celebrating) ────────────────────────────────── */

interface ConfettiPiece {
  id: number;
  x: number;
  y: number;
  color: string;
  rotation: number;
  size: number;
}

const CONFETTI_COLORS = ['#f59e0b', '#ef4444', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];

const ConfettiBurst: React.FC<{ active: boolean }> = ({ active }) => {
  const pieces = useMemo<ConfettiPiece[]>(() => {
    if (!active) return [];
    return Array.from({ length: 24 }, (_, i) => ({
      id: i,
      x: (Math.random() - 0.5) * 140,
      y: -(Math.random() * 100 + 30),
      color: CONFETTI_COLORS[i % CONFETTI_COLORS.length],
      rotation: Math.random() * 720 - 360,
      size: 4 + Math.random() * 4,
    }));
  }, [active]);

  return (
    <AnimatePresence>
      {active &&
        pieces.map((p: ConfettiPiece) => (
          <motion.div
            key={p.id}
            initial={{ x: 0, y: 0, rotate: 0, opacity: 1, scale: 1 }}
            animate={{
              x: p.x,
              y: [p.y, p.y + 80],
              rotate: p.rotation,
              opacity: [1, 1, 0],
              scale: [1, 1, 0.3],
            }}
            exit={{ opacity: 0 }}
            transition={{
              duration: 1.8,
              ease: 'easeOut',
              times: [0, 0.6, 1],
            }}
            className="absolute pointer-events-none"
            style={{
              left: '50%',
              top: '50%',
              width: p.size,
              height: p.size * 0.6,
              backgroundColor: p.color,
              borderRadius: '1px',
            }}
          />
        ))}
    </AnimatePresence>
  );
};

/* ── Main AvatarParticles component ──────────────────────────────────── */

interface Props {
  expression: AvatarExpression;
}

let particleIdCounter = 0;

export default function AvatarParticles({ expression }: Props) {
  const config = PARTICLE_CONFIGS[expression];
  const [particles, setParticles] = useState<ParticleData[]>([]);

  const spawnBatch = useCallback(() => {
    if (!config) return;

    const batch: ParticleData[] = Array.from({ length: config.count }, (_, i) => {
      particleIdCounter += 1;
      return {
        id: particleIdCounter,
        symbol: config.symbols[Math.floor(Math.random() * config.symbols.length)],
        angle: (Math.PI * 2 * i) / config.count + (Math.random() - 0.5) * 0.5,
        delay: Math.random() * 0.3,
        radius: config.radius * (0.7 + Math.random() * 0.3),
        lifetime: config.lifetime * (0.8 + Math.random() * 0.4),
        scale: 0.8 + Math.random() * 0.4,
      };
    });

    setParticles((prev: ParticleData[]) => [...prev.slice(-20), ...batch]); // cap old particles
  }, [config]);

  // Spawn particles on expression change
  useEffect(() => {
    if (!config) {
      setParticles([]);
      return;
    }

    // Immediate first batch
    spawnBatch();

    if (!config.continuous || !config.interval) return;

    // Continuous spawning
    const timer = setInterval(spawnBatch, config.interval);
    return () => clearInterval(timer);
  }, [expression, config, spawnBatch]);

  return (
    <div className="absolute inset-0 overflow-visible pointer-events-none z-10">
      <AnimatePresence>
        {particles.map((p: ParticleData) => (
          <Particle key={p.id} p={p} />
        ))}
      </AnimatePresence>

      <ConfettiBurst active={expression === 'celebrating'} />
    </div>
  );
}
