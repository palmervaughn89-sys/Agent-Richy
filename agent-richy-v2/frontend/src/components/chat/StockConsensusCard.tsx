'use client';

import { motion } from 'framer-motion';
import type { ConsensusRating, FirmRating, AnalystRating } from '@/types/investment';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 });
}

function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return iso;
  }
}

function scoreRingColor(score: number): string {
  if (score >= 70) return '#00E87B';
  if (score >= 50) return '#FBBF24';
  return '#F87171';
}

function scoreBarCss(score: number): string {
  if (score >= 70) return 'bg-accent';
  if (score >= 50) return 'bg-amber-400';
  return 'bg-red-400';
}

function ratingBadge(rating: AnalystRating): { bg: string; text: string; label: string } {
  switch (rating) {
    case 'strong_buy':  return { bg: 'bg-accent/20',          text: 'text-accent',    label: 'Strong Buy' };
    case 'buy':         return { bg: 'bg-accent/15',          text: 'text-accent',    label: 'Buy' };
    case 'overweight':  return { bg: 'bg-accent/10',          text: 'text-accent',    label: 'Overweight' };
    case 'hold':        return { bg: 'bg-s2',                 text: 'text-off',       label: 'Hold' };
    case 'underweight': return { bg: 'bg-amber-500/15',       text: 'text-amber-400', label: 'Underweight' };
    case 'sell':        return { bg: 'bg-red-500/15',         text: 'text-red-400',   label: 'Sell' };
    case 'strong_sell': return { bg: 'bg-red-500/20',         text: 'text-red-400',   label: 'Strong Sell' };
  }
}

/* ── Animation ─────────────────────────────────────────────────────── */

const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const fadeUp  = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } } };

/* ── SVG Gauge ─────────────────────────────────────────────────────── */

function ScoreGauge({ score, label }: { score: number; label: string }) {
  const r = 54;
  const C = 2 * Math.PI * r;
  const offset = C - (score / 100) * C;
  const color = scoreRingColor(score);

  return (
    <div className="flex flex-col items-center">
      <svg width="130" height="130" viewBox="0 0 130 130">
        <circle cx="65" cy="65" r={r} fill="none" stroke="currentColor" strokeWidth="8" className="text-s2" />
        <circle
          cx="65" cy="65" r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={C}
          strokeDashoffset={offset}
          transform="rotate(-90 65 65)"
          className="transition-all duration-700"
        />
        <text x="65" y="62" textAnchor="middle" dominantBaseline="central" fill="currentColor" className="text-txt text-3xl font-bold" fontSize="32" fontWeight="700">
          {score}
        </text>
        <text x="65" y="85" textAnchor="middle" fill="currentColor" className="text-muted" fontSize="10">
          / 100
        </text>
      </svg>
      <p className="text-muted text-sm mt-1">{label}</p>
    </div>
  );
}

/* ── Rating distribution bars ──────────────────────────────────────── */

function RatingDist({ buy, hold, sell }: { buy: number; hold: number; sell: number }) {
  const max = Math.max(buy, hold, sell, 1);
  const items = [
    { label: 'Buy', count: buy, color: 'bg-accent' },
    { label: 'Hold', count: hold, color: 'bg-s2' },
    { label: 'Sell', count: sell, color: 'bg-red-500/60' },
  ];

  return (
    <div className="space-y-2 flex-1 min-w-[140px]">
      {items.map((it) => (
        <div key={it.label} className="flex items-center gap-2">
          <span className="text-off text-xs w-8 text-right">{it.label}</span>
          <div className="flex-1 bg-s2/40 rounded-full h-3 overflow-hidden">
            <div className={`${it.color} h-full rounded-full transition-all`} style={{ width: `${(it.count / max) * 100}%` }} />
          </div>
          <span className="text-txt text-xs font-mono w-5">{it.count}</span>
        </div>
      ))}
    </div>
  );
}

/* ── Price target range bar ────────────────────────────────────────── */

function PriceRange({ low, median, avg, high, current }: { low: number; median: number; avg: number; high: number; current: number }) {
  const min = Math.min(low, current) * 0.95;
  const maxVal = Math.max(high, current) * 1.05;
  const range = maxVal - min;
  const pct = (v: number) => ((v - min) / range) * 100;

  return (
    <div className="relative mt-3 mb-6">
      {/* Track */}
      <div className="h-2 bg-s2 rounded-full relative">
        {/* Range fill */}
        <div
          className="absolute h-full bg-accent/30 rounded-full"
          style={{ left: `${pct(low)}%`, width: `${pct(high) - pct(low)}%` }}
        />
      </div>

      {/* Markers */}
      {[
        { val: low, label: `Low ${fmt(low)}`, side: 'left' as const },
        { val: median, label: `Med ${fmt(median)}`, side: 'left' as const },
        { val: avg, label: `Avg ${fmt(avg)}`, side: 'right' as const },
        { val: high, label: `High ${fmt(high)}`, side: 'right' as const },
      ].map((m, i) => (
        <div key={i} className="absolute" style={{ left: `${pct(m.val)}%`, top: 0, transform: 'translateX(-50%)' }}>
          <div className="w-0.5 h-4 bg-accent/50 mx-auto" />
          <p className="text-muted text-[10px] whitespace-nowrap mt-0.5">{m.label}</p>
        </div>
      ))}

      {/* Current price line */}
      <div className="absolute" style={{ left: `${pct(current)}%`, top: '-4px', transform: 'translateX(-50%)' }}>
        <div className="w-0.5 h-6 bg-txt mx-auto" />
        <p className="text-txt text-[10px] font-bold whitespace-nowrap mt-0.5">Now {fmt(current)}</p>
      </div>
    </div>
  );
}

/* ── Firm row ──────────────────────────────────────────────────────── */

function FirmRow({ firm }: { firm: FirmRating }) {
  const badge = ratingBadge(firm.rating);
  return (
    <motion.div variants={fadeUp} className="bg-s1 rounded-lg p-3 flex items-center justify-between gap-3 flex-wrap">
      <span className="text-off font-medium min-w-[120px]">{firm.sourceName}</span>
      <span className={`${badge.bg} ${badge.text} text-xs font-mono px-2 py-0.5 rounded`}>{badge.label}</span>
      {firm.priceTarget != null && <span className="text-txt text-sm">{fmt(firm.priceTarget)}</span>}
      <span className="text-muted text-xs">{fmtDate(firm.dateIssued)}</span>
      {firm.sourceUrl && (
        <a href={firm.sourceUrl} target="_blank" rel="noopener noreferrer" className="text-accent hover:underline text-xs">
          ↗
        </a>
      )}
    </motion.div>
  );
}

/* ── Morningstar stars ─────────────────────────────────────────────── */

function Stars({ count }: { count: number }) {
  return (
    <span className="inline-flex gap-0.5">
      {[1, 2, 3, 4, 5].map((n) => (
        <span key={n} className={n <= count ? 'text-accent' : 'text-s2'}>★</span>
      ))}
    </span>
  );
}

/* ── Metric card ───────────────────────────────────────────────────── */

function Metric({ label, value, tone }: { label: string; value: string; tone?: 'good' | 'bad' | 'neutral' }) {
  const color = tone === 'good' ? 'text-accent' : tone === 'bad' ? 'text-red-400' : 'text-txt';
  return (
    <div className="bg-s1 rounded-lg p-3 text-center">
      <p className="text-muted text-[10px] font-mono uppercase tracking-widest">{label}</p>
      <p className={`${color} font-medium text-sm mt-1`}>{value}</p>
    </div>
  );
}

/* ── Main component ────────────────────────────────────────────────── */

export default function StockConsensusCard({ stock }: { stock: ConsensusRating }) {
  const hasMorningstar = stock.morningstarStars != null;

  // Morningstar valuation label
  let morningstarValuation = '';
  if (hasMorningstar && stock.morningstarFairValue != null) {
    const ratio = stock.currentPrice / stock.morningstarFairValue;
    if (ratio < 0.9) morningstarValuation = 'undervalued';
    else if (ratio > 1.1) morningstarValuation = 'overvalued';
    else morningstarValuation = 'fairly valued';
  }

  // Metric tone helpers
  const peTone = (pe?: number) => {
    if (pe == null) return 'neutral' as const;
    return pe < 20 ? 'good' as const : pe > 40 ? 'bad' as const : 'neutral' as const;
  };
  const betaTone = (b?: number) => {
    if (b == null) return 'neutral' as const;
    return b <= 1.0 ? 'good' as const : b > 1.5 ? 'bad' as const : 'neutral' as const;
  };
  const growthTone = (g?: number) => {
    if (g == null) return 'neutral' as const;
    return g > 10 ? 'good' as const : g < 0 ? 'bad' as const : 'neutral' as const;
  };

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={stagger}
      className="bg-card border border-line rounded-card overflow-hidden"
    >
      {/* ── 1. HEADER ─────────────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="bg-s1 rounded-t-card p-5">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <h3 className="text-accent font-mono text-3xl font-bold">{stock.ticker}</h3>
            <p className="text-txt text-lg">{stock.companyName}</p>
          </div>
          <div className="text-right">
            <p className="text-off text-xl font-medium">{fmt(stock.currentPrice)}</p>
            <span className={`${stock.impliedUpside >= 0 ? 'text-accent' : 'text-red-400'} text-sm font-medium`}>
              {stock.impliedUpside >= 0 ? '▲' : '▼'} {Math.abs(stock.impliedUpside).toFixed(1)}% to avg target
            </span>
          </div>
        </div>
        <div className="mt-2">
          <span className="font-mono text-accent text-xs bg-accent/10 px-2 py-1 rounded">
            {stock.sector}
          </span>
        </div>
      </motion.div>

      <div className="p-5 space-y-4">
        {/* ── 2. CONSENSUS SCORE ─────────────────────────────────────── */}
        <motion.div variants={fadeUp} className="flex items-center gap-6 flex-wrap justify-center sm:justify-start">
          <ScoreGauge score={stock.consensusScore} label={stock.consensusLabel} />
          <RatingDist buy={stock.buyCount} hold={stock.holdCount} sell={stock.sellCount} />
        </motion.div>

        {/* ── 3. PRICE TARGETS ──────────────────────────────────────── */}
        <motion.div variants={fadeUp} className="bg-card border border-line rounded-card p-4">
          <p className="font-mono text-accent text-xs uppercase tracking-widest mb-2">PRICE TARGETS</p>

          {stock.currentPrice < stock.lowPriceTarget && (
            <p className="text-accent text-sm mb-2">Trading below all analyst targets</p>
          )}
          {stock.currentPrice > stock.highPriceTarget && (
            <p className="text-amber-400 text-sm mb-2">Trading above all analyst targets</p>
          )}

          <PriceRange
            low={stock.lowPriceTarget}
            median={stock.medianPriceTarget}
            avg={stock.avgPriceTarget}
            high={stock.highPriceTarget}
            current={stock.currentPrice}
          />

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
            <Metric label="Avg Target" value={fmt(stock.avgPriceTarget)} />
            <Metric label="High Target" value={fmt(stock.highPriceTarget)} />
            <Metric label="Low Target" value={fmt(stock.lowPriceTarget)} />
            <Metric label="Implied Upside" value={`${stock.impliedUpside >= 0 ? '+' : ''}${stock.impliedUpside.toFixed(1)}%`} tone={stock.impliedUpside >= 0 ? 'good' : 'bad'} />
          </div>
        </motion.div>

        {/* ── 4. FIRM RATINGS ───────────────────────────────────────── */}
        {stock.ratings.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">WHAT EACH FIRM SAYS</p>
            <div className="space-y-2">
              {stock.ratings.map((firm, i) => (
                <FirmRow key={`${firm.source}-${i}`} firm={firm} />
              ))}
            </div>
          </motion.div>
        )}

        {/* ── 5. MORNINGSTAR ────────────────────────────────────────── */}
        {hasMorningstar && (
          <motion.div variants={fadeUp} className="bg-s1 rounded-lg p-4">
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-2">MORNINGSTAR</p>
            <div className="flex items-center gap-4 flex-wrap">
              <Stars count={stock.morningstarStars!} />
              {stock.morningstarFairValue != null && (
                <span className="text-off text-sm">
                  Fair Value: <span className="text-txt font-medium">{fmt(stock.morningstarFairValue)}</span>
                </span>
              )}
              {stock.morningstarMoat && (
                <span className="font-mono text-[10px] bg-accent/10 text-accent px-1.5 py-0.5 rounded uppercase">
                  {stock.morningstarMoat} moat
                </span>
              )}
            </div>
            {morningstarValuation && (
              <p className="text-off text-sm mt-2">
                Morningstar considers this <span className={morningstarValuation === 'undervalued' ? 'text-accent font-medium' : morningstarValuation === 'overvalued' ? 'text-amber-400 font-medium' : 'text-off font-medium'}>{morningstarValuation}</span>
              </p>
            )}
          </motion.div>
        )}

        {/* ── 6. KEY METRICS ────────────────────────────────────────── */}
        <motion.div variants={fadeUp}>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {stock.peRatio != null && <Metric label="P/E Ratio" value={stock.peRatio.toFixed(1)} tone={peTone(stock.peRatio)} />}
            {stock.forwardPE != null && <Metric label="Forward P/E" value={stock.forwardPE.toFixed(1)} tone={peTone(stock.forwardPE)} />}
            {stock.dividendYield != null && <Metric label="Div Yield" value={`${stock.dividendYield.toFixed(2)}%`} tone={stock.dividendYield > 0 ? 'good' : 'neutral'} />}
            {stock.beta != null && <Metric label="Beta" value={stock.beta.toFixed(2)} tone={betaTone(stock.beta)} />}
            {stock.marketCap != null && <Metric label="Market Cap" value={stock.marketCap} />}
            {stock.revenueGrowthYoY != null && <Metric label="Rev Growth" value={`${stock.revenueGrowthYoY > 0 ? '+' : ''}${stock.revenueGrowthYoY.toFixed(1)}%`} tone={growthTone(stock.revenueGrowthYoY)} />}
          </div>
        </motion.div>

        {/* ── 7. BULL vs BEAR ───────────────────────────────────────── */}
        <motion.div variants={fadeUp} className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="bg-accent/5 border border-accent/20 rounded-card p-4">
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-2">BULL CASE</p>
            <p className="text-off text-sm">{stock.bullCase}</p>
          </div>
          <div className="bg-red-500/5 border border-red-500/20 rounded-card p-4">
            <p className="font-mono text-red-400 text-xs uppercase tracking-widest mb-2">BEAR CASE</p>
            <p className="text-off text-sm">{stock.bearCase}</p>
          </div>
        </motion.div>

        {/* ── 8. DISCLAIMER ─────────────────────────────────────────── */}
        <motion.div variants={fadeUp}>
          <p className="text-muted text-[11px] italic text-center">{stock.disclaimer}</p>
        </motion.div>
      </div>
    </motion.div>
  );
}
