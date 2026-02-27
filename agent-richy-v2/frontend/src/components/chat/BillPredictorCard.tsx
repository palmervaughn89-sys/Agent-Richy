'use client';

import { useRef } from 'react';
import { motion } from 'framer-motion';
import type { BillPrediction } from '@/types/tools';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

function dayName(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', { weekday: 'short' });
  } catch {
    return '';
  }
}

function dayNum(iso: string): string {
  try {
    return new Date(iso).getDate().toString();
  } catch {
    return iso;
  }
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return iso;
  }
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

/* ── Component ─────────────────────────────────────────────────────── */

export default function BillPredictorCard({
  prediction,
}: {
  prediction: BillPrediction;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);

  const diff = prediction.comparedToLastMonth;
  const diffPct = prediction.comparedToLastMonthPercent;
  const warningDates = new Set(prediction.cashFlowWarnings.map((w) => w.date));

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={stagger}
      className="bg-card border border-line rounded-card overflow-hidden"
    >
      {/* ── 1. HEADER ─────────────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="bg-s1 rounded-t-card p-5">
        <h3 className="text-xl font-bold text-txt">
          {prediction.period} Bill Forecast
        </h3>
        <p className="text-3xl font-bold text-accent mt-1">
          {fmt(prediction.totalPredicted)}
        </p>
        <p className="text-sm mt-1">
          {diff > 0 && (
            <span className="text-amber-400">
              ↑ {fmt(Math.abs(diff))} more than last month (+{Math.abs(diffPct)}%)
            </span>
          )}
          {diff < 0 && (
            <span className="text-accent">
              ↓ {fmt(Math.abs(diff))} less than last month (-{Math.abs(diffPct)}%)
            </span>
          )}
          {diff === 0 && <span className="text-muted">Same as last month</span>}
        </p>
      </motion.div>

      <div className="p-5 space-y-4">
        {/* ── 2. CALENDAR STRIP ─────────────────────────────────────── */}
        {prediction.calendarView.length > 0 && (
          <motion.div variants={fadeUp}>
            <div
              ref={scrollRef}
              className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-s2"
            >
              {prediction.calendarView.map((day) => {
                const hasWarning = warningDates.has(day.date);
                return (
                  <div
                    key={day.date}
                    className={`bg-card border rounded-lg p-3 min-w-[80px] text-center shrink-0 ${
                      hasWarning
                        ? 'border-amber-500/50'
                        : 'border-line'
                    }`}
                  >
                    <p className="text-txt font-bold">{dayNum(day.date)}</p>
                    <p className="text-muted text-xs">{dayName(day.date)}</p>
                    <p className="text-accent text-sm font-medium mt-1">
                      {fmt(day.dailyTotal)}
                    </p>
                    {day.bills.length > 1 && (
                      <p className="text-muted text-[10px] mt-0.5">
                        {day.bills.length} bills
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* ── 3. BILL LIST ──────────────────────────────────────────── */}
        <motion.div variants={fadeUp}>
          <p className="font-mono text-accent text-xs uppercase tracking-wider mb-3">
            Upcoming Bills
          </p>
          <div className="space-y-2">
            {prediction.bills.map((entry, i) => (
              <motion.div
                key={entry.bill.id + i}
                variants={fadeUp}
                className="bg-card border border-line rounded-lg p-4 flex items-center justify-between gap-3"
              >
                {/* Left: name + badges */}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-txt font-medium truncate">
                      {entry.bill.name}
                    </span>
                    <span className="font-mono text-[10px] text-accent bg-accent/10 px-1.5 py-0.5 rounded">
                      {entry.bill.category}
                    </span>
                    {entry.bill.autopay && (
                      <span className="bg-accent/10 text-accent text-[10px] font-mono px-1.5 py-0.5 rounded">
                        AUTO
                      </span>
                    )}
                  </div>
                </div>

                {/* Center: due date */}
                <span className="text-off text-sm shrink-0">
                  {formatDate(entry.dueDate)}
                </span>

                {/* Right: amount */}
                <span className="text-txt font-semibold shrink-0">
                  {entry.isEstimate && (
                    <span className="text-muted text-xs mr-0.5">~</span>
                  )}
                  {fmt(entry.amount)}
                  {entry.isEstimate && (
                    <span className="text-muted text-xs ml-1">est.</span>
                  )}
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* ── 4. WARNINGS ───────────────────────────────────────────── */}
        {prediction.cashFlowWarnings.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-amber-400 text-xs uppercase tracking-wider mb-3">
              ⚠️ Heads Up
            </p>
            <div className="space-y-2">
              {prediction.cashFlowWarnings.map((w, i) => (
                <div
                  key={i}
                  className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3"
                >
                  <p className="text-off text-sm">{w.warning}</p>
                  <p className="text-amber-400 font-medium text-sm mt-1">
                    {formatDate(w.date)} &middot; {fmt(w.totalDue)}
                  </p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── 5. UNUSUAL ITEMS ──────────────────────────────────────── */}
        {prediction.unusualItems.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-wider mb-3">
              Unusual This Month
            </p>
            <div className="space-y-2">
              {prediction.unusualItems.map((item, i) => (
                <div
                  key={i}
                  className="bg-s1 rounded-lg p-3 flex items-center justify-between gap-3"
                >
                  <div className="min-w-0">
                    <span className="text-off text-sm">
                      {item.billName} &mdash;{' '}
                      <span className="text-muted">{item.reason}</span>
                    </span>
                  </div>
                  <span className="text-txt font-medium shrink-0">
                    {fmt(item.amount)}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
