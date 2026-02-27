'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import type { PurchaseTimingAdvice } from '@/types/economicIntel';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function fmtDec(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/* ── Animation ─────────────────────────────────────────────────────── */

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
};

/* ── Verdict Badge ─────────────────────────────────────────────────── */

function VerdictBadge({ timing }: { timing: 'buy_now' | 'wait' | 'urgent' }) {
  const config: Record<string, { label: string; cls: string }> = {
    buy_now: { label: 'BUY NOW', cls: 'text-accent bg-accent/10' },
    wait: { label: 'WAIT', cls: 'text-amber-400 bg-amber-400/10' },
    urgent: { label: 'URGENT — BUY BEFORE PRICE INCREASE', cls: 'text-red-400 bg-red-400/10' },
  };
  const { label, cls } = config[timing] ?? config.buy_now;
  return (
    <span className={`inline-block font-mono font-bold text-lg rounded-full px-6 py-2 ${cls}`}>
      {label}
    </span>
  );
}

/* ── Star Rating ───────────────────────────────────────────────────── */

function Stars({ rating }: { rating: number }) {
  return (
    <span className="inline-flex gap-0.5">
      {[1, 2, 3, 4, 5].map((s) => (
        <span key={s} className={s <= rating ? 'text-accent' : 'text-white/10'}>★</span>
      ))}
    </span>
  );
}

/* ── Forecast Bar ──────────────────────────────────────────────────── */

function ForecastBar({ label, price, confidence, currentPrice, maxPrice }: {
  label: string;
  price: number;
  confidence: number;
  currentPrice: number;
  maxPrice: number;
}) {
  const barWidth = maxPrice > 0 ? (price / maxPrice) * 100 : 0;
  const currentWidth = maxPrice > 0 ? (currentPrice / maxPrice) * 100 : 0;
  const diff = price - currentPrice;
  const isLower = diff < 0;

  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-off text-xs">{label}</span>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-medium ${isLower ? 'text-accent' : diff > 0 ? 'text-red-400' : 'text-off'}`}>
            {fmtDec(price)}
          </span>
          <span className="text-muted text-[10px]">{Math.round(confidence * 100)}% conf.</span>
        </div>
      </div>
      <div className="relative h-3 bg-white/5 rounded-full overflow-hidden">
        {/* Current price marker */}
        <div
          className="absolute top-0 bottom-0 w-px bg-txt/40 z-10"
          style={{ left: `${currentWidth}%` }}
        />
        {/* Forecast bar */}
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${barWidth}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className={`h-full rounded-full ${isLower ? 'bg-accent/40' : diff > 0 ? 'bg-red-400/40' : 'bg-blue-400/40'}`}
        />
      </div>
    </div>
  );
}

/* ── Current Month Info ────────────────────────────────────────────── */

function getCurrentMonthRating(bestMonth: string, worstMonth: string): number {
  // Simple heuristic: extract current month name and check mentions
  const months = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];
  const now = months[new Date().getMonth()];
  if (bestMonth.includes(now)) return 5;
  if (worstMonth.includes(now)) return 1;
  return 3;
}

/* ── Main Component ────────────────────────────────────────────────── */

interface PurchaseTimingCardProps {
  timing: PurchaseTimingAdvice;
}

export default function PurchaseTimingCard({ timing }: PurchaseTimingCardProps) {
  const maxPrice = useMemo(() => {
    const prices = [
      timing.currentPrice,
      timing.priceForecast.weeks2.price,
      timing.priceForecast.weeks4.price,
      timing.priceForecast.months3.price,
    ];
    return Math.max(...prices) * 1.1; // 10% headroom
  }, [timing]);

  const currentMonthRating = useMemo(
    () => getCurrentMonthRating(timing.bestMonthToBuy, timing.worstMonthToBuy),
    [timing.bestMonthToBuy, timing.worstMonthToBuy],
  );

  return (
    <motion.div
      variants={stagger}
      initial="hidden"
      animate="show"
      className="bg-card border border-line rounded-[14px] p-5"
    >
      {/* ── Verdict ────────────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="text-center mb-4">
        <p className="text-off text-xs mb-2">Should you buy <span className="text-txt font-medium">{timing.item}</span> right now?</p>
        <VerdictBadge timing={timing.timing} />
      </motion.div>

      {/* ── Reason ─────────────────────────────────────────────── */}
      <motion.p variants={fadeUp} className="text-off text-sm text-center leading-relaxed mt-3">
        {timing.reason}
      </motion.p>

      {/* ── Current Price ──────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="text-center mt-4 mb-1">
        <span className="text-muted text-xs">Current price</span>
        <p className="text-txt text-xl font-bold">{fmtDec(timing.currentPrice)}</p>
      </motion.div>

      {/* ── Price Forecast ─────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="mt-4">
        <p className="font-mono text-accent text-[10px] tracking-[0.08em] uppercase mb-3">
          Price Forecast
        </p>
        <ForecastBar
          label="In 2 weeks"
          price={timing.priceForecast.weeks2.price}
          confidence={timing.priceForecast.weeks2.confidence}
          currentPrice={timing.currentPrice}
          maxPrice={maxPrice}
        />
        <ForecastBar
          label="In 4 weeks"
          price={timing.priceForecast.weeks4.price}
          confidence={timing.priceForecast.weeks4.confidence}
          currentPrice={timing.currentPrice}
          maxPrice={maxPrice}
        />
        <ForecastBar
          label="In 3 months"
          price={timing.priceForecast.months3.price}
          confidence={timing.priceForecast.months3.confidence}
          currentPrice={timing.currentPrice}
          maxPrice={maxPrice}
        />
        <div className="flex items-center gap-2 mt-1">
          <div className="w-px h-3 bg-txt/40" />
          <span className="text-muted text-[10px]">Current price line</span>
        </div>
      </motion.div>

      {/* ── Seasonal Context ───────────────────────────────────── */}
      <motion.div variants={fadeUp} className="mt-4 bg-s1 rounded-lg p-3">
        <p className="font-mono text-accent text-[10px] tracking-[0.08em] uppercase mb-2">
          Seasonal Context
        </p>
        <div className="space-y-1.5">
          <div className="flex items-start gap-2">
            <span className="text-accent text-sm">✓</span>
            <p className="text-off text-xs leading-relaxed">
              <span className="text-txt font-medium">Best time to buy:</span> {timing.bestMonthToBuy}
            </p>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-red-400 text-sm">✗</span>
            <p className="text-off text-xs leading-relaxed">
              <span className="text-txt font-medium">Worst time:</span> {timing.worstMonthToBuy}
            </p>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-off text-xs">This month&apos;s rating:</span>
            <Stars rating={currentMonthRating} />
          </div>
        </div>
        {/* Supply / demand */}
        <div className="flex gap-3 mt-3">
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
            timing.demandLevel === 'low' ? 'text-accent border-accent/20 bg-accent/5'
            : timing.demandLevel === 'high' ? 'text-red-400 border-red-400/20 bg-red-400/5'
            : 'text-off border-white/10 bg-white/5'
          }`}>
            Demand: {timing.demandLevel}
          </span>
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
            timing.supplyLevel === 'excess' ? 'text-accent border-accent/20 bg-accent/5'
            : timing.supplyLevel === 'tight' ? 'text-red-400 border-red-400/20 bg-red-400/5'
            : 'text-off border-white/10 bg-white/5'
          }`}>
            Supply: {timing.supplyLevel}
          </span>
        </div>
      </motion.div>

      {/* ── Alternatives ───────────────────────────────────────── */}
      {timing.alternatives.length > 0 && (
        <motion.div variants={fadeUp} className="mt-4">
          <p className="font-mono text-accent text-[10px] tracking-[0.08em] uppercase mb-2">
            Alternatives
          </p>
          <div className="space-y-2">
            {timing.alternatives.map((alt) => (
              <div
                key={alt.name}
                className="bg-s1 rounded-lg p-3 flex items-center justify-between gap-3"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-txt text-sm font-medium">{alt.name}</p>
                  <p className="text-off text-xs mt-0.5">{alt.tradeoff}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-txt text-sm font-medium">{fmtDec(alt.price)}</p>
                  <p className="text-accent text-xs">Save {fmt(alt.savings)}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
