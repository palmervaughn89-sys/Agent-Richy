'use client';

import { motion } from 'framer-motion';
import type { RippleEffect } from '@/types/moneyMap';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function fmtCompact(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 });
}

/* ── Animation ─────────────────────────────────────────────────────── */

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
};

const rippleRing = (i: number) => ({
  hidden: { opacity: 0, scale: 0.7 },
  show: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.5, ease: 'easeOut', delay: 0.15 + i * 0.15 },
  },
});

/* ── Bar widths for visual ripple ──────────────────────────────────── */

const BAR_WIDTHS = ['20%', '35%', '55%', '75%', '100%'];

/* ══════════════════════════════════════════════════════════════════════
   COMPONENT
   ══════════════════════════════════════════════════════════════════════ */

export default function RippleEffectCard({ ripple }: { ripple: RippleEffect }) {
  const metrics = ripple.metricsImpact;

  const metricParts: string[] = [];
  if (metrics.savingsRateChange !== 0)
    metricParts.push(`${metrics.savingsRateChange > 0 ? '+' : ''}${metrics.savingsRateChange.toFixed(2)}% savings rate`);
  if (metrics.debtFreeAcceleration > 0)
    metricParts.push(`Debt-free ${metrics.debtFreeAcceleration} days sooner`);
  if (metrics.retirementAcceleration > 0)
    metricParts.push(`Retire ${metrics.retirementAcceleration} days sooner`);

  return (
    <div className="bg-card border border-line rounded-card overflow-hidden">

      {/* ── 1. TRIGGER ────────────────────────────────────────── */}
      <motion.div
        variants={stagger}
        initial="hidden"
        animate="show"
        className="bg-s1 p-4 border-b border-line"
      >
        <motion.span variants={fadeUp} className="font-mono text-accent text-[11px] tracking-label">
          RIPPLE EFFECT
        </motion.span>
        <motion.p variants={fadeUp} className="text-txt font-semibold text-lg mt-1 leading-snug">
          {ripple.trigger}
        </motion.p>
        <motion.p variants={fadeUp} className="text-accent text-2xl font-bold mt-1">
          −{fmtCompact(ripple.monthlySavings)}<span className="text-sm font-normal text-muted">/month</span>
        </motion.p>
        <motion.p variants={fadeUp} className="text-muted text-xs mt-1">{ripple.triggerDate}</motion.p>
      </motion.div>

      {/* ── 2. RIPPLE CHAIN ───────────────────────────────────── */}
      <motion.div
        variants={stagger}
        initial="hidden"
        animate="show"
        className="p-4"
      >
        <div className="space-y-3">
          {ripple.ripples.map((step, i) => {
            const barWidth = BAR_WIDTHS[Math.min(i, BAR_WIDTHS.length - 1)];
            const opacity = 1 - i * 0.08;
            const isLast = i === ripple.ripples.length - 1;
            const displayAmount = step.investedAmount > step.amount ? step.investedAmount : step.amount;

            return (
              <motion.div key={i} variants={rippleRing(i)} className="flex items-start gap-3">
                {/* Dot — grows with each step */}
                <div className="flex flex-col items-center flex-shrink-0 pt-1">
                  <motion.div
                    className="rounded-full bg-accent"
                    style={{
                      width: 8 + i * 4,
                      height: 8 + i * 4,
                    }}
                    animate={isLast ? {
                      boxShadow: ['0 0 0px rgba(0,232,123,0.3)', '0 0 12px rgba(0,232,123,0.5)', '0 0 0px rgba(0,232,123,0.3)'],
                    } : undefined}
                    transition={isLast ? { duration: 2, repeat: Infinity } : undefined}
                  />
                  {!isLast && <div className="w-px h-4 bg-accent/20 mt-1" />}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-xs text-txt-off font-medium">{step.timeframe}</span>
                    <span className={`text-sm font-mono font-bold ${isLast ? 'text-accent' : 'text-txt'}`}>
                      {fmt(displayAmount)}
                    </span>
                  </div>

                  {/* Expanding bar — the visual "ripple" */}
                  <div className="h-2 bg-line rounded-full overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      style={{
                        backgroundColor: `rgba(0,232,123,${opacity})`,
                      }}
                      initial={{ width: 0 }}
                      animate={{ width: barWidth }}
                      transition={{ duration: 0.6, ease: 'easeOut', delay: 0.2 + i * 0.15 }}
                    />
                  </div>

                  <p className="text-[11px] text-muted mt-1 leading-snug">{step.description}</p>
                  {step.milestone && (
                    <span className="text-[10px] text-accent mt-0.5 inline-block">
                      ✨ {step.milestone}
                    </span>
                  )}

                  {/* Multiplier between steps */}
                  {!isLast && i > 0 && ripple.ripples[i - 1] && (
                    (() => {
                      const prevAmount = ripple.ripples[i - 1].investedAmount || ripple.ripples[i - 1].amount;
                      const mult = prevAmount > 0 ? (displayAmount / prevAmount).toFixed(1) : '—';
                      return (
                        <span className="text-[9px] text-accent/50 font-mono mt-0.5 inline-block ml-1">
                          ×{mult}
                        </span>
                      );
                    })()
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* ── 3. IMPACT ON YOUR LIFE ────────────────────────────── */}
      {(ripple.goalImpact.length > 0 || metricParts.length > 0) && (
        <div className="border-t border-line p-4 space-y-3">
          {ripple.goalImpact.length > 0 && (
            <div className="space-y-2">
              {ripple.goalImpact.map((gi, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 + i * 0.1 }}
                  className="bg-s1 rounded-lg p-3 flex items-center gap-3"
                >
                  <span className="text-accent text-sm">🎯</span>
                  <div className="flex-1 min-w-0">
                    <span className="text-xs text-txt-off">{gi.goalName}</span>
                    <p className="text-accent text-sm font-medium">{gi.timeSaved}</p>
                  </div>
                  <span className="text-[10px] font-mono text-accent bg-accent/10 px-2 py-0.5 rounded-full">
                    +{gi.percentageBoost.toFixed(1)}%
                  </span>
                </motion.div>
              ))}
            </div>
          )}

          {metricParts.length > 0 && (
            <p className="text-muted text-xs text-center">
              {metricParts.join(' · ')}
            </p>
          )}
        </div>
      )}

      {/* ── 4. DAILY EQUIVALENT ───────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="bg-accent/5 rounded-b-card p-3 text-center border-t border-accent/10"
      >
        <span className="text-accent text-sm font-medium">
          That&apos;s {fmtCompact(metrics.dailyEquivalent)}/day working for your future
        </span>
      </motion.div>
    </div>
  );
}
