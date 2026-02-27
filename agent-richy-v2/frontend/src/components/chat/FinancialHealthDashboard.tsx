'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PieChart, Pie, Cell,
  ResponsiveContainer, Tooltip,
} from 'recharts';
import type { FinancialDNA } from '@/lib/financialDNA';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function pct(n: number): string {
  return `${Math.round(n)}%`;
}

function clamp(n: number, min = 0, max = 100): number {
  return Math.max(min, Math.min(max, n));
}

/* ── Animation ─────────────────────────────────────────────────────── */

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
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

/* ── Color palette ─────────────────────────────────────────────────── */

const SCORE_COLORS = ['#00E87B', '#3B82F6', '#A78BFA', '#F59E0B', '#06B6D4'];

function scoreColor(score: number): string {
  if (score >= 80) return '#00E87B';
  if (score >= 60) return '#3B82F6';
  if (score >= 40) return '#F59E0B';
  return '#EF4444';
}

function trajectoryLabel(t: 'improving' | 'stable' | 'declining'): {
  icon: string;
  label: string;
  color: string;
} {
  switch (t) {
    case 'improving':
      return { icon: '↑', label: 'Improving', color: 'text-accent' };
    case 'declining':
      return { icon: '↓', label: 'Declining', color: 'text-red-400' };
    default:
      return { icon: '→', label: 'Stable', color: 'text-muted' };
  }
}

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

/* ── Score bar sub-component ───────────────────────────────────────── */

function ScoreBar({
  label,
  score,
  color,
}: {
  label: string;
  score: number;
  color: string;
}) {
  const s = clamp(score);
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-off text-xs">{label}</span>
        <span className="text-txt text-xs font-medium">{s}</span>
      </div>
      <div className="w-full h-2 bg-s2 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${s}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
    </div>
  );
}

/* ── Goal progress bar ─────────────────────────────────────────────── */

function GoalBar({
  name,
  current,
  target,
  onTrack,
}: {
  name: string;
  current: number;
  target: number;
  onTrack: boolean;
}) {
  const progress = target > 0 ? clamp((current / target) * 100) : 0;
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-off text-sm truncate mr-2">{name}</span>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-txt text-xs font-medium">
            {fmt(current)} / {fmt(target)}
          </span>
          <span className={`text-[10px] ${onTrack ? 'text-accent' : 'text-amber-400'}`}>
            {onTrack ? '● On track' : '● Behind'}
          </span>
        </div>
      </div>
      <div className="w-full h-2 bg-s2 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`h-full rounded-full ${onTrack ? 'bg-accent' : 'bg-amber-400'}`}
        />
      </div>
    </div>
  );
}

/* ── Circular gauge (SVG) ──────────────────────────────────────────── */

function CircularGauge({ score, size = 140 }: { score: number; size?: number }) {
  const s = clamp(score);
  const r = (size - 16) / 2;
  const circumference = 2 * Math.PI * r;
  const strokeDash = (s / 100) * circumference;
  const color = scoreColor(s);

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="block">
      {/* Background ring */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="currentColor"
        className="text-s2"
        strokeWidth={10}
      />
      {/* Score ring */}
      <motion.circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={10}
        strokeLinecap="round"
        strokeDasharray={circumference}
        initial={{ strokeDashoffset: circumference }}
        animate={{ strokeDashoffset: circumference - strokeDash }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      {/* Score text */}
      <text
        x={size / 2}
        y={size / 2}
        textAnchor="middle"
        dominantBaseline="central"
        className="fill-txt font-bold"
        fontSize={size * 0.28}
      >
        {s}
      </text>
    </svg>
  );
}

/* ── Custom tooltip ────────────────────────────────────────────────── */

interface RadarPayloadEntry {
  name: string;
  value: number;
}

function RadarTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: RadarPayloadEntry[];
}) {
  if (!active || !payload || payload.length === 0) return null;
  const d = payload[0];
  return (
    <div className="bg-card border border-line rounded-lg px-3 py-2 shadow-lg">
      <p className="text-txt text-xs font-medium">{d.name}</p>
      <p className="text-accent text-sm font-bold">{d.value}</p>
    </div>
  );
}

/* ── Main component ────────────────────────────────────────────────── */

interface Props {
  dna: FinancialDNA;
}

export default function FinancialHealthDashboard({ dna }: Props) {
  const [showWeaknesses, setShowWeaknesses] = useState(true);

  const { scores, spendingFingerprint, wealthProfile, goals } = dna;
  const traj = trajectoryLabel(scores.trajectory);

  /* Score breakdown data */
  const scoreBreakdown = [
    { label: 'Spending Efficiency', score: scores.spendingEfficiency, color: SCORE_COLORS[0] },
    { label: 'Debt Management', score: scores.debtManagement, color: SCORE_COLORS[1] },
    { label: 'Savings & Investing', score: scores.savingsAndInvesting, color: SCORE_COLORS[2] },
    { label: 'Financial Knowledge', score: scores.financialKnowledge, color: SCORE_COLORS[3] },
    { label: 'Cash Flow Health', score: dna.cashFlow.cashFlowScore, color: SCORE_COLORS[4] },
  ];

  /* Radar data — spending fingerprint behavioral axes */
  const radarData = [
    { axis: 'Planned', value: spendingFingerprint.planningScore },
    { axis: 'Price Conscious', value: spendingFingerprint.priceConsciousness },
    { axis: 'Impulse Control', value: 100 - spendingFingerprint.impulseSpendingScore },
    { axis: 'Brand Loyalty', value: spendingFingerprint.brandLoyalty },
  ];

  /* Top spending categories for mini donut */
  const categoryData = spendingFingerprint.topCategories
    .slice(0, 5)
    .map((c) => ({ name: c.category, value: c.monthlyAmount }));

  /* Net worth - single point for display (history would require time-series data) */
  const netWorth = wealthProfile.netWorth;

  return (
    <motion.div
      variants={stagger}
      initial="hidden"
      animate="show"
      className="bg-card border border-line rounded-card overflow-hidden"
    >
      {/* ── HEADER ────────────────────────────────────────────── */}
      <div className="bg-gradient-to-r from-s1 to-card p-6">
        <p className="font-mono text-accent text-xs tracking-widest uppercase">
          Financial Health Dashboard
        </p>
        <p className="text-muted text-xs mt-0.5">
          Your Financial DNA — updated {new Date(dna.lastUpdated).toLocaleDateString()}
        </p>
      </div>

      {/* ── OVERALL SCORE ─────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="flex flex-col items-center py-6">
        <CircularGauge score={scores.overallFinancialHealth} size={160} />

        <div className="flex items-center gap-2 mt-3">
          <span className={`text-lg font-semibold ${traj.color}`}>
            {traj.icon}
          </span>
          <span className={`text-sm font-medium ${traj.color}`}>
            {traj.label}
          </span>
        </div>

        {scores.percentileAmongUsers > 0 && (
          <p className="text-muted text-xs mt-1">
            Better than {scores.percentileAmongUsers}% of users your age
          </p>
        )}
      </motion.div>

      {/* ── SCORE BREAKDOWN ───────────────────────────────────── */}
      <motion.div variants={fadeUp} className="px-4 pb-4">
        <p className="font-mono text-muted text-[10px] tracking-widest uppercase mb-3">
          Score Breakdown
        </p>
        <div className="space-y-3">
          {scoreBreakdown.map((s) => (
            <ScoreBar key={s.label} label={s.label} score={s.score} color={s.color} />
          ))}
        </div>
      </motion.div>

      {/* ── SPENDING FINGERPRINT — RADAR ──────────────────────── */}
      {radarData.some((d) => d.value > 0) && (
        <motion.div variants={fadeUp} className="px-4 pb-4">
          <p className="font-mono text-muted text-[10px] tracking-widest uppercase mb-3">
            Spending Fingerprint
          </p>
          <div className="bg-s1 rounded-card p-3">
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="70%">
                <PolarGrid stroke="#1E2D26" />
                <PolarAngleAxis
                  dataKey="axis"
                  tick={{ fill: '#8B9A8F', fontSize: 11 }}
                />
                <Radar
                  dataKey="value"
                  stroke="#00E87B"
                  fill="#00E87B"
                  fillOpacity={0.15}
                  strokeWidth={2}
                  dot={{ r: 3, fill: '#00E87B' }}
                />
                <Tooltip content={<RadarTooltip />} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}

      {/* ── TOP CATEGORIES — MINI DONUT ───────────────────────── */}
      {categoryData.length > 0 && (
        <motion.div variants={fadeUp} className="px-4 pb-4">
          <p className="font-mono text-muted text-[10px] tracking-widest uppercase mb-3">
            Top Spending Categories
          </p>
          <div className="flex items-center gap-4">
            <div className="w-[120px] h-[120px] shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={30}
                    outerRadius={50}
                    strokeWidth={0}
                  >
                    {categoryData.map((_, i) => (
                      <Cell
                        key={i}
                        fill={SCORE_COLORS[i % SCORE_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number) => fmt(value)}
                    contentStyle={{
                      backgroundColor: '#101A15',
                      border: '1px solid #1E2D26',
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 space-y-1.5">
              {categoryData.map((c, i) => (
                <div key={c.name} className="flex items-center gap-2 text-xs">
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: SCORE_COLORS[i % SCORE_COLORS.length] }}
                  />
                  <span className="text-off flex-1 truncate">{c.name}</span>
                  <span className="text-txt font-medium">{fmt(c.value)}/mo</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* ── STRENGTHS & WEAKNESSES ────────────────────────────── */}
      {(spendingFingerprint.spendingStrengths.length > 0 ||
        spendingFingerprint.spendingWeaknesses.length > 0) && (
        <motion.div variants={fadeUp} className="px-4 pb-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Strengths */}
            {spendingFingerprint.spendingStrengths.length > 0 && (
              <div>
                <p className="font-mono text-accent text-[10px] tracking-widest uppercase mb-2">
                  Strengths
                </p>
                <ul className="space-y-2">
                  {spendingFingerprint.spendingStrengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-accent mt-0.5 shrink-0">✓</span>
                      <div>
                        <p className="text-txt text-sm font-medium">{s.category}</p>
                        <p className="text-muted text-xs">{s.description}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Weaknesses */}
            {spendingFingerprint.spendingWeaknesses.length > 0 && (
              <div>
                <button
                  onClick={() => setShowWeaknesses(!showWeaknesses)}
                  className="font-mono text-amber-400 text-[10px] tracking-widest uppercase mb-2 flex items-center gap-1 cursor-pointer"
                >
                  Areas to Improve
                  <Chevron open={showWeaknesses} />
                </button>
                <AnimatePresence>
                  {showWeaknesses && (
                    <motion.ul
                      variants={collapse}
                      initial="initial"
                      animate="animate"
                      exit="exit"
                      className="space-y-2 overflow-hidden"
                    >
                      {spendingFingerprint.spendingWeaknesses.map((w, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-amber-400 mt-0.5 shrink-0">!</span>
                          <div>
                            <p className="text-txt text-sm font-medium">{w.category}</p>
                            <p className="text-muted text-xs">{w.description}</p>
                            {w.suggestedIntervention && (
                              <p className="text-accent text-xs mt-0.5">
                                → {w.suggestedIntervention}
                              </p>
                            )}
                            {w.estimatedMonthlyCost > 0 && (
                              <p className="text-red-400 text-[11px] mt-0.5">
                                ~{fmt(w.estimatedMonthlyCost)}/mo impact
                              </p>
                            )}
                          </div>
                        </li>
                      ))}
                    </motion.ul>
                  )}
                </AnimatePresence>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* ── NET WORTH ─────────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="px-4 pb-4">
        <p className="font-mono text-muted text-[10px] tracking-widest uppercase mb-3">
          Net Worth
        </p>
        <div className="bg-s1 rounded-card p-4 flex items-center justify-between">
          <div>
            <p className={`text-2xl font-bold ${netWorth >= 0 ? 'text-accent' : 'text-red-400'}`}>
              {fmt(netWorth)}
            </p>
            <p className="text-muted text-xs mt-0.5">
              Assets {fmt(wealthProfile.totalSavings + wealthProfile.totalInvestments)} −
              Debt {fmt(dna.debtProfile.totalDebt)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-off text-xs">Savings Rate</p>
            <p className="text-txt text-lg font-semibold">{pct(wealthProfile.savingsRate)}</p>
          </div>
        </div>

        {/* Emergency fund status */}
        <div className="mt-2 flex items-center gap-2 text-xs">
          <span
            className={`w-2 h-2 rounded-full shrink-0 ${
              wealthProfile.emergencyFund.adequate ? 'bg-accent' : 'bg-amber-400'
            }`}
          />
          <span className="text-off">
            Emergency fund: {wealthProfile.emergencyFund.monthsCovered.toFixed(1)} months
            {wealthProfile.emergencyFund.adequate ? ' ✓' : ' — needs attention'}
          </span>
        </div>
      </motion.div>

      {/* ── GOALS ─────────────────────────────────────────────── */}
      {goals.active.length > 0 && (
        <motion.div variants={fadeUp} className="px-4 pb-6">
          <p className="font-mono text-muted text-[10px] tracking-widest uppercase mb-3">
            Active Goals
          </p>
          <div className="space-y-3">
            {goals.active.map((g) => (
              <GoalBar
                key={g.id}
                name={g.name}
                current={g.currentProgress}
                target={g.targetAmount}
                onTrack={g.onTrack}
              />
            ))}
          </div>

          {/* Mentioned goals (informal) */}
          {goals.mentioned.length > 0 && (
            <div className="mt-3 pt-3 border-t border-line">
              <p className="text-muted text-[10px] font-mono uppercase tracking-wider mb-1.5">
                You&apos;ve mentioned wanting
              </p>
              <div className="flex flex-wrap gap-1.5">
                {goals.mentioned.map((m, i) => (
                  <span
                    key={i}
                    className="text-xs text-off bg-s2 px-2 py-0.5 rounded-full"
                  >
                    {m}
                  </span>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}
