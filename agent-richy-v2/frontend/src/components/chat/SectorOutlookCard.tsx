'use client';

import { motion } from 'framer-motion';
import type { SectorOutlook, Sentiment } from '@/types/market';

const SENTIMENT_BADGE: Record<Sentiment, string> = {
  bullish: 'bg-accent/15 text-accent',
  moderately_bullish: 'bg-accent/10 text-accent/80',
  neutral: 'bg-white/10 text-off',
  moderately_bearish: 'bg-amber-500/15 text-amber-400',
  bearish: 'bg-red-500/15 text-red-400',
};

function sentimentLabel(s: Sentiment): string {
  return s.replace(/_/g, ' ');
}

export default function SectorOutlookCard({ outlook }: { outlook: SectorOutlook }) {
  const total = outlook.bullCount + outlook.neutralCount + outlook.bearCount || 1;
  const bullPct = (outlook.bullCount / total) * 100;
  const neutralPct = (outlook.neutralCount / total) * 100;
  const bearPct = (outlook.bearCount / total) * 100;

  const sources = Array.from(new Set(outlook.insights.map((i) => i.source)));

  const { peRatio, ytdReturn, morningstarValuation } = outlook.keyMetrics;
  const hasMetrics = peRatio != null || ytdReturn != null || morningstarValuation != null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="bg-card border border-line rounded-card p-5"
    >
      {/* Header */}
      <div className="flex justify-between items-center">
        <span className="text-lg font-semibold text-txt">{outlook.sectorName}</span>
        <span
          className={`font-mono text-[11px] uppercase tracking-label px-2.5 py-1 rounded-full ${SENTIMENT_BADGE[outlook.consensusSentiment]}`}
        >
          {sentimentLabel(outlook.consensusSentiment)}
        </span>
      </div>

      {/* Sentiment bar */}
      <div className="h-2 rounded-full overflow-hidden flex mt-3">
        {bullPct > 0 && (
          <div className="bg-accent" style={{ width: `${bullPct}%` }} />
        )}
        {neutralPct > 0 && (
          <div className="bg-s2" style={{ width: `${neutralPct}%` }} />
        )}
        {bearPct > 0 && (
          <div className="bg-red-500/50" style={{ width: `${bearPct}%` }} />
        )}
      </div>
      <p className="text-muted text-xs mt-1.5">
        {outlook.bullCount} Bullish · {outlook.neutralCount} Neutral · {outlook.bearCount} Bearish
      </p>

      {/* Key metrics */}
      {hasMetrics && (
        <div className="grid grid-cols-3 gap-3 mt-4">
          {peRatio != null && (
            <div className="bg-s1 rounded-lg p-3 text-center">
              <div className="text-accent font-bold">{peRatio.toFixed(1)}x</div>
              <div className="text-muted text-xs font-mono uppercase">P/E</div>
            </div>
          )}
          {ytdReturn != null && (
            <div className="bg-s1 rounded-lg p-3 text-center">
              <div className="text-accent font-bold">
                {ytdReturn >= 0 ? '+' : ''}
                {ytdReturn.toFixed(1)}%
              </div>
              <div className="text-muted text-xs font-mono uppercase">YTD</div>
            </div>
          )}
          {morningstarValuation != null && (
            <div className="bg-s1 rounded-lg p-3 text-center">
              <div className="text-accent font-bold capitalize">
                {morningstarValuation.replace(/_/g, ' ')}
              </div>
              <div className="text-muted text-xs font-mono uppercase">Valuation</div>
            </div>
          )}
        </div>
      )}

      {/* Bull vs Bear cases */}
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="bg-s1 rounded-lg p-3">
          <div className="text-accent font-mono text-[11px] uppercase tracking-label mb-1">
            Bull Case
          </div>
          <p className="text-off text-sm">{outlook.topBullCase}</p>
        </div>
        <div className="bg-s1 rounded-lg p-3">
          <div className="text-red-400 font-mono text-[11px] uppercase tracking-label mb-1">
            Bear Case
          </div>
          <p className="text-off text-sm">{outlook.topBearCase}</p>
        </div>
      </div>

      {/* Sources */}
      {sources.length > 0 && (
        <p className="text-muted text-xs italic mt-3">{sources.join(', ')}</p>
      )}
    </motion.div>
  );
}
