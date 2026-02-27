'use client';

import { motion } from 'framer-motion';
import type { SectorConsensus } from '@/types/investment';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function pct(n: number): string {
  return `${n >= 0 ? '+' : ''}${n.toFixed(1)}%`;
}

function consensusBadge(view: 'overweight' | 'equal_weight' | 'underweight') {
  switch (view) {
    case 'overweight':
      return { bg: 'bg-accent/15', text: 'text-accent', label: 'Overweight' };
    case 'equal_weight':
      return { bg: 'bg-s2', text: 'text-off', label: 'Equal Weight' };
    case 'underweight':
      return { bg: 'bg-red-500/15', text: 'text-red-400', label: 'Underweight' };
  }
}

function ratingColor(rating: 'overweight' | 'equal_weight' | 'underweight'): string {
  if (rating === 'overweight') return 'text-accent';
  if (rating === 'underweight') return 'text-red-400';
  return 'text-off';
}

function scoreBarColor(score: number): string {
  if (score >= 70) return 'bg-accent';
  if (score >= 50) return 'bg-amber-400';
  return 'bg-red-400';
}

function toneCss(value: number, goodAbove: number, badBelow: number): 'text-accent' | 'text-red-400' | 'text-txt' {
  if (value > goodAbove) return 'text-accent';
  if (value < badBelow) return 'text-red-400';
  return 'text-txt';
}

/* ── Animation ─────────────────────────────────────────────────────── */

const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const fadeUp = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } } };

/* ── Component ─────────────────────────────────────────────────────── */

export default function SectorConsensusCard({ sector }: { sector: SectorConsensus }) {
  const badge = consensusBadge(sector.consensusView);

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={stagger}
      className="bg-card border border-line rounded-card overflow-hidden"
    >
      {/* ── HEADER ────────────────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="bg-s1 rounded-t-card p-5">
        <p className="font-mono text-accent text-xs uppercase tracking-widest">SECTOR VIEW</p>
        <div className="flex items-center gap-3 mt-1 flex-wrap">
          <h3 className="text-2xl font-bold text-txt">{sector.sectorName}</h3>
          <span className={`${badge.bg} ${badge.text} text-sm font-mono font-bold px-3 py-1 rounded-full`}>
            {badge.label}
          </span>
        </div>
        <p className="text-muted text-sm mt-1">
          {sector.overweightCount} overweight · {sector.equalWeightCount} equal weight · {sector.underweightCount} underweight
        </p>
      </motion.div>

      <div className="p-5 space-y-4">
        {/* ── FIRM VIEWS ──────────────────────────────────────────── */}
        {sector.firmViews.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">FIRM VIEWS</p>
            <div className="space-y-2">
              {sector.firmViews.map((fv, i) => (
                <motion.div key={i} variants={fadeUp} className="bg-s1 rounded-lg p-3 flex items-start gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-off font-medium">{fv.sourceName}</span>
                      <span className={`${ratingColor(fv.sectorRating)} font-mono text-[10px] uppercase`}>
                        {fv.sectorRating.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-muted text-sm mt-0.5">{fv.keyReason}</p>
                  </div>
                  <span className="text-muted text-xs shrink-0">
                    {new Date(fv.dateIssued).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── SECTOR METRICS ──────────────────────────────────────── */}
        <motion.div variants={fadeUp}>
          <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">SECTOR METRICS</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-s1 rounded-lg p-3 text-center">
              <p className="text-muted text-[10px] font-mono uppercase tracking-widest">P/E Ratio</p>
              <p className={`${toneCss(sector.sectorMetrics.peRatio, 0, 40)} font-medium text-sm mt-1`}>
                {sector.sectorMetrics.peRatio.toFixed(1)}
              </p>
            </div>
            <div className="bg-s1 rounded-lg p-3 text-center">
              <p className="text-muted text-[10px] font-mono uppercase tracking-widest">YTD Return</p>
              <p className={`${toneCss(sector.sectorMetrics.ytdReturn, 0, 0)} font-medium text-sm mt-1`}>
                {pct(sector.sectorMetrics.ytdReturn)}
              </p>
            </div>
            <div className="bg-s1 rounded-lg p-3 text-center">
              <p className="text-muted text-[10px] font-mono uppercase tracking-widest">Div Yield</p>
              <p className={`${sector.sectorMetrics.dividendYield > 0 ? 'text-accent' : 'text-txt'} font-medium text-sm mt-1`}>
                {sector.sectorMetrics.dividendYield.toFixed(2)}%
              </p>
            </div>
            <div className="bg-s1 rounded-lg p-3 text-center">
              <p className="text-muted text-[10px] font-mono uppercase tracking-widest">EPS Growth</p>
              <p className={`${toneCss(sector.sectorMetrics.earningsGrowth, 5, 0)} font-medium text-sm mt-1`}>
                {pct(sector.sectorMetrics.earningsGrowth)}
              </p>
            </div>
          </div>
        </motion.div>

        {/* ── TOP PICKS ───────────────────────────────────────────── */}
        {sector.topPicks.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">TOP PICKS</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {sector.topPicks.slice(0, 5).map((stock) => (
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
                  <div className="flex items-center justify-between mt-2 text-xs">
                    <span className="text-muted">{fmt(stock.currentPrice)}</span>
                    <span className={stock.impliedUpside >= 0 ? 'text-accent' : 'text-red-400'}>
                      {stock.impliedUpside >= 0 ? '+' : ''}{stock.impliedUpside.toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-muted text-[10px] mt-1">{stock.consensusLabel} · {stock.buyCount}B {stock.holdCount}H {stock.sellCount}S</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── CATALYSTS ───────────────────────────────────────────── */}
        {sector.catalysts.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">CATALYSTS</p>
            <div className="space-y-1.5">
              {sector.catalysts.map((c, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-accent text-sm mt-0.5">▸</span>
                  <p className="text-off text-sm">{c}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── RISKS ───────────────────────────────────────────────── */}
        {sector.risks.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-red-400 text-xs uppercase tracking-widest mb-3">RISKS</p>
            <div className="space-y-1.5">
              {sector.risks.map((r, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-red-400 text-sm mt-0.5">▸</span>
                  <p className="text-off text-sm">{r}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── DISCLAIMER ──────────────────────────────────────────── */}
        <motion.div variants={fadeUp}>
          <p className="text-muted text-[11px] italic text-center">
            Sector views aggregated from publicly available analyst research. All ratings belong to their respective firms. This is educational content, not investment advice.
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
}
