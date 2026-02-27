'use client';

import { motion } from 'framer-motion';
import type { AnalystInsight, Sentiment } from '@/types/market';

const SENTIMENT_BADGE: Record<Sentiment, string> = {
  bullish: 'bg-accent/15 text-accent',
  moderately_bullish: 'bg-accent/10 text-accent/80',
  neutral: 'bg-white/10 text-off',
  moderately_bearish: 'bg-amber-500/15 text-amber-400',
  bearish: 'bg-red-500/15 text-red-400',
};

const CONFIDENCE_DOT: Record<string, string> = {
  high: 'bg-accent',
  medium: 'bg-amber-400',
  low: 'bg-white/30',
};

function sentimentLabel(s: Sentiment): string {
  return s.replace(/_/g, ' ');
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}

export default function AnalystInsightCard({ insight }: { insight: AnalystInsight }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="bg-s1 border border-line rounded-lg p-4 relative"
    >
      {/* Sentiment badge — top right */}
      <span
        className={`absolute top-3 right-3 font-mono text-[11px] uppercase tracking-label px-2.5 py-1 rounded-full ${SENTIMENT_BADGE[insight.sentiment]}`}
      >
        {sentimentLabel(insight.sentiment)}
      </span>

      {/* Source row */}
      <div className="flex items-center gap-2 flex-wrap pr-24">
        <span className="text-accent font-mono text-xs uppercase tracking-label">
          {insight.source}
        </span>
        <span className="text-muted text-xs">{formatDate(insight.date)}</span>
        <span
          className={`inline-block w-2 h-2 rounded-full ${CONFIDENCE_DOT[insight.confidence]}`}
          title={`${insight.confidence} confidence`}
        />
      </div>

      {/* Headline */}
      <h4 className="text-txt font-medium mt-1 pr-24">{insight.headline}</h4>

      {/* Summary */}
      <p className="text-off text-sm mt-2">{insight.summary}</p>

      {/* Key points */}
      {insight.keyPoints.length > 0 && (
        <ul className="mt-2 space-y-1">
          {insight.keyPoints.map((point, i) => (
            <li key={i} className="text-off text-sm flex gap-1.5">
              <span className="text-accent shrink-0">→</span>
              <span>{point}</span>
            </li>
          ))}
        </ul>
      )}

      {/* Price target */}
      {insight.priceTarget != null && (
        <div className="flex items-center gap-3 mt-2 text-xs text-muted">
          {insight.currentPrice != null && <span>Current: ${insight.currentPrice}</span>}
          <span className="text-accent font-semibold">Target: ${insight.priceTarget}</span>
        </div>
      )}

      {/* Source link */}
      {insight.sourceUrl && (
        <a
          href={insight.sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block text-accent text-xs mt-2 hover:underline"
        >
          Read full report →
        </a>
      )}
    </motion.div>
  );
}
