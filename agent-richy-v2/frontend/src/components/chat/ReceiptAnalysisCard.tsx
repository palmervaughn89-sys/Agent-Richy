'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { AnalyzedReceipt } from '@/types/tools';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}

/* Green palette for category segments */
const SEGMENT_COLORS = [
  'bg-[#00E87B]',     // accent
  'bg-[#00C468]',
  'bg-[#009E54]',
  'bg-[#007A40]',
  'bg-[#00562D]',
  'bg-[#2BFFA0]',
  'bg-[#14D88A]',
  'bg-[#0AAF6E]',
];

const SEGMENT_DOT_COLORS = [
  'bg-[#00E87B]',
  'bg-[#00C468]',
  'bg-[#009E54]',
  'bg-[#007A40]',
  'bg-[#00562D]',
  'bg-[#2BFFA0]',
  'bg-[#14D88A]',
  'bg-[#0AAF6E]',
];

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
  animate: {
    height: 'auto',
    opacity: 1,
    transition: { duration: 0.25, ease: 'easeOut' },
  },
  exit: {
    height: 0,
    opacity: 0,
    transition: { duration: 0.2, ease: 'easeIn' },
  },
};

/* ── Chevron SVG ───────────────────────────────────────────────────── */

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      className={`text-muted transition-transform duration-200 ${
        open ? 'rotate-180' : ''
      }`}
    >
      <path
        d="M4 6L8 10L12 6"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/* ── Component ─────────────────────────────────────────────────────── */

export default function ReceiptAnalysisCard({
  receipt,
}: {
  receipt: AnalyzedReceipt;
}) {
  const [itemsOpen, setItemsOpen] = useState(false);
  const sortedItems = [...receipt.items].sort(
    (a, b) => b.totalPrice - a.totalPrice,
  );
  const totalAlertSavings = receipt.priceAlerts.reduce(
    (sum, a) => sum + a.savings,
    0,
  );
  const cmp = receipt.comparedToAverage;

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={stagger}
      className="bg-card border border-line rounded-card overflow-hidden"
    >
      {/* ── 1. RECEIPT HEADER ──────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="bg-s1 rounded-t-card p-5">
        <h3 className="text-xl font-bold text-txt">{receipt.store}</h3>
        <p className="text-muted text-sm mt-0.5">
          {fmtDate(receipt.date)}
          {receipt.storeAddress && <> · {receipt.storeAddress}</>}
        </p>
        <p className="text-3xl font-bold text-accent mt-2">
          {fmt(receipt.total)}
        </p>
        <p className="text-off text-sm mt-1">
          Subtotal {fmt(receipt.subtotal)} + Tax {fmt(receipt.tax)}
          {receipt.paymentMethod && (
            <span className="text-muted"> · {receipt.paymentMethod}</span>
          )}
        </p>
      </motion.div>

      <div className="p-5 space-y-4">
        {/* ── 2. CATEGORY BREAKDOWN ─────────────────────────────────── */}
        {receipt.categoryBreakdown.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">
              WHERE YOUR MONEY WENT
            </p>

            {/* Stacked bar */}
            <div className="h-4 rounded-full overflow-hidden flex">
              {receipt.categoryBreakdown.map((cat, i) => (
                <div
                  key={cat.category}
                  className={`${SEGMENT_COLORS[i % SEGMENT_COLORS.length]} transition-all`}
                  style={{ width: `${cat.percentage}%` }}
                  title={`${cat.category}: ${fmt(cat.amount)} (${cat.percentage}%)`}
                />
              ))}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-x-4 gap-y-1.5 mt-3">
              {receipt.categoryBreakdown.map((cat, i) => (
                <div key={cat.category} className="flex items-center gap-1.5">
                  <span
                    className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                      SEGMENT_DOT_COLORS[i % SEGMENT_DOT_COLORS.length]
                    }`}
                  />
                  <span className="text-off text-sm">{cat.category}</span>
                  <span className="text-muted text-xs">
                    {fmt(cat.amount)} ({cat.percentage}%)
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── 3. PRICE ALERTS ───────────────────────────────────────── */}
        {receipt.priceAlerts.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">
              💰 COULD HAVE SAVED
            </p>
            <div className="space-y-2">
              {receipt.priceAlerts.map((alert, i) => (
                <div
                  key={i}
                  className="bg-accent/10 border border-accent/20 rounded-lg p-3"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="text-txt font-medium">{alert.item}</p>
                      <p className="text-off text-sm mt-0.5">
                        You paid {fmt(alert.paidPrice)} at {receipt.store}
                      </p>
                      <p className="text-accent font-medium text-sm">
                        Available for {fmt(alert.betterPrice)} at{' '}
                        {alert.betterStore}
                      </p>
                    </div>
                    <span className="bg-accent text-black px-2 py-0.5 rounded-full text-xs font-bold shrink-0">
                      Save {fmt(alert.savings)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-accent font-semibold text-sm mt-3 text-right">
              Total potential savings: {fmt(totalAlertSavings)}
            </p>
          </motion.div>
        )}

        {/* ── 4. ITEMS LIST (collapsible) ───────────────────────────── */}
        <motion.div variants={fadeUp}>
          <button
            onClick={() => setItemsOpen(!itemsOpen)}
            className="w-full flex items-center justify-between cursor-pointer group"
          >
            <p className="font-mono text-muted text-xs uppercase tracking-widest group-hover:text-off transition-colors">
              ALL ITEMS ({receipt.items.length})
            </p>
            <Chevron open={itemsOpen} />
          </button>

          <AnimatePresence>
            {itemsOpen && (
              <motion.div
                key="items"
                variants={collapse}
                initial="initial"
                animate="animate"
                exit="exit"
                className="overflow-hidden"
              >
                <div className="mt-2">
                  {sortedItems.map((item, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between text-sm border-b border-line py-2 last:border-b-0"
                    >
                      <span className="text-off truncate mr-3">
                        {item.name}
                        {item.quantity > 1 && (
                          <span className="text-muted ml-1">
                            ×{item.quantity}
                          </span>
                        )}
                      </span>
                      <span className="text-txt shrink-0">
                        {fmt(item.totalPrice)}
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* ── 5. TRIP COMPARISON ─────────────────────────────────────── */}
        {cmp && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">
              TRIP COMPARISON
            </p>

            {/* Bars */}
            <div className="space-y-2">
              {/* This trip */}
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-off">This trip</span>
                  <span className="text-txt font-medium">
                    {fmt(cmp.thisTrip)}
                  </span>
                </div>
                <div className="h-3 bg-s2 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{
                      width: `${Math.min(
                        (cmp.thisTrip /
                          Math.max(cmp.thisTrip, cmp.averageTrip)) *
                          100,
                        100,
                      )}%`,
                    }}
                    transition={{ duration: 0.6, ease: 'easeOut', delay: 0.3 }}
                    className="h-full bg-accent rounded-full"
                  />
                </div>
              </div>

              {/* Average trip */}
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-off">Your average</span>
                  <span className="text-txt font-medium">
                    {fmt(cmp.averageTrip)}
                  </span>
                </div>
                <div className="h-3 bg-s2 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{
                      width: `${Math.min(
                        (cmp.averageTrip /
                          Math.max(cmp.thisTrip, cmp.averageTrip)) *
                          100,
                        100,
                      )}%`,
                    }}
                    transition={{ duration: 0.6, ease: 'easeOut', delay: 0.4 }}
                    className="h-full bg-accent/40 rounded-full"
                  />
                </div>
              </div>
            </div>

            {/* Trend */}
            <p className="text-off text-sm mt-3">
              {cmp.trend === 'increasing' && (
                <>
                  <span className="text-amber-400">↑</span> Your grocery
                  spending is <span className="text-amber-400">increasing</span>
                </>
              )}
              {cmp.trend === 'decreasing' && (
                <>
                  <span className="text-accent">↓</span> Your grocery spending
                  is <span className="text-accent">decreasing</span>
                </>
              )}
              {cmp.trend === 'stable' && (
                <>
                  <span className="text-muted">→</span> Your grocery spending is{' '}
                  <span className="text-muted">stable</span>
                </>
              )}
              {' '}
              <span className="text-muted">
                ({fmt(Math.abs(cmp.difference))}{' '}
                {cmp.difference >= 0 ? 'more' : 'less'} than average)
              </span>
            </p>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
