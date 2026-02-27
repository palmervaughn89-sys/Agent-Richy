'use client';

import { motion } from 'framer-motion';
import type { SubscriptionValue } from '@/types/pricing';

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

const VALUE_BADGE: Record<
  SubscriptionValue['valueRating'],
  { label: string; className: string }
> = {
  excellent: { label: 'Excellent Value', className: 'bg-accent/15 text-accent' },
  good: { label: 'Good Value', className: 'bg-accent/10 text-accent/80' },
  fair: { label: 'Fair Value', className: 'bg-amber-500/15 text-amber-400' },
  poor: { label: 'Poor Value', className: 'bg-red-500/15 text-red-400' },
  unused: { label: 'Not Using — Cancel?', className: 'bg-red-500/20 text-red-400' },
};

const COST_COLOR: Record<SubscriptionValue['valueRating'], string> = {
  excellent: 'text-accent',
  good: 'text-accent/80',
  fair: 'text-amber-400',
  poor: 'text-red-400',
  unused: 'text-red-400',
};

export default function SubscriptionValueCard({
  subscriptions,
}: {
  subscriptions: SubscriptionValue[];
}) {
  // Sort worst value first (highest costPerHour, unused at top)
  const sorted = [...subscriptions].sort((a, b) => {
    if (a.valueRating === 'unused' && b.valueRating !== 'unused') return -1;
    if (b.valueRating === 'unused' && a.valueRating !== 'unused') return 1;
    return b.costPerHour - a.costPerHour;
  });

  const totalMonthly = subscriptions.reduce((s, sub) => s + sub.monthlyCost, 0);
  const totalHours = subscriptions.reduce((s, sub) => s + sub.hoursUsedPerMonth, 0);
  const avgCostPerHour = totalHours > 0 ? totalMonthly / totalHours : 0;

  const cuttable = subscriptions.filter(
    (s) => s.valueRating === 'poor' || s.valueRating === 'unused'
  );
  const potentialSavings = cuttable.reduce((s, sub) => s + sub.monthlyCost, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="bg-card border border-line rounded-card p-5"
    >
      {/* Header */}
      <h3 className="text-lg font-semibold text-txt">Subscription Value Report</h3>
      <p className="text-muted text-sm">Are you getting your money&apos;s worth?</p>

      {/* Subscription list */}
      <div className="mt-4 space-y-3">
        {sorted.map((sub, idx) => {
          const badge = VALUE_BADGE[sub.valueRating];
          const costColor = COST_COLOR[sub.valueRating];

          return (
            <motion.div
              key={sub.id}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, delay: idx * 0.05 }}
              className="bg-s1 rounded-lg p-4"
            >
              {/* Top row */}
              <div className="flex justify-between items-center">
                <span className="text-txt font-medium">{sub.serviceName}</span>
                <span className="text-off">{fmt(sub.monthlyCost)}/mo</span>
              </div>

              {/* Stats grid */}
              <div className="grid grid-cols-3 gap-2 mt-2">
                {/* Hours used */}
                <div>
                  <div className="text-txt font-bold">
                    {sub.hoursUsedPerMonth}
                    <span className="text-muted text-xs font-normal ml-0.5">hrs</span>
                  </div>
                  <div className="text-muted text-xs">Hours used</div>
                </div>

                {/* Cost per hour */}
                <div>
                  <div className={`font-bold ${costColor}`}>
                    {sub.hoursUsedPerMonth > 0
                      ? fmt(sub.costPerHour)
                      : '—'}
                    <span className="text-muted text-xs font-normal ml-0.5">/hr</span>
                  </div>
                  <div className="text-muted text-xs">Cost per hour</div>
                </div>

                {/* Value badge */}
                <div className="flex items-start justify-end">
                  <span
                    className={`text-xs font-semibold px-2 py-1 rounded-full whitespace-nowrap ${badge.className}`}
                  >
                    {badge.label}
                  </span>
                </div>
              </div>

              {/* Recommendation */}
              <p className="text-off text-sm mt-2">{sub.recommendation}</p>

              {/* Alternatives */}
              {sub.alternativeOptions && sub.alternativeOptions.length > 0 && (
                <div className="text-muted text-xs mt-1 space-y-0.5">
                  {sub.alternativeOptions.map((alt, i) => (
                    <p key={i}>
                      → {alt.name} ({fmt(alt.cost)}/mo) — {alt.note}
                    </p>
                  ))}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Summary footer */}
      <div className="border-t border-line pt-3 mt-4 space-y-1.5">
        <div className="flex justify-between text-sm">
          <span className="text-muted">Total monthly spend</span>
          <span className="text-txt font-semibold">{fmt(totalMonthly)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted">Avg cost per hour</span>
          <span className="text-off">{fmt(avgCostPerHour)}/hr</span>
        </div>
        {potentialSavings > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-muted">
              Potential savings (cut poor &amp; unused)
            </span>
            <span className="text-accent font-bold">{fmt(potentialSavings)}/mo</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
