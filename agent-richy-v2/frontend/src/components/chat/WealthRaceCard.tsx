'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { WealthRaceLeaderboard, WealthRaceProfile } from '@/lib/wealthRace';
import { ACHIEVEMENTS } from '@/lib/wealthRace';

/* ── Rarity colors ─────────────────────────────────────────────────── */

const RARITY: Record<string, { border: string; bg: string; text: string; label: string }> = {
  common:    { border: 'border-zinc-500/40', bg: 'bg-zinc-500/10', text: 'text-zinc-300', label: 'Common' },
  uncommon:  { border: 'border-accent/40',   bg: 'bg-accent/10',   text: 'text-accent',   label: 'Uncommon' },
  rare:      { border: 'border-blue-400/40', bg: 'bg-blue-400/10', text: 'text-blue-400',  label: 'Rare' },
  epic:      { border: 'border-purple-400/40', bg: 'bg-purple-400/10', text: 'text-purple-400', label: 'Epic' },
  legendary: { border: 'border-amber-400/40', bg: 'bg-amber-400/10', text: 'text-amber-400', label: 'Legendary' },
};

/* ── Animated counter ──────────────────────────────────────────────── */

function Counter({ value, suffix = '' }: { value: number; suffix?: string }) {
  return (
    <motion.span
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      <motion.span
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        {value}{suffix}
      </motion.span>
    </motion.span>
  );
}

/* ── Custom tooltip ────────────────────────────────────────────────── */

function DistTooltip({ active, payload }: { active?: boolean; payload?: { payload: { scoreRange: string; count: number; percentage: number; userInThisRange: boolean } }[] }) {
  if (!active || !payload?.[0]) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-s1 border border-line rounded-lg px-3 py-2 text-xs shadow-lg">
      <p className="text-txt font-medium">{d.scoreRange}</p>
      <p className="text-off">{d.count.toLocaleString()} users ({d.percentage}%)</p>
      {d.userInThisRange && <p className="text-accent font-medium mt-0.5">← You are here</p>}
    </div>
  );
}

/* ── Score breakdown bar ───────────────────────────────────────────── */

function ScoreRow({ label, value }: { label: string; value: number }) {
  const color = value >= 70 ? 'bg-accent' : value >= 40 ? 'bg-amber-400' : 'bg-red-400';
  return (
    <div className="flex items-center gap-3">
      <span className="text-off text-xs w-20 shrink-0">{label}</span>
      <div className="flex-1 h-2 bg-s2 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
        />
      </div>
      <span className="text-txt text-xs font-medium w-8 text-right">{value}</span>
    </div>
  );
}

/* ── Component ─────────────────────────────────────────────────────── */

interface Props {
  leaderboard: WealthRaceLeaderboard;
  profile: WealthRaceProfile;
}

export default function WealthRaceCard({ leaderboard, profile }: Props) {
  const earnedIds = new Set(profile.achievements.map((a) => a.id));

  /* Distribution chart data — sort descending by range */
  const distData = [...leaderboard.distribution].sort((a, b) => {
    const aStart = parseInt(a.scoreRange);
    const bStart = parseInt(b.scoreRange);
    return bStart - aStart;
  });

  /* Next percentile progress */
  const { currentPercentile, nextPercentile, whatItTakes } = leaderboard.toNextPercentile;
  const pctProgress = nextPercentile > 0
    ? Math.min(100, Math.round(((100 - currentPercentile) / (100 - nextPercentile)) * 100))
    : 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="bg-card border border-line rounded-card overflow-hidden w-full"
    >
      {/* ── Rank Hero ──────────────────────────────────────────────── */}
      <div className="bg-gradient-to-br from-s1 to-card p-6 text-center">
        <p className="font-mono text-accent text-xs tracking-widest">YOUR RANK</p>

        <p className="text-4xl font-bold text-accent mt-2">
          Top <Counter value={leaderboard.userPercentile} suffix="%" />
        </p>

        <p className="text-off text-sm mt-1">
          Better than {100 - leaderboard.userPercentile}% of {profile.ageGroup} in {profile.region}
        </p>

        <div className="mt-4 inline-flex items-center gap-2 bg-s2/60 rounded-full px-4 py-2">
          <span className="text-txt text-2xl font-bold">
            <Counter value={profile.overallScore} />
          </span>
          <span className="text-muted text-xs">/ 100</span>
        </div>

        {/* Score breakdown */}
        <div className="mt-4 max-w-xs mx-auto space-y-2">
          <ScoreRow label="Savings" value={profile.savingsScore} />
          <ScoreRow label="Debt" value={profile.debtScore} />
          <ScoreRow label="Investing" value={profile.investingScore} />
          <ScoreRow label="Spending" value={profile.spendingScore} />
          <ScoreRow label="Knowledge" value={profile.knowledgeScore} />
        </div>
      </div>

      <div className="p-5 space-y-5">
        {/* ── To Next Level ──────────────────────────────────────────── */}
        <div className="bg-accent/10 border border-accent/20 rounded-lg p-4 text-center">
          <p className="text-off text-sm">{whatItTakes}</p>
          <div className="mt-3 h-3 bg-s2 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-accent rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${pctProgress}%` }}
              transition={{ duration: 1, ease: [0.22, 1, 0.36, 1], delay: 0.4 }}
            />
          </div>
          <p className="text-muted text-xs mt-1.5">
            Top {currentPercentile}% → Top {nextPercentile}%
          </p>
        </div>

        {/* ── Distribution Chart ─────────────────────────────────────── */}
        <div>
          <p className="font-mono text-accent text-xs tracking-widest mb-3">SCORE DISTRIBUTION</p>
          <div className="bg-card border border-line rounded-lg p-4">
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={distData} layout="vertical" margin={{ left: 4, right: 4 }}>
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="scoreRange"
                  tick={{ fill: '#9CA3AF', fontSize: 11, fontFamily: 'IBM Plex Mono, monospace' }}
                  width={52}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip content={<DistTooltip />} cursor={false} />
                <ReferenceLine x={0} stroke="transparent" />
                <Bar dataKey="percentage" radius={[0, 4, 4, 0]} maxBarSize={18}>
                  {distData.map((entry, i) => (
                    <Cell
                      key={i}
                      fill={entry.userInThisRange ? '#00E87B' : '#2A3A30'}
                      stroke={entry.userInThisRange ? '#00E87B' : 'transparent'}
                      strokeWidth={entry.userInThisRange ? 1 : 0}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* ── Streaks ────────────────────────────────────────────────── */}
        <div>
          <p className="font-mono text-accent text-xs tracking-widest mb-3">STREAKS</p>
          <div className="flex gap-3">
            <div className="flex-1 bg-s1 rounded-lg p-3 text-center">
              <p className="text-2xl">🔥</p>
              <p className="text-txt text-lg font-bold mt-1">
                <Counter value={profile.streaks.currentEngagementStreak} />
              </p>
              <p className="text-muted text-[10px] font-mono tracking-wider">CURRENT</p>
            </div>
            <div className="flex-1 bg-s1 rounded-lg p-3 text-center">
              <p className="text-2xl">⚡</p>
              <p className="text-txt text-lg font-bold mt-1">
                <Counter value={profile.streaks.longestStreak} />
              </p>
              <p className="text-muted text-[10px] font-mono tracking-wider">LONGEST</p>
            </div>
            <div className="flex-1 bg-s1 rounded-lg p-3 text-center">
              <p className="text-2xl">💰</p>
              <p className="text-txt text-lg font-bold mt-1">
                <Counter value={profile.streaks.currentSavingsStreak} />
              </p>
              <p className="text-muted text-[10px] font-mono tracking-wider">SAVINGS MO</p>
            </div>
          </div>
        </div>

        {/* ── Achievements ───────────────────────────────────────────── */}
        <div>
          <p className="font-mono text-accent text-xs tracking-widest mb-3">
            ACHIEVEMENTS ({profile.achievements.length} / {ACHIEVEMENTS.length})
          </p>
          <div className="grid grid-cols-4 sm:grid-cols-6 gap-2">
            {ACHIEVEMENTS.map((ach) => {
              const earned = earnedIds.has(ach.id);
              const r = RARITY[ach.rarity] ?? RARITY.common;

              return (
                <motion.div
                  key={ach.id}
                  whileHover={{ scale: 1.08 }}
                  className={`relative flex flex-col items-center p-2 rounded-lg border text-center cursor-default transition-colors ${
                    earned
                      ? `${r.border} ${r.bg}`
                      : 'border-line bg-s2/40 opacity-40 grayscale'
                  }`}
                  title={`${ach.name}: ${ach.description}${earned ? '' : ' (Locked)'}`}
                >
                  <span className="text-xl leading-none">{ach.icon}</span>
                  <span className={`text-[9px] font-medium mt-1 leading-tight ${earned ? r.text : 'text-muted'}`}>
                    {ach.name}
                  </span>
                  {earned && (
                    <span className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${r.bg} ${r.border} border`} />
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* ── Leaderboard Preview ────────────────────────────────────── */}
        {leaderboard.topPerformers.length > 0 && (
          <div>
            <p className="font-mono text-accent text-xs tracking-widest mb-3">
              TOP PERFORMERS — {leaderboard.category}
            </p>
            <div className="space-y-1">
              {leaderboard.topPerformers.map((p) => (
                <div
                  key={p.rank}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${
                    p.isCurrentUser ? 'bg-accent/10 border border-accent/20' : 'bg-s1'
                  }`}
                >
                  <span className="text-muted font-mono text-xs w-6 text-right">#{p.rank}</span>
                  <span className={`flex-1 ${p.isCurrentUser ? 'text-accent font-semibold' : 'text-off'}`}>
                    {p.isCurrentUser ? 'You' : p.anonymousLabel}
                  </span>
                  <span className="text-txt font-medium">{p.score}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
