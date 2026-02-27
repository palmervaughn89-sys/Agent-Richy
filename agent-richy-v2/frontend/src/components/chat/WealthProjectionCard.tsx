'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts';
import ExportableCard from './ExportableCard';
import type { WealthProjection } from '@/lib/wealthTrajectory';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function fmtShort(n: number): string {
  if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
  return fmt(n);
}

/* ── Animation ─────────────────────────────────────────────────────── */

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
      width="14"
      height="14"
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

/* ── Chart colors ──────────────────────────────────────────────────── */

const SCENARIO_COLORS = {
  current_path: '#8B9A8F',   // muted
  optimized: '#00E87B',      // accent
  aggressive: '#3B82F6',     // blue
};

const SCENARIO_LABELS = {
  current_path: 'Current Path',
  optimized: 'Optimized',
  aggressive: 'Aggressive',
};

/* ── Custom tooltip ────────────────────────────────────────────────── */

interface TooltipPayloadEntry {
  name: string;
  value: number;
  color: string;
}

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
}) {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="bg-card border border-line rounded-lg px-3 py-2 shadow-lg">
      <p className="text-muted text-[10px] font-mono uppercase mb-1">Year {label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 text-xs">
          <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: p.color }} />
          <span className="text-off">{p.name}:</span>
          <span className="text-txt font-medium">{fmtShort(p.value)}</span>
        </div>
      ))}
    </div>
  );
}

/* ── Build export data ─────────────────────────────────────────────── */

function buildExportData(wp: WealthProjection) {
  const lines = [
    `Wealth Trajectory — ${wp.basedOn}`,
    '',
    `Current Net Worth: ${fmt(wp.currentNetWorth)}`,
    `Monthly Surplus: ${fmt(wp.currentMonthlySurplus)}`,
    `Savings Rate: ${wp.currentSavingsRate}%`,
    '',
    '— Projections —',
  ];

  for (const p of wp.projections) {
    lines.push(`\nYear ${p.years}:`);
    for (const s of p.scenarios) {
      lines.push(`  ${SCENARIO_LABELS[s.name]}: Net Worth ${fmt(s.netWorth)} | Passive Income ${fmt(s.passiveIncome)}/mo | FI: ${s.financialIndependenceProgress}%`);
    }
  }

  if (wp.milestones.length > 0) {
    lines.push('\n— Milestones —');
    for (const m of wp.milestones) {
      lines.push(`  ${m.name}: Current path ${m.currentPathDate} | Optimized ${m.optimizedPathDate} (${m.timeSavedByOptimizing} months saved)`);
    }
  }

  if (wp.topActions.length > 0) {
    lines.push('\n— Top Actions —');
    for (const a of wp.topActions) {
      lines.push(`  ${a.action}: ${fmt(a.monthlyImpact)}/mo → ${fmt(a.retirementImpact)} at retirement`);
    }
  }

  const rp = wp.retirementProjection;
  lines.push(
    '\n— Retirement —',
    `  Current path retirement age: ${rp.currentPathRetirementAge}`,
    `  Optimized retirement age: ${rp.optimizedPathRetirementAge}`,
    `  Monthly retirement income: ${fmt(rp.monthlyRetirementIncome)}`,
    `  Gap: ${fmt(rp.gap)}/mo`,
  );

  const text = lines.join('\n');
  return { clipboard: text, formatted: text };
}

/* ── Component ─────────────────────────────────────────────────────── */

interface Props {
  projection: WealthProjection;
}

export default function WealthProjectionCard({ projection }: Props) {
  const wp = projection;
  const [showMilestones, setShowMilestones] = useState(true);
  const [showActions, setShowActions] = useState(false);
  const [showPeers, setShowPeers] = useState(false);

  // Build chart data for the multi-line chart
  const chartData = wp.projections.map((p) => {
    const row: Record<string, number | string> = { year: p.years };
    for (const s of p.scenarios) {
      row[s.name] = s.netWorth;
    }
    return row;
  });

  // Delta between optimized and current at 30yr (or last projection)
  const lastProj = wp.projections[wp.projections.length - 1];
  const currentLast = lastProj?.scenarios.find((s) => s.name === 'current_path')?.netWorth ?? 0;
  const optimizedLast = lastProj?.scenarios.find((s) => s.name === 'optimized')?.netWorth ?? 0;
  const delta = optimizedLast - currentLast;
  const lastYears = lastProj?.years ?? 30;

  // Monthly difference for "the hook"
  const monthlyDiff = wp.topActions.reduce((s, a) => s + a.monthlyImpact, 0);

  const rp = wp.retirementProjection;

  return (
    <ExportableCard
      title="Wealth Trajectory"
      exportData={buildExportData(wp)}
    >
      <motion.div
        variants={stagger}
        initial="hidden"
        animate="show"
        className="overflow-hidden rounded-t-card"
      >
        {/* ── HEADER ──────────────────────────────────────────── */}
        <div className="bg-gradient-to-r from-s1 to-card p-6">
          <p className="font-mono text-accent text-xs tracking-widest uppercase">
            Wealth Trajectory
          </p>
          <p className="text-muted text-xs mt-0.5">{wp.basedOn}</p>

          {/* Current snapshot */}
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div>
              <p className="text-muted text-[10px] font-mono uppercase">Net Worth</p>
              <p className={`text-lg font-bold ${wp.currentNetWorth >= 0 ? 'text-accent' : 'text-red-400'}`}>
                {fmtShort(wp.currentNetWorth)}
              </p>
            </div>
            <div>
              <p className="text-muted text-[10px] font-mono uppercase">Surplus/mo</p>
              <p className="text-lg font-bold text-txt">{fmtShort(wp.currentMonthlySurplus)}</p>
            </div>
            <div>
              <p className="text-muted text-[10px] font-mono uppercase">Savings Rate</p>
              <p className="text-lg font-bold text-txt">{wp.currentSavingsRate}%</p>
            </div>
          </div>
        </div>

        {/* ── THE HOOK ────────────────────────────────────────── */}
        {delta > 0 && monthlyDiff > 0 && (
          <motion.div variants={fadeUp} className="bg-accent/5 border border-accent/20 rounded-lg p-4 mx-4 mt-4">
            <p className="text-txt text-sm font-medium">
              The difference between your current path and the optimized path is{' '}
              <span className="text-accent font-bold">{fmt(monthlyDiff)}/month</span>.
            </p>
            <p className="text-off text-sm mt-1">
              Over {lastYears} years invested at historical market returns, that&apos;s{' '}
              <span className="text-accent font-bold">{fmtShort(delta)}</span>.
            </p>
            <p className="text-muted text-xs mt-1 italic">
              That&apos;s not a typo. {fmt(monthlyDiff)} a month becomes {fmtShort(delta)}.
              That&apos;s the cost of not optimizing.
            </p>
          </motion.div>
        )}

        {/* ── MULTI-DECADE CHART ──────────────────────────────── */}
        {chartData.length > 0 && (
          <motion.div variants={fadeUp} className="px-4 mt-4">
            <p className="font-mono text-muted text-[10px] tracking-widest uppercase mb-3">
              Net Worth Over Time
            </p>
            <div className="bg-s1 rounded-card p-3">
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={chartData}>
                  <CartesianGrid stroke="#1E2D26" strokeDasharray="4 4" />
                  <XAxis
                    dataKey="year"
                    tick={{ fill: '#8B9A8F', fontSize: 11 }}
                    axisLine={{ stroke: '#1E2D26' }}
                    tickFormatter={(v) => `${v}y`}
                  />
                  <YAxis
                    tick={{ fill: '#8B9A8F', fontSize: 11 }}
                    axisLine={{ stroke: '#1E2D26' }}
                    tickFormatter={(v) => fmtShort(v)}
                    width={60}
                  />
                  <Tooltip content={<ChartTooltip />} />
                  <Legend
                    wrapperStyle={{ fontSize: 11, color: '#8B9A8F' }}
                    formatter={(value: string) => SCENARIO_LABELS[value as keyof typeof SCENARIO_LABELS] ?? value}
                  />
                  <Line
                    type="monotone"
                    dataKey="current_path"
                    name="current_path"
                    stroke={SCENARIO_COLORS.current_path}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    strokeDasharray="6 3"
                  />
                  <Line
                    type="monotone"
                    dataKey="optimized"
                    name="optimized"
                    stroke={SCENARIO_COLORS.optimized}
                    strokeWidth={2.5}
                    dot={{ r: 3, fill: SCENARIO_COLORS.optimized }}
                  />
                  <Line
                    type="monotone"
                    dataKey="aggressive"
                    name="aggressive"
                    stroke={SCENARIO_COLORS.aggressive}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    strokeDasharray="2 2"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        )}

        {/* ── RETIREMENT ──────────────────────────────────────── */}
        <motion.div variants={fadeUp} className="px-4 mt-4">
          <p className="font-mono text-muted text-[10px] tracking-widest uppercase mb-3">
            Retirement Outlook
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-card border border-line rounded-card p-3 text-center">
              <p className="text-muted text-[10px] font-mono uppercase">Current Path</p>
              <p className="text-2xl font-bold text-txt mt-1">Age {rp.currentPathRetirementAge}</p>
              <p className="text-muted text-xs">{fmtShort(rp.retirementSavingsAtCurrentPath)} saved</p>
            </div>
            <div className="bg-card border border-accent/30 rounded-card p-3 text-center">
              <p className="text-accent text-[10px] font-mono uppercase">Optimized</p>
              <p className="text-2xl font-bold text-accent mt-1">Age {rp.optimizedPathRetirementAge}</p>
              <p className="text-muted text-xs">{fmtShort(rp.retirementSavingsOptimized)} saved</p>
            </div>
          </div>
          <div className="mt-2 flex flex-col sm:flex-row gap-2 text-xs">
            <span className="text-off">
              Monthly retirement income: <span className="text-txt font-medium">{fmt(rp.monthlyRetirementIncome)}</span>
            </span>
            <span className="text-off">
              + Social Security est: <span className="text-txt font-medium">{fmt(rp.socialSecurityEstimate)}</span>
            </span>
            <span className={rp.gap >= 0 ? 'text-accent' : 'text-red-400'}>
              {rp.gap >= 0 ? 'Surplus' : 'Gap'}: {fmt(Math.abs(rp.gap))}/mo
            </span>
          </div>
        </motion.div>

        {/* ── MILESTONES ──────────────────────────────────────── */}
        {wp.milestones.length > 0 && (
          <motion.div variants={fadeUp} className="px-4 mt-4">
            <button
              onClick={() => setShowMilestones(!showMilestones)}
              className="font-mono text-muted text-[10px] tracking-widest uppercase flex items-center gap-1 cursor-pointer"
            >
              Milestones
              <Chevron open={showMilestones} />
            </button>
            <AnimatePresence>
              {showMilestones && (
                <motion.div
                  key="milestones"
                  variants={collapse}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  className="overflow-hidden"
                >
                  <div className="mt-2 space-y-2">
                    {wp.milestones.map((m, i) => (
                      <div key={i} className="bg-s1 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-txt text-sm font-medium">{m.name}</span>
                          {m.timeSavedByOptimizing > 0 && (
                            <span className="text-accent text-[10px] font-mono">
                              {m.timeSavedByOptimizing} months faster
                            </span>
                          )}
                        </div>
                        <div className="flex gap-4 mt-1 text-xs">
                          <span className="text-muted">
                            Current: <span className="text-off">{m.currentPathDate}</span>
                          </span>
                          <span className="text-muted">
                            Optimized: <span className="text-accent">{m.optimizedPathDate}</span>
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* ── TOP ACTIONS ─────────────────────────────────────── */}
        {wp.topActions.length > 0 && (
          <motion.div variants={fadeUp} className="px-4 mt-4">
            <button
              onClick={() => setShowActions(!showActions)}
              className="font-mono text-muted text-[10px] tracking-widest uppercase flex items-center gap-1 cursor-pointer"
            >
              Impact Actions
              <Chevron open={showActions} />
            </button>
            <AnimatePresence>
              {showActions && (
                <motion.div
                  key="actions"
                  variants={collapse}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  className="overflow-hidden"
                >
                  <div className="mt-2 space-y-2">
                    {wp.topActions.map((a, i) => (
                      <div key={i} className="bg-s1 rounded-lg p-3">
                        <p className="text-txt text-sm font-medium">{a.action}</p>
                        <div className="grid grid-cols-3 gap-2 mt-1.5 text-xs">
                          <div>
                            <span className="text-muted">Monthly: </span>
                            <span className="text-accent font-medium">{fmt(a.monthlyImpact)}</span>
                          </div>
                          <div>
                            <span className="text-muted">10yr: </span>
                            <span className="text-txt font-medium">{fmtShort(a.tenYearImpact)}</span>
                          </div>
                          <div>
                            <span className="text-muted">Retire: </span>
                            <span className="text-accent font-medium">{fmtShort(a.retirementImpact)}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* ── PEER COMPARISON ─────────────────────────────────── */}
        {wp.peerComparison.length > 0 && (
          <motion.div variants={fadeUp} className="px-4 mt-4 pb-4">
            <button
              onClick={() => setShowPeers(!showPeers)}
              className="font-mono text-muted text-[10px] tracking-widest uppercase flex items-center gap-1 cursor-pointer"
            >
              Peer Comparison
              <Chevron open={showPeers} />
            </button>
            <AnimatePresence>
              {showPeers && (
                <motion.div
                  key="peers"
                  variants={collapse}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  className="overflow-hidden"
                >
                  <div className="mt-2 space-y-2">
                    {wp.peerComparison.map((pc, i) => (
                      <div key={i} className="flex items-center justify-between bg-s1 rounded-lg px-3 py-2">
                        <span className="text-off text-sm">{pc.metric}</span>
                        <div className="flex items-center gap-3 text-xs">
                          <span className="text-txt font-medium">
                            You: {typeof pc.userValue === 'number' && pc.metric.includes('rate')
                              ? `${pc.userValue}%`
                              : fmtShort(pc.userValue)}
                          </span>
                          <span className="text-muted">
                            Median: {typeof pc.peerMedian === 'number' && pc.metric.includes('rate')
                              ? `${pc.peerMedian}%`
                              : fmtShort(pc.peerMedian)}
                          </span>
                          <span
                            className={`font-mono text-[10px] px-1.5 py-0.5 rounded ${
                              pc.percentile >= 60
                                ? 'bg-accent/15 text-accent'
                                : pc.percentile >= 40
                                  ? 'bg-amber-400/15 text-amber-400'
                                  : 'bg-red-500/15 text-red-400'
                            }`}
                          >
                            Top {100 - pc.percentile}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </motion.div>
    </ExportableCard>
  );
}
