'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ExportableCard from './ExportableCard';
import type { OptimizedGroceryPlan } from '@/lib/groceryPlanner';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

function pct(n: number): string {
  return `${Math.round(n)}%`;
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

/* ── Badge sub-component ───────────────────────────────────────────── */

function Badge({
  label,
  variant,
}: {
  label: string;
  variant: 'sale' | 'coupon' | 'swap';
}) {
  const styles = {
    sale: 'bg-red-500/15 text-red-400',
    coupon: 'bg-accent/15 text-accent',
    swap: 'bg-blue-500/15 text-blue-400',
  };

  return (
    <span
      className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase ${styles[variant]}`}
    >
      {label}
    </span>
  );
}

/* ── Export builder ─────────────────────────────────────────────────── */

function buildExportData(plan: OptimizedGroceryPlan) {
  // Plain clipboard: simple grouped list
  const clipLines: string[] = [
    `GROCERY LIST — ${plan.totalItems} items`,
    `Optimized total: ${fmt(plan.optimizedTotal)} (save ${fmt(plan.totalSavings)})`,
    '',
  ];

  for (const trip of plan.storeTrips) {
    clipLines.push(`--- ${trip.storeName} (${trip.items.length} items) ---`);
    for (const it of trip.items) {
      const parts = [`  ${it.item.name} x${it.item.quantity} ${it.item.unit}`];
      if (it.couponAvailable && it.couponCode) {
        parts.push(`  [COUPON: ${it.couponCode}]`);
      }
      clipLines.push(parts.join(''));
    }
    clipLines.push(`  Subtotal: ${fmt(trip.subtotal)}`);
    clipLines.push('');
  }

  // Formatted: richer version with prices + coupons + tips
  const fmtLines: string[] = [
    '=== OPTIMIZED GROCERY PLAN ===',
    `${plan.totalItems} items · Save ${fmt(plan.totalSavings)} (${pct(plan.savingsPercentage)})`,
    '',
  ];

  for (const trip of plan.storeTrips) {
    fmtLines.push(`📍 ${trip.storeName}`);
    for (const it of trip.items) {
      let line = `  • ${it.item.name} (${it.item.quantity} ${it.item.unit}) — ${fmt(it.priceAtThisStore)}`;
      if (it.savings > 0) line += ` (save ${fmt(it.savings)})`;
      fmtLines.push(line);
      if (it.couponAvailable && it.couponCode) {
        fmtLines.push(`    🎟️ Coupon: ${it.couponCode} (-${fmt(it.couponSavings ?? 0)})`);
      }
    }
    fmtLines.push(`  Subtotal: ${fmt(trip.subtotal)}`);
    fmtLines.push('');
  }

  if (plan.tips.length > 0) {
    fmtLines.push('💡 TIPS');
    plan.tips.forEach((tip) => fmtLines.push(`  • ${tip}`));
    fmtLines.push('');
  }

  fmtLines.push('=== END ===');

  return {
    clipboard: clipLines.join('\n'),
    formatted: fmtLines.join('\n'),
  };
}

/* ── Main Component ────────────────────────────────────────────────── */

export default function GroceryPlanCard({
  plan,
}: {
  plan: OptimizedGroceryPlan;
}) {
  const [subsOpen, setSubsOpen] = useState(false);

  return (
    <ExportableCard title="Grocery Plan" exportData={buildExportData(plan)}>
      <motion.div
        initial="hidden"
        animate="show"
        variants={stagger}
        className="bg-card border border-line rounded-t-card overflow-hidden"
      >
        {/* ── 1. SAVINGS HERO ─────────────────────────────────────── */}
        <motion.div
          variants={fadeUp}
          className="bg-accent/10 rounded-t-card p-5"
        >
          <p className="font-mono text-accent text-xs uppercase tracking-widest">
            OPTIMIZED PLAN
          </p>
          <div className="flex items-baseline gap-3 mt-2">
            <span className="text-3xl font-bold text-accent">
              {fmt(plan.totalSavings)}
            </span>
            <span className="text-muted text-sm">
              saved ({pct(plan.savingsPercentage)})
            </span>
          </div>
          <div className="flex items-center gap-4 mt-2 text-sm text-off">
            <span>{plan.totalItems} items</span>
            <span>·</span>
            <span>{plan.storeTrips.length} store{plan.storeTrips.length !== 1 ? 's' : ''}</span>
            <span>·</span>
            <span>Total: {fmt(plan.optimizedTotal)}</span>
          </div>
        </motion.div>

        <div className="p-5 space-y-4">
          {/* ── 2. STORE TRIPS ──────────────────────────────────────── */}
          {plan.storeTrips.map((trip) => (
            <motion.div
              key={trip.store}
              variants={fadeUp}
              className="bg-s1 border border-line rounded-lg overflow-hidden"
            >
              {/* Store header */}
              <div className="px-4 py-3 flex items-center justify-between">
                <div>
                  <span className="text-txt font-medium">{trip.storeName}</span>
                  <span className="text-muted text-sm ml-2">
                    {trip.items.length} item{trip.items.length !== 1 ? 's' : ''}
                  </span>
                </div>
                <span className="text-accent font-medium">{fmt(trip.subtotal)}</span>
              </div>

              {/* Items */}
              <div className="border-t border-line divide-y divide-line/50">
                {trip.items.map((it, i) => (
                  <div key={i} className="px-4 py-2.5 flex items-center gap-3">
                    {/* Item info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-off text-sm truncate">
                          {it.item.name}
                        </span>
                        <span className="text-muted text-xs">
                          ×{it.item.quantity} {it.item.unit}
                        </span>
                      </div>
                      {/* Badges */}
                      <div className="flex items-center gap-1.5 mt-1">
                        {it.onSale && <Badge label="SALE" variant="sale" />}
                        {it.couponAvailable && (
                          <Badge
                            label={it.couponCode ? `COUPON: ${it.couponCode}` : 'COUPON'}
                            variant="coupon"
                          />
                        )}
                        {it.substituteAvailable && (
                          <Badge label="SWAP" variant="swap" />
                        )}
                      </div>
                    </div>

                    {/* Price */}
                    <div className="text-right shrink-0">
                      <span className="text-txt text-sm font-medium">
                        {fmt(it.priceAtThisStore)}
                      </span>
                      {it.savings > 0 && (
                        <p className="text-accent text-xs">
                          −{fmt(it.savings)}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Coupon savings */}
              {trip.couponsApplied > 0 && (
                <div className="px-4 py-2 border-t border-line bg-accent/5 flex items-center justify-between text-xs">
                  <span className="text-accent">
                    🎟️ {trip.couponsApplied} coupon{trip.couponsApplied !== 1 ? 's' : ''} applied
                  </span>
                  <span className="text-accent font-medium">
                    −{fmt(trip.couponSavings)}
                  </span>
                </div>
              )}
            </motion.div>
          ))}

          {/* ── 3. SINGLE STORE COMPARISON ──────────────────────────── */}
          <motion.div
            variants={fadeUp}
            className="bg-s1 border border-line rounded-lg p-4"
          >
            <p className="font-mono text-muted text-[11px] uppercase tracking-widest mb-2">
              ONE-STOP OPTION
            </p>
            <div className="flex items-center justify-between">
              <div>
                <span className="text-txt font-medium">{plan.singleStoreBest.store}</span>
                <span className="text-muted text-sm ml-2">
                  (all items here)
                </span>
              </div>
              <span className="text-off font-medium">{fmt(plan.singleStoreBest.total)}</span>
            </div>
            <p className="text-muted text-xs mt-1">
              +{fmt(plan.singleStoreBest.convenienceTax)} more than optimized plan
              {plan.singleStoreBest.convenienceTax < 10 && (
                <span className="text-off ml-1">
                  — maybe worth the time savings?
                </span>
              )}
            </p>
          </motion.div>

          {/* ── 4. SUBSTITUTIONS (collapsible) ──────────────────────── */}
          {plan.substitutions.length > 0 && (
            <motion.div
              variants={fadeUp}
              className="bg-card border border-line rounded-lg overflow-hidden"
            >
              <button
                onClick={() => setSubsOpen(!subsOpen)}
                className="w-full px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-s1/50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <span className="text-txt font-medium">Substitutions</span>
                  <span className="bg-blue-500/15 text-blue-400 text-[10px] font-mono px-2 py-0.5 rounded">
                    {plan.substitutions.length}
                  </span>
                </div>
                <Chevron open={subsOpen} />
              </button>

              <AnimatePresence>
                {subsOpen && (
                  <motion.div
                    key="subs"
                    variants={collapse}
                    initial="initial"
                    animate="animate"
                    exit="exit"
                    className="overflow-hidden"
                  >
                    <div className="px-4 pb-3 space-y-3">
                      {plan.substitutions.map((sub, i) => (
                        <div
                          key={i}
                          className="bg-s1 rounded-lg p-3 text-sm"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-off line-through">
                              {sub.original} — {fmt(sub.originalPrice)}
                            </span>
                            <span className="text-accent text-xs font-medium">
                              Save {fmt(sub.savings)}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-accent">→</span>
                            <span className="text-txt">
                              {sub.substitute} — {fmt(sub.substitutePrice)}
                            </span>
                          </div>
                          <p className="text-muted text-xs mt-1">{sub.note}</p>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}

          {/* ── 5. TIPS ─────────────────────────────────────────────── */}
          {plan.tips.length > 0 && (
            <motion.div variants={fadeUp}>
              <p className="font-mono text-accent text-xs uppercase tracking-widest mb-2">
                💡 SMART TIPS
              </p>
              <div className="space-y-1.5">
                {plan.tips.map((tip, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 text-sm text-off"
                  >
                    <span className="text-accent mt-0.5 shrink-0">•</span>
                    <span>{tip}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </ExportableCard>
  );
}
