'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import type { GoalSimulationResult } from '@/types/tools';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

function fmtShort(n: number): string {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
  return fmt(n);
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}

/* ── Progress Ring SVG ─────────────────────────────────────────────── */

function ProgressRing({ percent, size = 120 }: { percent: number; size?: number }) {
  const stroke = 8;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const filled = Math.min(percent, 100);
  const offset = circumference - (filled / 100) * circumference;

  return (
    <svg width={size} height={size} className="transform -rotate-90">
      {/* Track */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        className="stroke-s2"
        strokeWidth={stroke}
      />
      {/* Filled */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        className="stroke-accent"
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        style={{ transition: 'stroke-dashoffset 1s ease-out' }}
      />
    </svg>
  );
}

/* ── Probability Gauge ─────────────────────────────────────────────── */

function ProbabilityGauge({ probability }: { probability: number }) {
  const color =
    probability >= 75
      ? 'text-accent'
      : probability >= 50
      ? 'text-amber-400'
      : 'text-red-400';
  const bgColor =
    probability >= 75
      ? 'stroke-accent'
      : probability >= 50
      ? 'stroke-amber-400'
      : 'stroke-red-400';

  const size = 100;
  const stroke = 7;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (probability / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            className="stroke-s2"
            strokeWidth={stroke}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            className={bgColor}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1s ease-out' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-xl font-bold ${color}`}>{probability}%</span>
        </div>
      </div>
      <span className="text-muted text-xs mt-1">Chance of success</span>
    </div>
  );
}

/* ── Stagger wrapper ───────────────────────────────────────────────── */

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
};

/* ── Component ─────────────────────────────────────────────────────── */

export default function GoalSimulatorCard({
  result,
}: {
  result: GoalSimulationResult;
}) {
  const [boostsOpen, setBoostsOpen] = useState(true);
  const percent = Math.min(
    Math.round((result.currentSaved / result.targetAmount) * 100),
    100,
  );

  const fastestScenario = result.scenarios.reduce(
    (min, s) => (s.monthsToGoal < min.monthsToGoal ? s : min),
    result.scenarios[0],
  );

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={stagger}
      className="bg-card border border-line rounded-card overflow-hidden"
    >
      {/* ── 1. HERO ───────────────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="bg-s1 rounded-card p-6">
        <h3 className="text-2xl font-bold text-txt">{result.goalName}</h3>

        {/* Progress ring + stats */}
        <div className="flex flex-col sm:flex-row items-center gap-6 mt-5">
          {/* Ring */}
          <div className="relative shrink-0">
            <ProgressRing percent={percent} size={120} />
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-accent text-3xl font-bold">{percent}%</span>
            </div>
          </div>

          {/* Stats */}
          <div className="flex-1 text-center sm:text-left space-y-1.5">
            <p className="text-off">
              {fmt(result.currentSaved)} of {fmt(result.targetAmount)}
            </p>
            <p className="text-accent font-semibold">
              Reaching your goal in {result.monthsToGoal} months
            </p>
            <p className="text-muted">
              Target: {formatDate(result.projectedCompletionDate)}
            </p>
            <p className="text-off text-sm">
              That&apos;s just {fmt(result.dailyEquivalent)}/day
            </p>
          </div>
        </div>
      </motion.div>

      <div className="p-5 space-y-6">
        {/* ── 2. SCENARIOS ──────────────────────────────────────────── */}
        {result.scenarios.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-wider mb-3">
              Scenarios
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {result.scenarios.map((s) => {
                const isFastest = s === fastestScenario && result.scenarios.length > 1;
                return (
                  <div
                    key={s.name}
                    className="bg-card border border-line rounded-card p-4 relative"
                  >
                    {isFastest && (
                      <span className="absolute top-2 right-2 bg-accent/15 text-accent font-mono text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full">
                        Fastest
                      </span>
                    )}
                    <p className="text-txt font-medium text-sm pr-16">{s.name}</p>
                    <p className="text-accent text-xl font-bold mt-1">
                      {fmt(s.monthlyAmount)}/mo
                    </p>
                    <p className="text-muted text-sm mt-1">
                      {s.monthsToGoal} months &middot; {formatDate(s.completionDate)}
                    </p>
                    <p className="text-off text-xs mt-1">{s.description}</p>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* ── 3. MILESTONE TIMELINE ─────────────────────────────────── */}
        {result.milestones.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-wider mb-3">
              Milestones
            </p>
            <div className="relative">
              {/* Track */}
              <div className="bg-s2 rounded-full h-3 relative overflow-hidden">
                <div
                  className="bg-accent rounded-full h-full"
                  style={{ width: `${percent}%`, transition: 'width 1s ease-out' }}
                />
              </div>

              {/* Pulsing current position */}
              <div
                className="absolute top-0 h-3 flex items-center"
                style={{ left: `${percent}%`, transform: 'translateX(-50%)' }}
              >
                <span className="w-3.5 h-3.5 rounded-full bg-accent ring-2 ring-accent/30 animate-pulse" />
              </div>

              {/* Milestone markers */}
              <div className="relative mt-4">
                {result.milestones.map((m) => (
                  <div
                    key={m.percentage}
                    className="absolute flex flex-col items-center"
                    style={{
                      left: `${m.percentage}%`,
                      transform: 'translateX(-50%)',
                    }}
                  >
                    <span className="w-2 h-2 rounded-full bg-accent/60" />
                    <span className="text-muted text-[10px] mt-1 whitespace-nowrap">
                      {formatDate(m.projectedDate)}
                    </span>
                    <span className="text-off text-[10px] whitespace-nowrap">
                      {fmtShort(m.amount)}
                    </span>
                  </div>
                ))}
              </div>

              {/* Spacer for markers */}
              <div className="h-12" />
            </div>
          </motion.div>
        )}

        {/* ── 4. BOOST SUGGESTIONS ──────────────────────────────────── */}
        {result.boostSuggestions.length > 0 && (
          <motion.div variants={fadeUp}>
            <button
              onClick={() => setBoostsOpen((v) => !v)}
              className="font-mono text-accent text-xs uppercase tracking-wider mb-3 cursor-pointer hover:underline focus:outline-none"
            >
              {boostsOpen ? 'Ways to get there faster ↑' : 'Ways to get there faster →'}
            </button>

            {boostsOpen && (
              <div className="space-y-2">
                {result.boostSuggestions.map((b, i) => (
                  <div
                    key={i}
                    className="bg-card border border-line rounded-lg p-3 flex items-center justify-between gap-3"
                  >
                    <span className="text-off text-sm">{b.action}</span>
                    <span className="shrink-0 bg-accent/15 text-accent font-mono text-xs px-2 py-1 rounded-full whitespace-nowrap">
                      Save {b.timeSaved} mo
                    </span>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* ── 5. MONTE CARLO ────────────────────────────────────────── */}
        {result.monteCarlo && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-wider mb-3">
              Probability Analysis
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-6">
              {/* Gauge */}
              <ProbabilityGauge probability={result.monteCarlo.probabilityOfSuccess} />

              {/* Percentile range bar */}
              <div className="flex-1 w-full">
                <div className="relative h-6 rounded-full overflow-hidden bg-s2">
                  {/* Gradient fill from p10 to p90 */}
                  <div
                    className="absolute inset-y-0 rounded-full"
                    style={{
                      left: `${(result.monteCarlo.percentile10 / result.monteCarlo.percentile90) * 20}%`,
                      right: '0%',
                      background:
                        'linear-gradient(to right, rgba(239,68,68,0.3), rgba(0,232,123,0.3), rgba(0,232,123,0.7))',
                    }}
                  />
                  {/* Median marker */}
                  <div
                    className="absolute inset-y-0 w-0.5 bg-accent"
                    style={{
                      left: `${(result.monteCarlo.percentile50 / result.monteCarlo.percentile90) * 100}%`,
                    }}
                  />
                </div>

                <div className="flex justify-between mt-1.5 text-[10px]">
                  <span className="text-red-400">
                    Worst: {fmtShort(result.monteCarlo.percentile10)}
                  </span>
                  <span className="text-accent font-semibold">
                    Likely: {fmtShort(result.monteCarlo.percentile50)}
                  </span>
                  <span className="text-accent/70">
                    Best: {fmtShort(result.monteCarlo.percentile90)}
                  </span>
                </div>
              </div>
            </div>

            <p className="text-muted text-xs mt-2">
              Based on {result.monteCarlo.simulations.toLocaleString()} simulated
              outcomes using historical market data
            </p>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
