'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AreaChart, Area, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, ReferenceDot,
} from 'recharts';
import ExportableCard from './ExportableCard';
import type { RippleTrackerData, RippleEffect } from '@/types/moneyMap';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function fmtShort(n: number): string {
  if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
  return fmt(n);
}

function fmtHourly(n: number): string {
  return `$${n.toFixed(2)}`;
}

/* ── Animation ─────────────────────────────────────────────────────── */

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.38, ease: 'easeOut' } },
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.85 },
  show: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
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
      width="14" height="14" viewBox="0 0 16 16" fill="none"
      className={`text-muted transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
    >
      <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/* ── Custom chart tooltip ──────────────────────────────────────────── */

interface ChartPayload {
  value?: number;
  dataKey?: string;
  name?: string;
}

function CompoundTooltip({ active, payload, label }: {
  active?: boolean;
  payload?: ChartPayload[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  const saved = payload.find(p => p.dataKey === 'saved')?.value ?? 0;
  const invested = payload.find(p => p.dataKey === 'invested')?.value ?? 0;
  return (
    <div className="bg-s1 border border-line rounded-lg px-3 py-2 text-xs shadow-lg">
      <p className="text-muted font-mono mb-1">Year {label}</p>
      <p className="text-accent">Invested: {fmtShort(invested)}</p>
      <p className="text-txt-off">Raw savings: {fmtShort(saved)}</p>
      <p className="text-muted mt-1 text-[10px]">Growth: {fmtShort(invested - saved)}</p>
    </div>
  );
}

/* ── Ripple ring animation ─────────────────────────────────────────── */

function RippleRing({ delay, size }: { delay: number; size: number }) {
  return (
    <motion.div
      className="absolute rounded-full border border-accent/30"
      style={{
        width: size,
        height: size,
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
      }}
      initial={{ opacity: 0, scale: 0.3 }}
      animate={{ opacity: [0, 0.5, 0], scale: [0.3, 1, 1.3] }}
      transition={{
        duration: 2.5,
        delay,
        repeat: Infinity,
        ease: 'easeOut',
      }}
    />
  );
}

/* ── Single ripple card ────────────────────────────────────────────── */

function RippleCard({ ripple }: { ripple: RippleEffect }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div variants={fadeUp} className="bg-card border border-line rounded-card p-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left cursor-pointer"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <p className="text-txt font-medium text-sm">{ripple.trigger}</p>
            <p className="text-accent font-mono text-xs mt-0.5">
              {fmt(ripple.monthlySavings)}/month
            </p>
          </div>
          <Chevron open={expanded} />
        </div>

        {/* Ripple chain preview — always visible */}
        <div className="mt-3 space-y-0">
          {ripple.ripples.map((r, i) => (
            <div
              key={i}
              className="flex items-center gap-2 py-1"
              style={{ paddingLeft: i * 12 }}
            >
              {/* Ripple dot */}
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{
                  backgroundColor: `rgba(0, 232, 123, ${1 - i * 0.15})`,
                  boxShadow: i === 0 ? '0 0 6px rgba(0,232,123,0.4)' : 'none',
                }}
              />
              {/* Timeframe */}
              <span className="text-[11px] text-muted font-mono w-20 flex-shrink-0">{r.timeframe}</span>
              {/* Amount */}
              <span
                className="text-[11px] font-mono font-medium"
                style={{ color: `rgba(0, 232, 123, ${1 - i * 0.12})` }}
              >
                {fmtShort(r.investedAmount)}
              </span>
              {/* Milestone */}
              {r.milestone && (
                <span className="text-[10px] text-txt-off ml-1 hidden sm:inline">
                  — {r.milestone}
                </span>
              )}
            </div>
          ))}
        </div>
      </button>

      {/* Expanded details */}
      <AnimatePresence>
        {expanded && (
          <motion.div {...collapse} className="overflow-hidden">
            <div className="mt-3 pt-3 border-t border-line space-y-2">
              {/* Descriptions */}
              {ripple.ripples.map((r, i) => (
                <p key={i} className="text-xs text-txt-off" style={{ paddingLeft: i * 8 }}>
                  {r.description}
                </p>
              ))}

              {/* Goal impacts */}
              {ripple.goalImpact.length > 0 && (
                <div className="mt-2 space-y-1">
                  {ripple.goalImpact.map((g, i) => (
                    <p key={i} className="text-accent text-sm">
                      🎯 {g.timeSaved}
                    </p>
                  ))}
                </div>
              )}

              {/* Metric impacts */}
              <div className="flex flex-wrap gap-3 mt-2">
                {ripple.metricsImpact.savingsRateChange !== 0 && (
                  <span className="text-muted text-xs font-mono">
                    +{ripple.metricsImpact.savingsRateChange.toFixed(2)}% savings rate
                  </span>
                )}
                {ripple.metricsImpact.retirementAcceleration > 0 && (
                  <span className="text-muted text-xs font-mono">
                    {ripple.metricsImpact.retirementAcceleration}d sooner to retire
                  </span>
                )}
                {ripple.metricsImpact.dailyEquivalent > 0 && (
                  <span className="text-muted text-xs font-mono">
                    ${ripple.metricsImpact.dailyEquivalent.toFixed(2)}/day for your future
                  </span>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ── Build export data ─────────────────────────────────────────────── */

function buildExport(data: RippleTrackerData) {
  const r = data.invisibleRaise;
  const lines = [
    `💸 YOUR INVISIBLE RAISE`,
    '',
    `Pre-tax equivalent: ${fmt(r.equivalentPreTaxRaise)}/year`,
    `Effective hourly:   ${fmtHourly(r.effectiveHourlyRaise)}/hr`,
    `Implemented:        ${fmt(r.implementedSavings)}/year`,
    `Pending:            ${fmt(r.pendingSavings)}/year`,
    '',
    data.powerStatement,
    '',
    `── COMPOUND PROJECTION ──`,
    `Year 1:  ${fmt(r.compoundProjection.year1)}`,
    `Year 5:  ${fmt(r.compoundProjection.year5)}`,
    `Year 10: ${fmt(r.compoundProjection.year10)}`,
    `Year 20: ${fmt(r.compoundProjection.year20)}`,
    `Year 30: ${fmt(r.compoundProjection.year30)}`,
    '',
    `── EQUIVALENT TO ──`,
    ...r.equivalentTo.map(e => `  ${e.icon} ${e.description}`),
    '',
    `── RECENT RIPPLES ──`,
    ...data.recentRipples.map(rip =>
      `  ${rip.trigger}: ${fmt(rip.monthlySavings)}/mo → ${fmtShort(rip.ripples[rip.ripples.length - 1]?.investedAmount ?? 0)} at retirement`
    ),
    '',
    `── MILESTONES ──`,
    ...r.milestones.map(m => `  ${m.reached ? '✅' : '🔒'} ${m.name} (${fmt(m.threshold)})`),
  ];
  const text = lines.join('\n');
  return { clipboard: text, formatted: text };
}

/* ══════════════════════════════════════════════════════════════════════
   MAIN COMPONENT
   ══════════════════════════════════════════════════════════════════════ */

export default function RippleTrackerCard({ data }: { data: RippleTrackerData }) {
  const [showHistory, setShowHistory] = useState(false);
  const exportData = useMemo(() => buildExport(data), [data]);

  const raise = data.invisibleRaise;
  const totalBar = raise.implementedSavings + raise.pendingSavings;
  const implementedPct = totalBar > 0 ? (raise.implementedSavings / totalBar) * 100 : 0;

  /* ── Compound chart data ──────────────────────────────────────── */
  const compoundData = useMemo(() => {
    const cp = raise.compoundProjection;
    const annual = raise.totalAnnualSavings;
    return [
      { year: '0', saved: 0, invested: 0 },
      { year: '1', saved: annual, invested: cp.year1 },
      { year: '5', saved: annual * 5, invested: cp.year5 },
      { year: '10', saved: annual * 10, invested: cp.year10 },
      { year: '20', saved: annual * 20, invested: cp.year20 },
      { year: '30', saved: annual * 30, invested: cp.year30 },
    ];
  }, [raise]);

  /* ── Milestone progress ───────────────────────────────────────── */
  const milestones = raise.milestones;
  const maxMilestone = milestones.length > 0 ? milestones[milestones.length - 1].threshold : 10000;
  const currentRaise = raise.totalAnnualSavings;

  /* ── History chart data ───────────────────────────────────────── */
  const historyData = raise.monthlyHistory;

  return (
    <ExportableCard title="Your Invisible Raise" exportData={exportData}>
      <motion.div
        variants={stagger}
        initial="hidden"
        animate="show"
        className="bg-card border border-line rounded-t-card overflow-hidden"
      >

        {/* ── 1. INVISIBLE RAISE HERO ────────────────────────────── */}
        <motion.div
          variants={scaleIn}
          className="relative bg-gradient-to-br from-accent/20 via-s1 to-card p-8 text-center overflow-hidden"
        >
          {/* Ambient ripple rings */}
          <div className="absolute inset-0 pointer-events-none">
            <RippleRing delay={0} size={160} />
            <RippleRing delay={0.8} size={280} />
            <RippleRing delay={1.6} size={400} />
          </div>

          <div className="relative z-10">
            <span className="font-mono text-accent text-xs tracking-label">YOUR INVISIBLE RAISE</span>

            <motion.p
              className="text-5xl sm:text-6xl font-bold text-accent mt-3 font-mono tracking-tight"
              initial={{ opacity: 0, scale: 0.7 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            >
              {fmt(raise.equivalentPreTaxRaise)}
              <span className="text-lg text-accent/60 font-normal">/year</span>
            </motion.p>

            <p className="text-txt-off text-lg mt-2">
              equivalent to a <span className="text-txt font-semibold">{fmtHourly(raise.effectiveHourlyRaise)}/hr</span> raise
            </p>

            {/* Implemented vs pending bar */}
            <div className="max-w-xs mx-auto mt-5">
              <div className="h-2 bg-line rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-accent rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${implementedPct}%` }}
                  transition={{ duration: 1, delay: 0.5, ease: 'easeOut' }}
                />
              </div>
              <p className="text-muted text-sm mt-2">
                <span className="text-accent font-mono">{fmt(raise.implementedSavings)}</span> confirmed
                {raise.pendingSavings > 0 && (
                  <> · <span className="text-txt-off font-mono">{fmt(raise.pendingSavings)}</span> waiting on you</>
                )}
              </p>
            </div>
          </div>
        </motion.div>

        {/* ── 2. POWER STATEMENT ─────────────────────────────────── */}
        <motion.div variants={fadeUp} className="mx-4 mt-4">
          <div className="bg-card border border-accent/20 rounded-card p-5">
            <p className="text-txt text-base sm:text-lg leading-relaxed">
              {data.powerStatement}
            </p>
          </div>
        </motion.div>

        {/* ── 3. COMPOUND VISUALIZATION ──────────────────────────── */}
        <motion.div variants={fadeUp} className="mx-4 mt-4">
          <div className="bg-card border border-line rounded-card p-4">
            <span className="font-mono text-accent text-xs tracking-label">WHERE YOUR RAISE GOES</span>

            <div className="mt-3" style={{ height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={compoundData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="gradSaved" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#009E52" stopOpacity={0.5} />
                      <stop offset="100%" stopColor="#009E52" stopOpacity={0.05} />
                    </linearGradient>
                    <linearGradient id="gradInvested" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#00E87B" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#00E87B" stopOpacity={0.05} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 6" />
                  <XAxis
                    dataKey="year"
                    tick={{ fontSize: 10, fill: '#5E736A', fontFamily: 'IBM Plex Mono' }}
                    tickLine={false}
                    axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                    label={{ value: 'Years', position: 'insideBottomRight', offset: -5, fontSize: 9, fill: '#5E736A' }}
                  />
                  <YAxis
                    tick={{ fontSize: 10, fill: '#5E736A', fontFamily: 'IBM Plex Mono' }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(v: number) => fmtShort(v)}
                    width={55}
                  />
                  <Tooltip content={<CompoundTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="saved"
                    stackId="1"
                    stroke="#009E52"
                    strokeWidth={1.5}
                    fill="url(#gradSaved)"
                    name="Raw Savings"
                  />
                  <Area
                    type="monotone"
                    dataKey="invested"
                    stackId="0"
                    stroke="#00E87B"
                    strokeWidth={2}
                    fill="url(#gradInvested)"
                    name="Invested Growth"
                  />
                  {/* Callout dots */}
                  <ReferenceDot x="5" y={raise.compoundProjection.year5} r={4} fill="#00E87B" stroke="none" />
                  <ReferenceDot x="10" y={raise.compoundProjection.year10} r={4} fill="#00E87B" stroke="none" />
                  <ReferenceDot x="30" y={raise.compoundProjection.year30} r={5} fill="#00E87B" stroke="none" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Callout labels below chart */}
            <div className="flex justify-between mt-3 text-[10px] font-mono">
              <div className="text-center">
                <span className="text-muted block">Year 5</span>
                <span className="text-accent">{fmtShort(raise.compoundProjection.year5)}</span>
              </div>
              <div className="text-center">
                <span className="text-muted block">Year 10</span>
                <span className="text-accent">{fmtShort(raise.compoundProjection.year10)}</span>
                <span className="text-txt-off block text-[9px]">that&apos;s a car</span>
              </div>
              <div className="text-center">
                <span className="text-muted block">Year 30</span>
                <span className="text-accent font-bold">{fmtShort(raise.compoundProjection.year30)}</span>
                <span className="text-txt-off block text-[9px]">retirement money</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* ── 4. EQUIVALENT TO ───────────────────────────────────── */}
        {raise.equivalentTo.length > 0 && (
          <motion.div variants={fadeUp} className="mx-4 mt-4">
            <span className="font-mono text-accent text-xs tracking-label">YOUR RAISE IS EQUIVALENT TO</span>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
              {raise.equivalentTo.map((eq, i) => (
                <motion.div
                  key={i}
                  variants={fadeUp}
                  className="bg-s1 border border-line rounded-card p-4 text-center hover:border-line-hover transition-colors"
                >
                  <span className="text-3xl block">{eq.icon}</span>
                  <p className="text-txt-off text-xs mt-2 leading-snug">{eq.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── 5. RECENT RIPPLES ──────────────────────────────────── */}
        {data.recentRipples.length > 0 && (
          <motion.div
            variants={stagger}
            initial="hidden"
            animate="show"
            className="mx-4 mt-4"
          >
            <span className="font-mono text-accent text-xs tracking-label">RECENT RIPPLE EFFECTS</span>
            <div className="mt-3 space-y-3">
              {data.recentRipples.map(ripple => (
                <RippleCard key={ripple.id} ripple={ripple} />
              ))}
            </div>
          </motion.div>
        )}

        {/* ── 6. MILESTONES ──────────────────────────────────────── */}
        {milestones.length > 0 && (
          <motion.div variants={fadeUp} className="mx-4 mt-4">
            <span className="font-mono text-accent text-xs tracking-label">RAISE MILESTONES</span>
            <div className="mt-3 bg-s1 border border-line rounded-card p-4">
              {/* Progress bar */}
              <div className="relative h-2 bg-line rounded-full overflow-visible">
                <motion.div
                  className="h-full bg-accent rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min((currentRaise / maxMilestone) * 100, 100)}%` }}
                  transition={{ duration: 1.2, delay: 0.3, ease: 'easeOut' }}
                />

                {/* Milestone markers */}
                {milestones.map((m, i) => {
                  const pos = (m.threshold / maxMilestone) * 100;
                  return (
                    <div
                      key={i}
                      className="absolute top-1/2 -translate-y-1/2"
                      style={{ left: `${pos}%` }}
                    >
                      {m.reached ? (
                        <div
                          className="w-4 h-4 -ml-2 rounded-full bg-accent border-2 border-s1 flex items-center justify-center"
                          title={`${m.name} — reached ${m.reachedDate ?? ''}`}
                        >
                          <span className="text-[7px]">{m.icon}</span>
                        </div>
                      ) : (
                        <div
                          className="w-4 h-4 -ml-2 rounded-full bg-s2 border-2 border-line flex items-center justify-center"
                          title={m.name}
                        >
                          <span className="text-[7px] text-muted">🔒</span>
                        </div>
                      )}
                    </div>
                  );
                })}

                {/* Current position pulsing dot */}
                <motion.div
                  className="absolute top-1/2 -translate-y-1/2 w-3 h-3 -ml-1.5 rounded-full bg-accent shadow-[0_0_8px_rgba(0,232,123,0.6)]"
                  style={{ left: `${Math.min((currentRaise / maxMilestone) * 100, 100)}%` }}
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                />
              </div>

              {/* Milestone labels */}
              <div className="flex justify-between mt-3">
                {milestones.map((m, i) => (
                  <div key={i} className="text-center" style={{ width: `${100 / milestones.length}%` }}>
                    <span className={`text-[9px] font-mono block ${m.reached ? 'text-accent' : 'text-muted'}`}>
                      {fmtShort(m.threshold)}
                    </span>
                    <span className={`text-[8px] block ${m.reached ? 'text-txt-off' : 'text-muted'}`}>
                      {m.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* ── 7. MONTHLY HISTORY (collapsible) ───────────────────── */}
        {historyData.length > 1 && (
          <div className="mx-4 mt-4 mb-4">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="w-full flex items-center justify-between bg-s1 border border-line rounded-lg px-4 py-3 cursor-pointer hover:border-line-hover transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm">📈</span>
                <span className="text-xs text-txt font-medium">Monthly Raise History</span>
                <span className="text-[10px] text-muted font-mono ml-1">{historyData.length} months</span>
              </div>
              <Chevron open={showHistory} />
            </button>

            <AnimatePresence>
              {showHistory && (
                <motion.div {...collapse} className="overflow-hidden">
                  <div className="mt-2 bg-s1 border border-line rounded-lg p-4">
                    <div style={{ height: 160 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={historyData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                          <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 6" />
                          <XAxis
                            dataKey="month"
                            tick={{ fontSize: 9, fill: '#5E736A', fontFamily: 'IBM Plex Mono' }}
                            tickLine={false}
                            axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                          />
                          <YAxis
                            tick={{ fontSize: 9, fill: '#5E736A', fontFamily: 'IBM Plex Mono' }}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(v: number) => fmtShort(v)}
                            width={50}
                          />
                          <Tooltip
                            content={({ active, payload, label }) => {
                              if (!active || !payload?.length) return null;
                              const raiseAmt = payload.find(p => p.dataKey === 'raiseAmount')?.value ?? 0;
                              const newOpts = payload.find(p => p.dataKey === 'newOptimizations')?.value ?? 0;
                              return (
                                <div className="bg-s1 border border-line rounded-lg px-3 py-2 text-xs shadow-lg">
                                  <p className="text-muted font-mono">{label as string}</p>
                                  <p className="text-accent">Raise: {fmtShort(raiseAmt as number)}/yr</p>
                                  {(newOpts as number) > 0 && (
                                    <p className="text-txt-off">+{newOpts as number} new optimization{(newOpts as number) > 1 ? 's' : ''}</p>
                                  )}
                                </div>
                              );
                            }}
                          />
                          <Line
                            type="monotone"
                            dataKey="raiseAmount"
                            stroke="#00E87B"
                            strokeWidth={2}
                            dot={(props: Record<string, unknown>) => {
                              const { cx, cy, payload: dotPayload } = props as { cx: number; cy: number; payload: { newOptimizations: number } };
                              const hasNew = dotPayload?.newOptimizations > 0;
                              return (
                                <circle
                                  key={`dot-${cx}-${cy}`}
                                  cx={cx}
                                  cy={cy}
                                  r={hasNew ? 4 : 2.5}
                                  fill={hasNew ? '#00E87B' : '#009E52'}
                                  stroke={hasNew ? '#00E87B' : 'none'}
                                  strokeWidth={hasNew ? 2 : 0}
                                  strokeOpacity={0.3}
                                />
                              );
                            }}
                            activeDot={{ r: 5, fill: '#00E87B', stroke: '#000', strokeWidth: 2 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <p className="text-[10px] text-muted mt-2 text-center">
                      Larger dots = months with new optimizations found
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Bottom padding if no history */}
        {historyData.length <= 1 && <div className="h-4" />}

      </motion.div>
    </ExportableCard>
  );
}
