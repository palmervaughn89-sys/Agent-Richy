'use client';

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart,
} from 'recharts';
import ExportableCard, { type ExportData } from './ExportableCard';
import type { TwinSimulation, LifeEvent } from '@/lib/financialTwin';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
  return `$${n.toLocaleString()}`;
}

function fmtFull(n: number): string {
  return `$${n.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

function sign(n: number): string {
  return n >= 0 ? `+${fmt(n)}` : fmt(n);
}

function signMonths(n: number): string {
  const abs = Math.abs(n);
  const yrs = Math.floor(abs / 12);
  const mos = abs % 12;
  const label = yrs > 0 ? (mos > 0 ? `${yrs}yr ${mos}mo` : `${yrs}yr`) : `${mos}mo`;
  return n < 0 ? `${label} earlier` : n > 0 ? `${label} later` : 'Same';
}

const CONFIDENCE_COLORS: Record<string, string> = {
  planning: 'bg-accent/20 text-accent',
  considering: 'bg-amber-400/20 text-amber-400',
  hypothetical: 'bg-blue-400/20 text-blue-400',
};

const CONFIDENCE_LABELS: Record<string, string> = {
  planning: 'Planning',
  considering: 'Considering',
  hypothetical: 'Hypothetical',
};

/* ── Chart tooltip ─────────────────────────────────────────────────── */

function TwinTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) {
  if (!active || !payload?.length) return null;
  const baseline = payload.find((p) => p.name === 'Baseline');
  const simulated = payload.find((p) => p.name === 'Simulated');
  const diff = (simulated?.value ?? 0) - (baseline?.value ?? 0);

  return (
    <div className="bg-card border border-line rounded-lg p-3 shadow-lg text-xs">
      <p className="font-mono text-muted mb-2">{label}</p>
      {baseline && (
        <p className="text-muted">Baseline: <span className="text-txt font-semibold">{fmtFull(baseline.value)}</span></p>
      )}
      {simulated && (
        <p className="text-accent">Simulated: <span className="text-txt font-semibold">{fmtFull(simulated.value)}</span></p>
      )}
      {baseline && simulated && (
        <p className={`mt-1 font-semibold ${diff >= 0 ? 'text-accent' : 'text-red-400'}`}>
          {diff >= 0 ? '▲' : '▼'} {fmtFull(Math.abs(diff))} {diff >= 0 ? 'ahead' : 'behind'}
        </p>
      )}
    </div>
  );
}

/* ── Event pill ────────────────────────────────────────────────────── */

function EventPill({ event }: { event: LifeEvent }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium ${CONFIDENCE_COLORS[event.userConfidence]}`}>
      {event.name}
      {event.probability != null && event.probability < 100 && (
        <span className="opacity-60">({event.probability}%)</span>
      )}
    </span>
  );
}

/* ── Expandable event card ─────────────────────────────────────────── */

function EventDetail({ event }: { event: LifeEvent }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="bg-card border border-line rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-s1 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase ${CONFIDENCE_COLORS[event.userConfidence]}`}>
            {CONFIDENCE_LABELS[event.userConfidence]}
          </span>
          <span className="text-sm font-semibold text-txt">{event.name}</span>
        </div>
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="text-muted text-xs"
        >
          ▼
        </motion.span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-3 border-t border-line pt-3">
              {event.description && (
                <p className="text-xs text-off leading-relaxed">{event.description}</p>
              )}

              {/* Financial impact */}
              <div className="grid grid-cols-2 gap-2">
                {event.oneTimeCost != null && event.oneTimeCost > 0 && (
                  <div className="bg-red-500/10 rounded-lg p-2 text-center">
                    <p className="text-[10px] text-muted uppercase">One-time Cost</p>
                    <p className="text-sm font-bold text-red-400">{fmtFull(event.oneTimeCost)}</p>
                  </div>
                )}
                {event.oneTimeIncome != null && event.oneTimeIncome > 0 && (
                  <div className="bg-accent/10 rounded-lg p-2 text-center">
                    <p className="text-[10px] text-muted uppercase">One-time Income</p>
                    <p className="text-sm font-bold text-accent">{fmtFull(event.oneTimeIncome)}</p>
                  </div>
                )}
                {event.monthlyExpenseChange != null && event.monthlyExpenseChange !== 0 && (
                  <div className={`${event.monthlyExpenseChange > 0 ? 'bg-red-500/10' : 'bg-accent/10'} rounded-lg p-2 text-center`}>
                    <p className="text-[10px] text-muted uppercase">Monthly Expenses</p>
                    <p className={`text-sm font-bold ${event.monthlyExpenseChange > 0 ? 'text-red-400' : 'text-accent'}`}>
                      {event.monthlyExpenseChange > 0 ? '+' : ''}{fmtFull(event.monthlyExpenseChange)}/mo
                    </p>
                  </div>
                )}
                {event.monthlyIncomeChange != null && event.monthlyIncomeChange !== 0 && (
                  <div className={`${event.monthlyIncomeChange > 0 ? 'bg-accent/10' : 'bg-red-500/10'} rounded-lg p-2 text-center`}>
                    <p className="text-[10px] text-muted uppercase">Monthly Income</p>
                    <p className={`text-sm font-bold ${event.monthlyIncomeChange > 0 ? 'text-accent' : 'text-red-400'}`}>
                      {event.monthlyIncomeChange > 0 ? '+' : ''}{fmtFull(event.monthlyIncomeChange)}/mo
                    </p>
                  </div>
                )}
              </div>

              {/* Cascading effects */}
              {(event.affectsInsurance || event.affectsTaxBracket || event.affectsHousing || event.affectsTransportation) && (
                <div>
                  <p className="text-[10px] text-muted uppercase mb-1">Cascading Effects</p>
                  <div className="flex flex-wrap gap-1">
                    {event.affectsInsurance && <span className="px-2 py-0.5 bg-s2 rounded text-[10px] text-off">Insurance</span>}
                    {event.affectsTaxBracket && <span className="px-2 py-0.5 bg-s2 rounded text-[10px] text-off">Tax Bracket</span>}
                    {event.affectsHousing && <span className="px-2 py-0.5 bg-s2 rounded text-[10px] text-off">Housing</span>}
                    {event.affectsTransportation && <span className="px-2 py-0.5 bg-s2 rounded text-[10px] text-off">Transportation</span>}
                  </div>
                </div>
              )}

              {/* Timing */}
              <div className="text-[11px] text-muted">
                Starts {event.startDate}
                {event.endDate && ` · Ends ${event.endDate}`}
                {event.duration && ` · ${event.duration} months`}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ── Risk card ─────────────────────────────────────────────────────── */

function RiskCard({ risk }: { risk: TwinSimulation['risks'][number] }) {
  const barColor = risk.probability > 60 ? 'bg-red-400' : risk.probability > 30 ? 'bg-amber-400' : 'bg-accent';

  return (
    <div className="bg-card border border-line rounded-lg p-4">
      <div className="flex items-start justify-between mb-2">
        <p className="text-sm font-semibold text-txt flex-1">{risk.description}</p>
        <span className="text-xs text-muted ml-2 whitespace-nowrap">{fmtFull(risk.financialImpact)}</span>
      </div>
      <div className="flex items-center gap-3 mb-2">
        <div className="flex-1 h-1.5 bg-s2 rounded-full overflow-hidden">
          <div className={`h-full rounded-full ${barColor}`} style={{ width: `${risk.probability}%` }} />
        </div>
        <span className="text-[11px] text-muted font-mono">{risk.probability}%</span>
      </div>
      <p className="text-xs text-off leading-relaxed">
        <span className="text-muted font-medium">Mitigation:</span> {risk.mitigation}
      </p>
    </div>
  );
}

/* ── Comparison cell ───────────────────────────────────────────────── */

function CompCell({ label, baseline, simulated }: { label: string; baseline: number; simulated: number }) {
  const diff = simulated - baseline;
  const better = diff > 0;

  return (
    <div className="bg-card border border-line rounded-lg p-3">
      <p className="text-[10px] text-muted uppercase tracking-wide mb-1">{label}</p>
      <div className="flex items-baseline justify-between">
        <span className="text-xs text-off line-through opacity-60">{fmt(baseline)}</span>
        <span className="text-sm font-bold text-txt">{fmt(simulated)}</span>
      </div>
      <p className={`text-[11px] font-semibold mt-1 ${better ? 'text-accent' : 'text-red-400'}`}>
        {better ? '▲' : '▼'} {sign(diff)}
      </p>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════
   FINANCIAL TWIN CARD
   ══════════════════════════════════════════════════════════════════════ */

interface FinancialTwinCardProps {
  simulation: TwinSimulation;
}

export default function FinancialTwinCard({ simulation }: FinancialTwinCardProps) {
  const [showEvents, setShowEvents] = useState(false);
  const { vsBaseline, risks, timeline, events } = simulation;

  /* ── Build chart data from timeline ──────────────────────────────── */
  const chartData = useMemo(() => {
    if (!timeline.length) return [];

    // We need baseline data alongside simulated.
    // Baseline = starting netWorth grown at a simple rate (no events).
    const baseStart = simulation.baselineSnapshot.netWorth;
    const baseSurplus = simulation.baselineSnapshot.monthlyIncome - simulation.baselineSnapshot.monthlyExpenses;

    return timeline.map((t) => {
      // Months from start
      const startDate = new Date(timeline[0].date);
      const thisDate = new Date(t.date);
      const monthsElapsed = (thisDate.getFullYear() - startDate.getFullYear()) * 12 + (thisDate.getMonth() - startDate.getMonth());

      // Simple baseline projection: net worth + surplus * months + 7% annual investment growth
      const baselineNW = baseStart + baseSurplus * monthsElapsed +
        (baseSurplus * 0.7 * monthsElapsed * (0.07 / 12) * monthsElapsed / 2);

      return {
        date: t.date.slice(0, 7), // YYYY-MM
        label: `${t.date.slice(0, 4)}`,
        Baseline: Math.round(baselineNW),
        Simulated: Math.round(t.netWorth),
        events: t.eventsThisYear,
      };
    });
  }, [timeline, simulation.baselineSnapshot]);

  // Deduplicate chart data to yearly points for cleaner chart
  const yearlyData = useMemo(() => {
    const seen = new Set<string>();
    return chartData.filter((d) => {
      const yr = d.date.slice(0, 4);
      if (seen.has(yr)) return false;
      seen.add(yr);
      return true;
    });
  }, [chartData]);

  // Event markers — years that have events
  const eventYears = useMemo(() => {
    const map = new Map<string, string[]>();
    for (const d of chartData) {
      if (d.events.length > 0) {
        const yr = d.date.slice(0, 4);
        if (!map.has(yr)) map.set(yr, []);
        map.get(yr)!.push(...d.events);
      }
    }
    return map;
  }, [chartData]);

  /* ── Comparison metrics at 5yr, 10yr, 20yr ──────────────────────── */
  const comparisonPoints = useMemo(() => {
    const findYear = (yr: number) => {
      const match = timeline.find((t) => t.year === yr);
      if (!match) return null;
      const startNW = simulation.baselineSnapshot.netWorth;
      const surplus = simulation.baselineSnapshot.monthlyIncome - simulation.baselineSnapshot.monthlyExpenses;
      const months = yr * 12;
      const baselineNW = startNW + surplus * months + (surplus * 0.7 * months * (0.07 / 12) * months / 2);
      return { baseline: Math.round(baselineNW), simulated: Math.round(match.netWorth), surplus: match.monthlySurplus, debt: match.totalDebt, investments: match.totalInvestments };
    };

    return {
      yr5: findYear(5),
      yr10: findYear(10),
      yr20: findYear(20),
    };
  }, [timeline, simulation.baselineSnapshot]);

  /* ── Export data ─────────────────────────────────────────────────── */
  const exportData: ExportData = useMemo(() => {
    const lines = [
      `FINANCIAL TWIN SIMULATION: ${simulation.name}`,
      `Generated: ${new Date(simulation.createdAt).toLocaleDateString()}`,
      '',
      'EVENTS:',
      ...events.map((e) => `  • ${e.name} (${e.userConfidence})`),
      '',
      'VERDICT:',
      vsBaseline.verdict,
      '',
      'NET WORTH COMPARISON:',
      `  5-year:  ${sign(vsBaseline.netWorthDifference5yr)}`,
      `  10-year: ${sign(vsBaseline.netWorthDifference10yr)}`,
      `  20-year: ${sign(vsBaseline.netWorthDifference20yr)}`,
      `  Retirement: ${signMonths(vsBaseline.retirementAgeDifference)}`,
      '',
      'RISKS:',
      ...risks.map((r) => `  • ${r.description} (${r.probability}% chance, ${fmtFull(r.financialImpact)} impact)`),
      '',
      "RICHY'S TAKE:",
      simulation.summary,
      '',
      'RECOMMENDATION:',
      simulation.recommendation,
    ];

    return {
      clipboard: lines.join('\n'),
      formatted: lines.join('\n'),
    };
  }, [simulation, events, vsBaseline, risks]);

  /* ── Verdict color ──────────────────────────────────────────────── */
  const verdictPositive = vsBaseline.netWorthDifference10yr >= 0;

  return (
    <ExportableCard title="Financial Twin Simulation" exportData={exportData}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      >
        {/* ── 1. SIMULATION HEADER ──────────────────────────────────── */}
        <div className="bg-s1 rounded-t-card p-6">
          <p className="font-mono text-accent text-xs tracking-widest uppercase mb-2">Financial Twin</p>
          <h3 className="text-2xl font-bold text-txt tracking-tight">{simulation.name}</h3>
          {events.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {events.map((e) => (
                <EventPill key={e.id} event={e} />
              ))}
            </div>
          )}
        </div>

        {/* ── 2. TIMELINE CHART ─────────────────────────────────────── */}
        {yearlyData.length > 0 && (
          <div className="mt-4 bg-card border border-line rounded-card p-4">
            <p className="text-xs text-muted font-mono uppercase tracking-wide mb-3">Net Worth: Baseline vs Simulated</p>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={yearlyData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    dataKey="label"
                    tick={{ fill: '#6B7280', fontSize: 11, fontFamily: 'IBM Plex Mono' }}
                    axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                    tickLine={false}
                  />
                  <YAxis
                    tickFormatter={(v: number) => fmt(v)}
                    tick={{ fill: '#6B7280', fontSize: 11, fontFamily: 'IBM Plex Mono' }}
                    axisLine={false}
                    tickLine={false}
                    width={60}
                  />
                  <Tooltip content={<TwinTooltip />} />

                  {/* Fill between lines */}
                  <Area
                    type="monotone"
                    dataKey="Simulated"
                    fill="rgba(0,232,123,0.08)"
                    stroke="none"
                    isAnimationActive={false}
                  />

                  {/* Event markers */}
                  {Array.from(eventYears.entries()).map(([yr, evts]) => (
                    <ReferenceLine
                      key={yr}
                      x={yr}
                      stroke="rgba(0,232,123,0.3)"
                      strokeDasharray="4 4"
                      label={{
                        value: evts[0]?.slice(0, 15) ?? '',
                        position: 'top',
                        fill: '#00E87B',
                        fontSize: 9,
                        fontFamily: 'IBM Plex Mono',
                      }}
                    />
                  ))}

                  {/* Baseline line */}
                  <Line
                    type="monotone"
                    dataKey="Baseline"
                    stroke="#6B7280"
                    strokeWidth={2}
                    strokeDasharray="6 4"
                    dot={false}
                    name="Baseline"
                  />

                  {/* Simulated line */}
                  <Line
                    type="monotone"
                    dataKey="Simulated"
                    stroke="#00E87B"
                    strokeWidth={2.5}
                    dot={{ fill: '#00E87B', r: 3 }}
                    activeDot={{ r: 5, fill: '#00E87B' }}
                    name="Simulated"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center gap-6 mt-3 text-[11px] text-muted">
              <span className="flex items-center gap-2">
                <span className="w-5 h-0.5 bg-[#6B7280] inline-block" style={{ borderTop: '2px dashed #6B7280' }} />
                Baseline (no changes)
              </span>
              <span className="flex items-center gap-2">
                <span className="w-5 h-0.5 bg-accent inline-block" />
                Simulated
              </span>
            </div>
          </div>
        )}

        {/* ── 3. VERDICT ────────────────────────────────────────────── */}
        <div className={`mt-4 rounded-card p-5 text-center border ${
          verdictPositive
            ? 'bg-accent/10 border-accent/20'
            : 'bg-red-500/10 border-red-500/20'
        }`}>
          <p className="text-xl font-bold text-txt leading-snug">{vsBaseline.verdict}</p>
          <p className="text-sm text-off mt-2">
            Retirement impact: <span className="font-semibold text-txt">{signMonths(vsBaseline.retirementAgeDifference)}</span>
            {' · '}
            Lifetime earnings: <span className="font-semibold text-txt">{sign(vsBaseline.totalLifetimeEarningsDifference)}</span>
          </p>
        </div>

        {/* ── 4. COMPARISON TABLE ───────────────────────────────────── */}
        <div className="mt-4">
          <p className="text-xs text-muted font-mono uppercase tracking-wide mb-3">Baseline vs Simulated</p>
          <div className="grid grid-cols-3 gap-2 mb-2">
            <div className="text-center text-[10px] text-muted font-mono">5 YEAR</div>
            <div className="text-center text-[10px] text-muted font-mono">10 YEAR</div>
            <div className="text-center text-[10px] text-muted font-mono">20 YEAR</div>
          </div>

          {/* Net Worth row */}
          <div className="grid grid-cols-3 gap-2 mb-2">
            {comparisonPoints.yr5 && (
              <CompCell label="Net Worth" baseline={comparisonPoints.yr5.baseline} simulated={comparisonPoints.yr5.simulated} />
            )}
            {comparisonPoints.yr10 && (
              <CompCell label="Net Worth" baseline={comparisonPoints.yr10.baseline} simulated={comparisonPoints.yr10.simulated} />
            )}
            {comparisonPoints.yr20 && (
              <CompCell label="Net Worth" baseline={comparisonPoints.yr20.baseline} simulated={comparisonPoints.yr20.simulated} />
            )}
          </div>

          {/* Surplus / Debt / Investments rows */}
          <div className="grid grid-cols-3 gap-2 mb-2">
            {comparisonPoints.yr5 && <CompCell label="Monthly Surplus" baseline={simulation.baselineSnapshot.monthlyIncome - simulation.baselineSnapshot.monthlyExpenses} simulated={comparisonPoints.yr5.surplus} />}
            {comparisonPoints.yr10 && <CompCell label="Monthly Surplus" baseline={simulation.baselineSnapshot.monthlyIncome - simulation.baselineSnapshot.monthlyExpenses} simulated={comparisonPoints.yr10.surplus} />}
            {comparisonPoints.yr20 && <CompCell label="Monthly Surplus" baseline={simulation.baselineSnapshot.monthlyIncome - simulation.baselineSnapshot.monthlyExpenses} simulated={comparisonPoints.yr20.surplus} />}
          </div>

          <div className="grid grid-cols-3 gap-2">
            {comparisonPoints.yr5 && <CompCell label="Debt Remaining" baseline={simulation.baselineSnapshot.totalDebt} simulated={comparisonPoints.yr5.debt} />}
            {comparisonPoints.yr10 && <CompCell label="Debt Remaining" baseline={simulation.baselineSnapshot.totalDebt} simulated={comparisonPoints.yr10.debt} />}
            {comparisonPoints.yr20 && <CompCell label="Debt Remaining" baseline={simulation.baselineSnapshot.totalDebt} simulated={comparisonPoints.yr20.debt} />}
          </div>
        </div>

        {/* ── 5. EVENTS DETAIL (collapsible) ────────────────────────── */}
        {events.length > 0 && (
          <div className="mt-4">
            <button
              onClick={() => setShowEvents(!showEvents)}
              className="flex items-center gap-2 text-xs text-muted hover:text-txt transition-colors font-mono uppercase tracking-wide"
            >
              <motion.span animate={{ rotate: showEvents ? 180 : 0 }} transition={{ duration: 0.2 }}>▼</motion.span>
              {events.length} Life Event{events.length > 1 ? 's' : ''} — Detailed Breakdown
            </button>
            <AnimatePresence>
              {showEvents && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden"
                >
                  <div className="space-y-2 mt-3">
                    {events.map((e) => (
                      <EventDetail key={e.id} event={e} />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* ── 6. RISKS ──────────────────────────────────────────────── */}
        {risks.length > 0 && (
          <div className="mt-4">
            <p className="text-xs text-muted font-mono uppercase tracking-wide mb-3">
              Risk Analysis ({risks.length})
            </p>
            <div className="space-y-2">
              {risks.map((r, i) => (
                <RiskCard key={i} risk={r} />
              ))}
            </div>
          </div>
        )}

        {/* ── 7. RICHY'S TAKE ───────────────────────────────────────── */}
        <div className="mt-4 bg-s1 rounded-card p-4">
          <p className="text-xs text-accent font-mono uppercase tracking-wide mb-3">Richy&apos;s Take</p>
          <div className="border-l-2 border-accent/30 pl-4">
            {simulation.summary && (
              <p className="text-sm text-off leading-relaxed">{simulation.summary}</p>
            )}
            {simulation.recommendation && (
              <p className="text-sm text-off leading-relaxed mt-3">
                <span className="font-semibold text-txt">Recommendation:</span> {simulation.recommendation}
              </p>
            )}
            {simulation.keyInsight && (
              <p className="text-sm font-semibold text-accent mt-3 leading-relaxed">
                💡 {simulation.keyInsight}
              </p>
            )}
          </div>
        </div>
      </motion.div>
    </ExportableCard>
  );
}
