'use client';

import { motion } from 'framer-motion';
import type { MarketIntelligenceReport, Sentiment } from '@/types/market';
import SectorOutlookCard from './SectorOutlookCard';

const SENTIMENT_LABEL: Record<Sentiment, string> = {
  bullish: 'bullish 📈',
  moderately_bullish: 'moderately bullish',
  neutral: 'neutral',
  moderately_bearish: 'moderately cautious',
  bearish: 'bearish 📉',
};

export default function MarketReportCard({
  report,
}: {
  report: MarketIntelligenceReport;
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="space-y-4"
    >
      {/* Header */}
      <div className="bg-s1 rounded-card p-6 text-center">
        <div className="font-mono text-accent text-sm tracking-label uppercase">
          Market Intelligence
        </div>
        <h2 className="text-2xl font-bold text-txt mt-2">
          Markets are feeling{' '}
          <span className="text-accent">{SENTIMENT_LABEL[report.marketSentiment]}</span>
        </h2>

        {/* Key themes */}
        {report.keyThemes.length > 0 && (
          <div className="flex flex-wrap gap-2 justify-center mt-3">
            {report.keyThemes.map((theme) => (
              <span
                key={theme}
                className="bg-ghost text-accent font-mono text-[11px] px-2.5 py-1 rounded-full"
              >
                {theme}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Top sectors */}
      {report.topSectors.length > 0 && (
        <div>
          <div className="font-mono text-accent text-xs uppercase tracking-label mb-3">
            Sectors Analysts Like
          </div>
          <div className="space-y-3">
            {report.topSectors.map((outlook, i) => (
              <motion.div
                key={outlook.sector}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08, duration: 0.3 }}
              >
                <SectorOutlookCard outlook={outlook} />
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Bottom sectors */}
      {report.bottomSectors.length > 0 && (
        <div>
          <div className="font-mono text-amber-400 text-xs uppercase tracking-label mb-3">
            Sectors Analysts Are Cautious On
          </div>
          <div className="space-y-3">
            {report.bottomSectors.map((outlook, i) => (
              <motion.div
                key={outlook.sector}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08, duration: 0.3 }}
              >
                <SectorOutlookCard outlook={outlook} />
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Contrarian callout */}
      {report.contrarian && (
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.35 }}
          className="bg-card border border-accent/30 rounded-card p-4"
        >
          <div className="font-mono text-accent text-[11px] uppercase tracking-label mb-1">
            Contrarian View
          </div>
          <p className="text-off text-sm italic">{report.contrarian}</p>
        </motion.div>
      )}

      {/* Disclaimer */}
      <p className="text-muted text-[11px] text-center italic">
        Market intelligence sourced from public analyst reports and financial press. All views
        attributed to their respective firms. This is not financial advice.
      </p>
    </motion.div>
  );
}
