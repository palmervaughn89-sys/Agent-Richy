'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface Badge {
  id: string;
  name?: string;
  label?: string;
  icon?: string;
  emoji?: string;
  earned: boolean;
  description?: string;
}

interface Props {
  badges: Badge[];
}

export default function BadgeDisplay({ badges }: Props) {
  const earned = badges.filter((b) => b.earned).length;

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-txt">
          🏆 Badges
        </h3>
        <span className="text-xs text-muted">
          {earned}/{badges.length} earned
        </span>
      </div>

      <div className="grid grid-cols-4 sm:grid-cols-6 gap-2">
        {badges.map((badge) => (
          <motion.div
            key={badge.id}
            whileHover={{ scale: 1.1, rotate: badge.earned ? 5 : 0 }}
            className={`flex flex-col items-center gap-1 p-2 rounded-lg cursor-default
              ${
                badge.earned
                  ? 'bg-accent/15 border border-accent/40'
                  : 'bg-s1 border border-line opacity-40'
              }`}
            title={badge.description}
          >
            <span className={`text-2xl ${!badge.earned ? 'grayscale' : ''}`}>
              {badge.icon || badge.emoji}
            </span>
            <span className="text-[9px] text-center font-medium text-off
                             line-clamp-1">
              {badge.name || badge.label}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
