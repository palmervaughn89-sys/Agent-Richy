'use client';

import { motion } from 'framer-motion';
import type { InvestmentTheme } from '@/types/investment';

/* ── Helpers ───────────────────────────────────────────────────────── */

function horizonLabel(h: InvestmentTheme['timeHorizon']): string {
  switch (h) {
    case 'near_term':   return 'Near-Term (0-6 mo)';
    case 'medium_term': return 'Medium-Term (6-18 mo)';
    case 'long_term':   return 'Long-Term (18+ mo)';
  }
}

function riskBadge(level: InvestmentTheme['riskLevel']): { bg: string; text: string; label: string } {
  switch (level) {
    case 'low':         return { bg: 'bg-accent/15',     text: 'text-accent',    label: 'Low Risk' };
    case 'moderate':    return { bg: 'bg-amber-400/15',  text: 'text-amber-400', label: 'Moderate Risk' };
    case 'high':        return { bg: 'bg-red-500/15',    text: 'text-red-400',   label: 'High Risk' };
    case 'speculative': return { bg: 'bg-red-500/20',    text: 'text-red-400',   label: 'Speculative' };
  }
}

function scoreBarColor(score: number): string {
  if (score >= 70) return 'bg-accent';
  if (score >= 50) return 'bg-amber-400';
  return 'bg-red-400';
}

/* ── Animation ─────────────────────────────────────────────────────── */

const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const fadeUp = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } } };

/* ── Component ─────────────────────────────────────────────────────── */

export default function InvestmentThemeCard({ theme }: { theme: InvestmentTheme }) {
  const risk = riskBadge(theme.riskLevel);

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={stagger}
      className="bg-card border border-line rounded-card overflow-hidden"
    >
      {/* ── HEADER ────────────────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="bg-s1 rounded-t-card p-5">
        <p className="font-mono text-accent text-xs uppercase tracking-widest">INVESTMENT THEME</p>
        <h3 className="text-2xl font-bold text-txt mt-1">{theme.themeName}</h3>
        <p className="text-off text-sm mt-2">{theme.description}</p>
        <div className="flex items-center gap-2 mt-3 flex-wrap">
          <span className="bg-s2 text-off text-xs font-mono px-2 py-1 rounded">
            {horizonLabel(theme.timeHorizon)}
          </span>
          <span className={`${risk.bg} ${risk.text} text-xs font-mono px-2 py-1 rounded`}>
            {risk.label}
          </span>
        </div>
      </motion.div>

      <div className="p-5 space-y-4">
        {/* ── FIRMS BACKING THIS THEME ────────────────────────────── */}
        {theme.supportingFirms.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">FIRMS BACKING THIS THEME</p>
            <div className="space-y-2">
              {theme.supportingFirms.map((firm, i) => (
                <motion.div key={i} variants={fadeUp} className="bg-s1 rounded-lg p-3">
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <span className="text-off font-medium">{firm.sourceName}</span>
                    <span className="text-muted text-xs">
                      {new Date(firm.datePublished).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                    </span>
                  </div>
                  <p className="text-muted text-sm mt-1">{firm.thesis}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── RELATED STOCKS ──────────────────────────────────────── */}
        {theme.relatedStocks.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">RELATED STOCKS</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {theme.relatedStocks.map((stock) => (
                <motion.div key={stock.ticker} variants={fadeUp} className="bg-card border border-line rounded-lg p-4">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-accent font-mono font-bold">{stock.ticker}</span>
                    <span className="text-txt font-bold">{stock.consensusScore}</span>
                  </div>
                  <p className="text-off text-sm truncate">{stock.companyName}</p>
                  <div className="bg-s2 rounded-full h-1.5 w-full mt-2">
                    <div
                      className={`${scoreBarColor(stock.consensusScore)} h-full rounded-full`}
                      style={{ width: `${stock.consensusScore}%` }}
                    />
                  </div>
                  <p className="text-muted text-xs mt-2">{stock.connection}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── DISCLAIMER ──────────────────────────────────────────── */}
        <motion.div variants={fadeUp}>
          <p className="text-muted text-[11px] italic text-center">
            Investment themes are aggregated from publicly available research by the listed firms. All views belong to their respective institutions. This is educational content, not investment advice.
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
}
