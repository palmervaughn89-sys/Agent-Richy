'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { ConsensusLeaderboard, ConsensusRating } from '@/types/investment';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function rankColor(rank: number): string {
  if (rank === 1) return 'text-amber-400';
  if (rank === 2) return 'text-gray-300';
  if (rank === 3) return 'text-amber-600';
  return 'text-accent';
}

function scoreBarColor(score: number): string {
  if (score >= 70) return 'bg-accent';
  if (score >= 50) return 'bg-amber-400';
  return 'bg-red-400';
}

function upsideColor(upside: number): string {
  return upside >= 0 ? 'text-accent' : 'text-red-400';
}

function upsideLabel(upside: number): string {
  return upside >= 0 ? `+${upside.toFixed(1)}%` : `${upside.toFixed(1)}%`;
}

/* ── Animation variants ────────────────────────────────────────────── */

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
};

const collapse = {
  initial: { height: 0, opacity: 0 },
  animate: { height: 'auto', opacity: 1, transition: { duration: 0.25, ease: 'easeOut' } },
  exit: { height: 0, opacity: 0, transition: { duration: 0.2, ease: 'easeIn' } },
};

/* ── Chevron ───────────────────────────────────────────────────────── */

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      className={`text-muted transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
    >
      <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/* ── Mini ratings bar (buy/hold/sell) ──────────────────────────────── */

function RatingsBar({ buy, hold, sell }: { buy: number; hold: number; sell: number }) {
  const total = buy + hold + sell;
  if (total === 0) return null;
  const bPct = (buy / total) * 100;
  const hPct = (hold / total) * 100;
  const sPct = (sell / total) * 100;

  return (
    <div>
      <div className="flex h-2 rounded-full overflow-hidden">
        {bPct > 0 && <div className="bg-accent" style={{ width: `${bPct}%` }} />}
        {hPct > 0 && <div className="bg-s2" style={{ width: `${hPct}%` }} />}
        {sPct > 0 && <div className="bg-red-500/50" style={{ width: `${sPct}%` }} />}
      </div>
      <p className="text-muted text-[10px] mt-0.5 font-mono">
        {buy}B · {hold}H · {sell}S
      </p>
    </div>
  );
}

/* ── Desktop table row ─────────────────────────────────────────────── */

function DesktopRow({ stock, rank }: { stock: ConsensusRating; rank: number }) {
  return (
    <motion.div
      variants={fadeUp}
      className="hidden md:grid grid-cols-[40px_1fr_100px_100px_80px_100px] gap-2 items-center bg-card border-b border-line px-5 py-4 hover:bg-card/80 transition cursor-pointer"
    >
      {/* Rank */}
      <span className={`${rankColor(rank)} font-bold text-xl font-mono`}>
        #{rank}
      </span>

      {/* Company */}
      <div className="min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-accent font-mono font-bold">{stock.ticker}</span>
          <span className="font-mono text-[10px] bg-accent/10 text-accent px-1.5 py-0.5 rounded">
            {stock.sector}
          </span>
        </div>
        <p className="text-off text-sm truncate">{stock.companyName}</p>
      </div>

      {/* Consensus score */}
      <div>
        <span className="text-txt font-bold text-lg">{stock.consensusScore}</span>
        <div className="bg-s2 rounded-full h-1.5 w-full mt-1">
          <div
            className={`${scoreBarColor(stock.consensusScore)} h-full rounded-full transition-all`}
            style={{ width: `${stock.consensusScore}%` }}
          />
        </div>
        <p className="text-muted text-[10px] mt-0.5">{stock.consensusLabel}</p>
      </div>

      {/* Avg price target */}
      <div>
        <p className="text-txt font-medium">{fmt(stock.avgPriceTarget)}</p>
        <p className="text-muted text-[10px]">Now {fmt(stock.currentPrice)}</p>
      </div>

      {/* Implied upside */}
      <span className={`${upsideColor(stock.impliedUpside)} font-medium`}>
        {upsideLabel(stock.impliedUpside)}
      </span>

      {/* Ratings breakdown */}
      <RatingsBar buy={stock.buyCount} hold={stock.holdCount} sell={stock.sellCount} />
    </motion.div>
  );
}

/* ── Mobile card ───────────────────────────────────────────────────── */

function MobileCard({ stock, rank }: { stock: ConsensusRating; rank: number }) {
  return (
    <motion.div
      variants={fadeUp}
      className="md:hidden bg-card border border-line rounded-lg p-4"
    >
      {/* Top row: rank + ticker + score */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className={`${rankColor(rank)} font-bold text-xl font-mono`}>
            #{rank}
          </span>
          <div>
            <span className="text-accent font-mono font-bold">{stock.ticker}</span>
            <p className="text-off text-sm">{stock.companyName}</p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-txt font-bold text-lg">{stock.consensusScore}</span>
          <p className="text-muted text-[10px]">{stock.consensusLabel}</p>
        </div>
      </div>

      {/* Sector badge */}
      <div className="mt-2">
        <span className="font-mono text-[10px] bg-accent/10 text-accent px-1.5 py-0.5 rounded">
          {stock.sector}
        </span>
      </div>

      {/* Score bar */}
      <div className="bg-s2 rounded-full h-1.5 w-full mt-2">
        <div
          className={`${scoreBarColor(stock.consensusScore)} h-full rounded-full`}
          style={{ width: `${stock.consensusScore}%` }}
        />
      </div>

      {/* Metrics row */}
      <div className="flex items-center justify-between mt-3 text-sm">
        <div>
          <p className="text-muted text-[10px]">Avg Target</p>
          <p className="text-txt font-medium">{fmt(stock.avgPriceTarget)}</p>
        </div>
        <div>
          <p className="text-muted text-[10px]">Current</p>
          <p className="text-off">{fmt(stock.currentPrice)}</p>
        </div>
        <div>
          <p className="text-muted text-[10px]">Upside</p>
          <p className={`${upsideColor(stock.impliedUpside)} font-medium`}>
            {upsideLabel(stock.impliedUpside)}
          </p>
        </div>
      </div>

      {/* Ratings */}
      <div className="mt-2">
        <RatingsBar buy={stock.buyCount} hold={stock.holdCount} sell={stock.sellCount} />
      </div>
    </motion.div>
  );
}

/* ── Main component ────────────────────────────────────────────────── */

export default function ConsensusLeaderboardCard({
  leaderboard,
}: {
  leaderboard: ConsensusLeaderboard;
}) {
  const [methodOpen, setMethodOpen] = useState(false);
  const sorted = [...leaderboard.topRated].sort((a, b) => b.consensusScore - a.consensusScore);
  const sortedSectors = [...leaderboard.sectorBreakdown].sort((a, b) => b.avgConsensusScore - a.avgConsensusScore);
  const maxSectorScore = sortedSectors.length > 0 ? sortedSectors[0].avgConsensusScore : 100;

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={stagger}
      className="bg-card border border-line rounded-card overflow-hidden"
    >
      {/* ── 1. HEADER ─────────────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="bg-s1 rounded-t-card p-6">
        <p className="font-mono text-accent text-xs uppercase tracking-widest">
          ANALYST CONSENSUS
        </p>
        <h3 className="text-2xl font-bold text-txt mt-1">
          Top Rated Stocks — {leaderboard.category}
        </h3>
        <p className="text-muted text-sm mt-1">{leaderboard.timeframe}</p>
        <p className="text-off text-sm mt-0.5">
          {leaderboard.sources.length} firms contributing ratings
        </p>
      </motion.div>

      {/* ── 2. LEADERBOARD TABLE ──────────────────────────────────── */}
      <div>
        {/* Desktop header */}
        <div className="hidden md:grid grid-cols-[40px_1fr_100px_100px_80px_100px] gap-2 bg-s2 px-5 py-3">
          {['Rank', 'Company', 'Consensus', 'Avg Target', 'Upside', 'Ratings'].map((h) => (
            <span key={h} className="text-muted font-mono text-[11px] uppercase tracking-widest">
              {h}
            </span>
          ))}
        </div>

        {/* Desktop rows */}
        {sorted.map((stock, i) => (
          <DesktopRow key={stock.ticker} stock={stock} rank={i + 1} />
        ))}

        {/* Mobile cards */}
        <div className="md:hidden p-4 space-y-3">
          {sorted.map((stock, i) => (
            <MobileCard key={stock.ticker} stock={stock} rank={i + 1} />
          ))}
        </div>
      </div>

      <div className="p-5 space-y-4">
        {/* ── 3. SECTOR BREAKDOWN ───────────────────────────────────── */}
        {sortedSectors.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">
              BY SECTOR
            </p>
            <div className="space-y-2">
              {sortedSectors.map((s) => (
                <div key={s.sector} className="flex items-center gap-3">
                  <span className="text-off text-sm w-28 shrink-0 truncate">{s.sector}</span>
                  <div className="flex-1 bg-s2 rounded-full h-2.5 overflow-hidden">
                    <div
                      className={`${scoreBarColor(s.avgConsensusScore)} h-full rounded-full transition-all`}
                      style={{ width: `${(s.avgConsensusScore / maxSectorScore) * 100}%` }}
                    />
                  </div>
                  <span className="text-txt font-medium text-sm w-8 text-right">{s.avgConsensusScore}</span>
                  <span className="text-accent font-mono text-xs w-12 text-right">{s.topPick}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── 4. METHODOLOGY (collapsible) ──────────────────────────── */}
        <motion.div variants={fadeUp}>
          <button
            onClick={() => setMethodOpen(!methodOpen)}
            className="w-full flex items-center justify-between cursor-pointer group"
          >
            <span className="text-muted text-sm group-hover:text-off transition-colors">
              How scores are calculated
            </span>
            <Chevron open={methodOpen} />
          </button>

          <AnimatePresence>
            {methodOpen && (
              <motion.div
                key="method"
                variants={collapse}
                initial="initial"
                animate="animate"
                exit="exit"
                className="overflow-hidden"
              >
                <div className="bg-s1 rounded-lg p-4 mt-2 space-y-3">
                  <p className="text-off text-sm">{leaderboard.methodology}</p>
                  <div>
                    <p className="text-muted text-xs font-mono uppercase tracking-widest mb-1">
                      Contributing Firms
                    </p>
                    <p className="text-off text-sm">
                      {leaderboard.sources.join(' · ')}
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* ── 5. DISCLAIMER ─────────────────────────────────────────── */}
        <motion.div variants={fadeUp}>
          <div className="bg-s1 rounded-lg p-3 text-center">
            <p className="text-muted text-[11px] italic">
              {leaderboard.disclaimer}
            </p>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
