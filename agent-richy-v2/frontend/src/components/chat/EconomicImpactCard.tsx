'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ExportableCard from './ExportableCard';
import type { PersonalEconomicImpact, DealPrediction } from '@/types/economicIntel';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function fmtDec(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function pct(n: number): string {
  const sign = n > 0 ? '+' : '';
  return `${sign}${n.toFixed(1)}%`;
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

const collapse = {
  initial: { height: 0, opacity: 0 },
  animate: { height: 'auto', opacity: 1, transition: { duration: 0.25, ease: 'easeOut' } },
  exit: { height: 0, opacity: 0, transition: { duration: 0.2, ease: 'easeIn' } },
};

/* ── Icons ─────────────────────────────────────────────────────────── */

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      width="14" height="14" viewBox="0 0 16 16" fill="none"
      className={`text-muted transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
    >
      <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function TrendArrow({ trend }: { trend: string }) {
  if (trend === 'getting_worse')
    return <span className="text-red-400 text-sm font-medium">↑ Rising</span>;
  if (trend === 'improving')
    return <span className="text-emerald-400 text-sm font-medium">↓ Falling</span>;
  return <span className="text-amber-400 text-sm font-medium">→ Stable</span>;
}

function ConfidenceBadge({ level }: { level: 'high' | 'medium' | 'low' }) {
  const styles: Record<string, string> = {
    high: 'text-accent bg-accent/10',
    medium: 'text-amber-400 bg-amber-400/10',
    low: 'text-muted bg-white/5',
  };
  return (
    <span className={`text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full ${styles[level]}`}>
      {level}
    </span>
  );
}

function ActionBadge({ action }: { action: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    wait: { label: 'WAIT TO BUY', cls: 'text-amber-400 bg-amber-400/10' },
    buy_now: { label: 'BUY NOW', cls: 'text-accent bg-accent/10' },
    stock_up: { label: 'STOCK UP', cls: 'text-accent bg-accent/10' },
    watch: { label: 'WATCH', cls: 'text-blue-400 bg-blue-400/10' },
    lock_in: { label: 'LOCK IN', cls: 'text-emerald-400 bg-emerald-400/10' },
  };
  const { label, cls } = map[action] ?? { label: action.toUpperCase(), cls: 'text-muted bg-white/5' };
  return (
    <span className={`font-mono text-sm font-bold px-3 py-1 rounded-full ${cls}`}>{label}</span>
  );
}

/* ── Category Impact Row ───────────────────────────────────────────── */

function CategoryRow({ impact, maxSpend }: {
  impact: PersonalEconomicImpact['categoryImpacts'][0];
  maxSpend: number;
}) {
  const barWidth = maxSpend > 0 ? (impact.userMonthlySpend / maxSpend) * 100 : 0;
  const impactBarWidth = maxSpend > 0 ? (Math.abs(impact.monthlyExtraCost) / maxSpend) * 100 : 0;
  const isPositive = impact.monthlyExtraCost > 0;

  return (
    <motion.div variants={fadeUp} className="bg-card border border-line rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-txt font-medium text-sm">{impact.category}</span>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-mono ${isPositive ? 'text-red-400' : 'text-accent'}`}>
            {pct(impact.inflationRate)}
          </span>
          <TrendArrow trend={impact.trend} />
        </div>
      </div>

      {/* Spend bar */}
      <div className="flex items-center gap-3 mb-1.5">
        <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
          <div className="h-full bg-accent/30 rounded-full" style={{ width: `${barWidth}%` }} />
        </div>
        <span className="text-off text-xs w-16 text-right">{fmt(impact.userMonthlySpend)}/mo</span>
      </div>

      {/* Impact bar */}
      <div className="flex items-center gap-3 mb-2">
        <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${isPositive ? 'bg-red-400/60' : 'bg-accent/60'}`}
            style={{ width: `${Math.min(impactBarWidth, 100)}%` }}
          />
        </div>
        <span className={`text-xs w-16 text-right font-medium ${isPositive ? 'text-red-400' : 'text-accent'}`}>
          {isPositive ? '+' : ''}{fmtDec(impact.monthlyExtraCost)}/mo
        </span>
      </div>

      {/* Richy action */}
      <p className="text-accent text-xs italic leading-relaxed">💡 {impact.richyAction}</p>
    </motion.div>
  );
}

/* ── Rate Impact Card ─────────────────────────────────────────────── */

function RateImpact({ title, emoji, details, actionLabel }: {
  title: string;
  emoji: string;
  details: string[];
  actionLabel: string;
}) {
  return (
    <motion.div variants={fadeUp} className="bg-s1 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">{emoji}</span>
        <span className="text-txt font-medium text-sm">{title}</span>
      </div>
      {details.map((d, i) => (
        <p key={i} className="text-off text-xs mb-1">{d}</p>
      ))}
      <div className="mt-3">
        <span className="text-accent text-xs font-medium bg-accent/10 rounded-full px-3 py-1 cursor-pointer hover:bg-accent/20 transition-colors">
          {actionLabel}
        </span>
      </div>
    </motion.div>
  );
}

/* ── Prediction Mini Card ─────────────────────────────────────────── */

function PredictionMini({ prediction }: { prediction: DealPrediction }) {
  return (
    <motion.div variants={fadeUp} className="bg-card border border-line rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-txt text-sm font-medium">{prediction.category}</span>
        <div className="flex items-center gap-2">
          <ConfidenceBadge level={prediction.confidence} />
          <span className="text-muted text-[10px] font-mono">{prediction.timeframe}</span>
        </div>
      </div>
      <p className="text-off text-xs mb-3">{prediction.prediction}</p>
      <div className="flex items-center justify-between">
        <ActionBadge action={prediction.action} />
        <span className="text-accent text-xs font-medium">{prediction.potentialSavings}</span>
      </div>
    </motion.div>
  );
}

/* ── Main Component ────────────────────────────────────────────────── */

interface EconomicImpactCardProps {
  impact: PersonalEconomicImpact;
}

export default function EconomicImpactCard({ impact }: EconomicImpactCardProps) {
  const [showRates, setShowRates] = useState(false);
  const [showPredictions, setShowPredictions] = useState(false);

  const sortedImpacts = useMemo(
    () => [...impact.categoryImpacts].sort((a, b) => Math.abs(b.monthlyExtraCost) - Math.abs(a.monthlyExtraCost)),
    [impact.categoryImpacts],
  );

  const maxSpend = useMemo(
    () => Math.max(...impact.categoryImpacts.map((c) => c.userMonthlySpend), 1),
    [impact.categoryImpacts],
  );

  /* ── Rate impacts ─────────────────────────────────────────────── */
  const rateCards: { title: string; emoji: string; details: string[]; actionLabel: string }[] = [];

  if (impact.rateImpacts.mortgageImpact?.shouldRefinance) {
    const m = impact.rateImpacts.mortgageImpact;
    rateCards.push({
      title: 'Mortgage Refinance Opportunity',
      emoji: '🏠',
      details: [
        `Your rate: ${m.currentRate}% → Market: ${m.currentMarketRate}%`,
        `Potential savings: ${fmt(m.refinanceSavings)}/month`,
        m.reason,
      ],
      actionLabel: 'Explore refinancing',
    });
  }

  if (impact.rateImpacts.creditCardImpact?.shouldTransfer) {
    const c = impact.rateImpacts.creditCardImpact;
    rateCards.push({
      title: 'Balance Transfer Savings',
      emoji: '💳',
      details: [
        `Your rate: ${c.currentRate}% → Available: ${c.avgMarketRate}%`,
        `Savings: ${fmt(c.balanceTransferSavings)}/month`,
      ],
      actionLabel: 'Compare balance transfers',
    });
  }

  if (impact.rateImpacts.savingsImpact && impact.rateImpacts.savingsImpact.annualEarningsDifference > 10) {
    const s = impact.rateImpacts.savingsImpact;
    rateCards.push({
      title: 'Savings Account Upgrade',
      emoji: '🏦',
      details: [
        `Your APY: ${s.currentAPY}% → Best available: ${s.bestAvailableAPY}%`,
        `Extra earnings: ${fmt(s.annualEarningsDifference)}/year on your ${fmt(s.balanceInSavings)} balance`,
      ],
      actionLabel: 'See top HYSA rates',
    });
  }

  /* ── Export data ──────────────────────────────────────────────── */
  const exportData = useMemo(() => {
    const lines = [
      `Economic Impact Report — ${impact.generatedAt}`,
      '',
      impact.headline,
      '',
      `Monthly inflation cost: ${fmtDec(impact.monthlyInflationCost)}`,
      `Annual inflation cost: ${fmt(impact.annualInflationCost)}`,
      `Net monthly impact: ${fmtDec(impact.netMonthlyImpact)}`,
      '',
      '— Category Impacts —',
      ...sortedImpacts.map(
        (c) => `${c.category}: ${fmtDec(c.monthlyExtraCost)}/mo (${pct(c.inflationRate)} inflation) — ${c.richyAction}`,
      ),
    ];
    const text = lines.join('\n');
    return { clipboard: text, formatted: text };
  }, [impact, sortedImpacts]);

  const netPositive = impact.netMonthlyImpact <= 0;

  return (
    <ExportableCard title="Economic Impact" exportData={exportData}>
      <motion.div variants={stagger} initial="hidden" animate="show">
        {/* ── Headline ─────────────────────────────────────────── */}
        <motion.div variants={fadeUp} className="bg-s1 rounded-t-[14px] p-6">
          <p className="font-mono text-accent text-xs tracking-[0.08em] uppercase mb-3">
            Your Economic Weather Report
          </p>
          <p className="text-txt text-lg font-semibold leading-relaxed mb-4">
            {impact.headline}
          </p>
          <div className="flex items-baseline gap-2">
            <span className="text-red-400 text-3xl font-bold">{fmtDec(impact.monthlyInflationCost)}</span>
            <span className="text-off text-sm">extra per month compared to last year</span>
          </div>
        </motion.div>

        {/* ── Category Impacts ─────────────────────────────────── */}
        <motion.div variants={fadeUp} className="mt-4 space-y-3">
          <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-2">
            {sortedImpacts.map((ci) => (
              <CategoryRow key={ci.category} impact={ci} maxSpend={maxSpend} />
            ))}
          </motion.div>
        </motion.div>

        {/* ── Rate Impacts ─────────────────────────────────────── */}
        {rateCards.length > 0 && (
          <motion.div variants={fadeUp} className="mt-4">
            <button
              onClick={() => setShowRates(!showRates)}
              className="w-full flex items-center justify-between px-4 py-3 bg-card border border-line rounded-lg hover:bg-s1 transition-colors"
            >
              <span className="font-mono text-accent text-xs tracking-[0.08em] uppercase">
                Rate Opportunities ({rateCards.length})
              </span>
              <Chevron open={showRates} />
            </button>
            <AnimatePresence>
              {showRates && (
                <motion.div {...collapse} className="overflow-hidden">
                  <div className="pt-2 space-y-2">
                    {rateCards.map((rc) => (
                      <RateImpact key={rc.title} {...rc} />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* ── Deal Predictions ─────────────────────────────────── */}
        {impact.relevantPredictions.length > 0 && (
          <motion.div variants={fadeUp} className="mt-4">
            <button
              onClick={() => setShowPredictions(!showPredictions)}
              className="w-full flex items-center justify-between px-4 py-3 bg-card border border-line rounded-lg hover:bg-s1 transition-colors"
            >
              <span className="font-mono text-accent text-xs tracking-[0.08em] uppercase">
                Upcoming Opportunities ({impact.relevantPredictions.length})
              </span>
              <Chevron open={showPredictions} />
            </button>
            <AnimatePresence>
              {showPredictions && (
                <motion.div {...collapse} className="overflow-hidden">
                  <motion.div variants={stagger} initial="hidden" animate="show" className="pt-2 space-y-2">
                    {impact.relevantPredictions.map((pred) => (
                      <PredictionMini key={pred.id} prediction={pred} />
                    ))}
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* ── Net Position ─────────────────────────────────────── */}
        <motion.div
          variants={fadeUp}
          className={`rounded-b-[14px] p-4 mt-4 text-center ${netPositive ? 'bg-accent/10' : 'bg-red-400/10'}`}
        >
          <p className="text-off text-xs mb-1">Net monthly impact</p>
          <p className={`text-2xl font-bold ${netPositive ? 'text-accent' : 'text-red-400'}`}>
            {impact.netMonthlyImpact > 0 ? '+' : ''}{fmtDec(impact.netMonthlyImpact)}
          </p>
          {netPositive && (
            <p className="text-accent text-xs mt-1">
              Richy&apos;s optimizations are outweighing inflation 💪
            </p>
          )}
        </motion.div>
      </motion.div>
    </ExportableCard>
  );
}
