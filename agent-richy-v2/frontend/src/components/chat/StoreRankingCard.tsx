'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import type { StoreCategoryRanking } from '@/types/pricing';

function rankColor(rank: number): string {
  if (rank === 1) return '#FFD700'; // gold
  if (rank === 2) return '#C0C0C0'; // silver
  if (rank === 3) return '#CD7F32'; // bronze
  return '';                         // fallback to text-muted
}

function priceLabel(index: number): { text: string; className: string } {
  if (index < 90) return { text: 'Great prices', className: 'text-accent' };
  if (index <= 100) return { text: 'Average', className: 'text-off' };
  return { text: 'Above average', className: 'text-amber-400' };
}

export default function StoreRankingCard({
  ranking,
}: {
  ranking: StoreCategoryRanking;
}) {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="bg-card border border-line rounded-card p-5"
    >
      {/* Header */}
      <h3 className="text-lg font-semibold text-txt">
        {ranking.categoryName} &mdash; Store Rankings
      </h3>
      <p className="text-muted text-sm">Where to get the best prices</p>

      {/* Rankings list */}
      <ul className="mt-4 space-y-2">
        {ranking.rankings.map((r, idx) => {
          const color = rankColor(r.rank);
          const price = priceLabel(r.avgPriceIndex);

          return (
            <motion.li
              key={r.store}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, delay: idx * 0.06 }}
              className="bg-s1 rounded-lg p-3 flex items-center gap-4 relative"
              onMouseEnter={() => setHoveredIdx(idx)}
              onMouseLeave={() => setHoveredIdx(null)}
              onFocus={() => setHoveredIdx(idx)}
              onBlur={() => setHoveredIdx(null)}
              tabIndex={0}
            >
              {/* Rank number */}
              <span
                className="font-bold text-2xl font-mono w-8 text-center shrink-0"
                style={color ? { color } : undefined}
              >
                {!color && (
                  <span className="text-muted">{r.rank}</span>
                )}
                {color && r.rank}
              </span>

              {/* Store + best-for */}
              <div className="flex-1 min-w-0">
                <span className="text-txt font-medium">{r.storeName}</span>
                <span className="block text-muted text-xs mt-0.5 truncate">
                  {r.bestFor}
                </span>
              </div>

              {/* Price index label */}
              <div className="text-right shrink-0">
                <span className={`text-sm font-semibold ${price.className}`}>
                  {price.text}
                </span>
                <span className="block text-muted text-[11px] font-mono">
                  Index: {r.avgPriceIndex}
                </span>
              </div>

              {/* Tooltip — watch out */}
              {hoveredIdx === idx && r.watchOut && (
                <motion.div
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute left-12 -bottom-8 z-10 bg-s2 border border-line rounded-lg px-3 py-1.5 text-muted text-xs shadow-lg whitespace-nowrap"
                >
                  ⚠️ {r.watchOut}
                </motion.div>
              )}
            </motion.li>
          );
        })}
      </ul>

      {/* Footer */}
      <div className="mt-3 space-y-0.5">
        <p className="text-muted text-[11px] italic">Source: {ranking.source}</p>
        <p className="text-muted text-[11px]">
          Last updated: {ranking.lastUpdated}
        </p>
      </div>
    </motion.div>
  );
}
