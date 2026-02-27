'use client';

import { useState, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sankey, Tooltip, ResponsiveContainer } from 'recharts';
import ExportableCard from './ExportableCard';
import type { MoneyMapData, MoneyFlow } from '@/types/moneyMap';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function fmtShort(n: number): string {
  if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
  return fmt(n);
}

function pct(n: number): string {
  const sign = n > 0 ? '+' : '';
  return `${sign}${Math.round(n)}%`;
}

function clamp(v: number, min: number, max: number) {
  return Math.max(min, Math.min(max, v));
}

/* ── Animation ─────────────────────────────────────────────────────── */

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.05 } },
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

/* ── Colors ────────────────────────────────────────────────────────── */

const HEALTH_COLORS: Record<string, string> = {
  healthy:  '#00E87B',
  caution:  '#F59E0B',
  warning:  '#F97316',
  critical: '#EF4444',
};

const CATEGORY_ICONS: Record<string, string> = {
  income_salary: '💼', income_freelance: '💻', income_side: '⚡', income_investment: '📈', income_other: '💵',
  housing: '🏠', utilities: '⚡', transportation: '🚗', food_groceries: '🛒', food_dining: '🍽️',
  insurance: '🛡️', healthcare: '🏥', debt_payments: '💳', subscriptions: '📱', personal_care: '✨',
  clothing: '👔', entertainment: '🎬', kids: '🧒', pets: '🐾', gifts: '🎁',
  savings_emergency: '🏦', savings_goals: '🎯', investing_retirement: '🏖️', investing_brokerage: '📊',
  taxes: '🏛️', fees: '📄', miscellaneous: '📦',
};

function healthColor(status: string): string {
  return HEALTH_COLORS[status] ?? '#5E736A';
}

function scoreColor(score: number): string {
  if (score >= 80) return '#00E87B';
  if (score >= 60) return '#3B82F6';
  if (score >= 40) return '#F59E0B';
  return '#EF4444';
}

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

/* ── Health Score Gauge ────────────────────────────────────────────── */

function HealthGauge({ score }: { score: number }) {
  const color = scoreColor(score);
  const circumference = 2 * Math.PI * 18;
  const filled = (clamp(score, 0, 100) / 100) * circumference;

  return (
    <div className="relative w-12 h-12 flex-shrink-0">
      <svg viewBox="0 0 44 44" className="w-full h-full -rotate-90">
        <circle cx="22" cy="22" r="18" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="3.5" />
        <motion.circle
          cx="22" cy="22" r="18" fill="none"
          stroke={color}
          strokeWidth="3.5"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference - filled }}
          transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
        />
      </svg>
      <span
        className="absolute inset-0 flex items-center justify-center text-[11px] font-bold font-mono"
        style={{ color }}
      >
        {score}
      </span>
    </div>
  );
}

/* ── Sankey custom node ────────────────────────────────────────────── */

function SankeyNode(props: Record<string, unknown>) {
  const { x, y, width, height, payload } = props as {
    x: number; y: number; width: number; height: number;
    payload: { name: string; color?: string; value: number };
  };
  if (!payload) return null;
  const color = payload.color || '#00E87B';
  const isLeft = (x as number) < 100;

  return (
    <g>
      <defs>
        <linearGradient id={`node-${payload.name.replace(/\s/g, '')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.9} />
          <stop offset="100%" stopColor={color} stopOpacity={0.5} />
        </linearGradient>
      </defs>
      <rect
        x={x} y={y} width={width} height={height}
        rx={3}
        fill={`url(#node-${payload.name.replace(/\s/g, '')})`}
        stroke={color}
        strokeWidth={0.5}
        strokeOpacity={0.3}
      />
      <text
        x={isLeft ? x - 6 : x + width + 6}
        y={y + height / 2}
        textAnchor={isLeft ? 'end' : 'start'}
        dominantBaseline="middle"
        className="text-[10px] font-medium"
        fill="#B8C9C0"
      >
        {payload.name}
      </text>
      <text
        x={isLeft ? x - 6 : x + width + 6}
        y={y + height / 2 + 13}
        textAnchor={isLeft ? 'end' : 'start'}
        dominantBaseline="middle"
        className="text-[9px] font-mono"
        fill="#5E736A"
      >
        {fmtShort(payload.value)}
      </text>
    </g>
  );
}

/* ── Sankey custom link ────────────────────────────────────────────── */

function SankeyLink(props: Record<string, unknown>) {
  const { sourceX, sourceY, sourceControlX, targetX, targetY, targetControlX,
          linkWidth, payload } = props as {
    sourceX: number; sourceY: number; sourceControlX: number;
    targetX: number; targetY: number; targetControlX: number;
    linkWidth: number; payload: { color?: string; source?: { name: string }; target?: { name: string } };
  };
  if (!sourceX) return null;

  const color = payload?.color || '#00E87B';
  const id = `link-${Math.random().toString(36).slice(2, 8)}`;

  return (
    <g>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor={color} stopOpacity={0.35} />
          <stop offset="50%" stopColor={color} stopOpacity={0.2} />
          <stop offset="100%" stopColor={color} stopOpacity={0.35} />
        </linearGradient>
      </defs>
      <path
        d={`M${sourceX},${sourceY}
            C${sourceControlX},${sourceY} ${targetControlX},${targetY} ${targetX},${targetY}`}
        fill="none"
        stroke={`url(#${id})`}
        strokeWidth={Math.max(linkWidth, 1)}
        strokeOpacity={0.8}
        className="transition-opacity duration-200 hover:!stroke-opacity-100"
      />
    </g>
  );
}

/* ── Mobile flow bar (simplified for small screens) ────────────────── */

function FlowBar({ flow, maxAmount }: { flow: MoneyFlow; maxAmount: number }) {
  const widthPct = Math.max((flow.monthlyAmount / maxAmount) * 100, 4);

  return (
    <motion.div variants={fadeUp} className="flex items-center gap-3 py-1.5">
      <span className="text-sm w-5 text-center flex-shrink-0">
        {CATEGORY_ICONS[flow.category] || '•'}
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-txt truncate">{flow.name}</span>
          <span className="text-xs font-mono text-txt font-medium ml-2 flex-shrink-0">
            {fmt(flow.monthlyAmount)}
          </span>
        </div>
        <div className="h-2 bg-line rounded-full overflow-hidden relative">
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: healthColor(flow.healthStatus) }}
            initial={{ width: 0 }}
            animate={{ width: `${widthPct}%` }}
            transition={{ duration: 0.6, ease: 'easeOut', delay: 0.1 }}
          />
          {flow.benchmark > 0 && (
            <div
              className="absolute top-0 h-full w-px bg-txt/40"
              style={{ left: `${Math.min((flow.benchmark / maxAmount) * 100, 100)}%` }}
            />
          )}
        </div>
      </div>
    </motion.div>
  );
}

/* ── Flow detail row ───────────────────────────────────────────────── */

function FlowDetailRow({ flow, maxAmount }: { flow: MoneyFlow; maxAmount: number }) {
  const [expanded, setExpanded] = useState(false);
  const barPct = Math.max((flow.monthlyAmount / maxAmount) * 100, 6);
  const benchPct = flow.benchmark > 0 ? (flow.benchmark / maxAmount) * 100 : 0;
  const overBench = flow.benchmark > 0 && flow.monthlyAmount > flow.benchmark;

  return (
    <motion.div variants={fadeUp} className="bg-card border border-line rounded-lg p-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left cursor-pointer"
      >
        <div className="flex items-center gap-3">
          {/* Icon + name */}
          <span className="text-base w-6 text-center flex-shrink-0">
            {CATEGORY_ICONS[flow.category] || '•'}
          </span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-sm text-txt font-medium truncate">{flow.name}</span>
              <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                <span className="text-sm font-mono text-txt font-bold">{fmt(flow.monthlyAmount)}</span>
                <span className="text-[10px] text-muted font-mono">
                  {Math.round(flow.percentOfIncome)}% of income
                </span>
                <Chevron open={expanded} />
              </div>
            </div>

            {/* Benchmark bar */}
            <div className="relative h-2.5 bg-line rounded-full overflow-visible">
              <motion.div
                className="h-full rounded-full relative"
                style={{ backgroundColor: healthColor(flow.healthStatus) }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(barPct, 100)}%` }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              />
              {benchPct > 0 && (
                <div
                  className="absolute top-[-2px] h-[calc(100%+4px)] w-0.5 bg-txt/50 rounded-full"
                  style={{ left: `${Math.min(benchPct, 100)}%` }}
                  title={`Benchmark: ${fmt(flow.benchmark)}`}
                />
              )}
            </div>

            {/* vs peers */}
            <div className="flex items-center gap-3 mt-1.5">
              <span
                className={`text-[10px] font-mono ${
                  flow.vsAverage > 10 ? 'text-red-400' :
                  flow.vsAverage > 0 ? 'text-amber-400' :
                  'text-accent'
                }`}
              >
                {pct(flow.vsAverage)} vs peers
              </span>
              <span className="text-[10px] text-muted">
                {flow.trend === 'increasing' ? '↑ Increasing' :
                 flow.trend === 'decreasing' ? '↓ Decreasing' : '→ Stable'}
              </span>
              {flow.optimizationAvailable && (
                <span className="text-[10px] text-accent font-medium flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
                  Save {fmt(flow.potentialSavings)}/mo
                </span>
              )}
            </div>
          </div>
        </div>
      </button>

      {/* Expanded: sub-flows + optimization */}
      <AnimatePresence>
        {expanded && (
          <motion.div {...collapse} className="overflow-hidden">
            <div className="mt-3 pt-3 border-t border-line space-y-2">
              {flow.subFlows && flow.subFlows.length > 0 && (
                <div className="space-y-1.5">
                  <span className="text-[10px] font-mono text-muted tracking-label">BREAKDOWN</span>
                  {flow.subFlows.map((sf, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <span className="text-txt-off">{sf.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-txt font-mono">{fmt(sf.amount)}</span>
                        <span className="text-muted font-mono text-[10px]">{Math.round(sf.percentage)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {flow.optimizationNote && (
                <div className="bg-accent/5 border border-accent/15 rounded-md p-2.5 text-xs text-txt-off">
                  💡 {flow.optimizationNote}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ── Build export data ─────────────────────────────────────────────── */

function buildExport(data: MoneyMapData) {
  const lines = [
    `💰 YOUR MONEY MAP — ${data.period}`,
    '',
    `Total Income:  ${fmt(data.totalInflow)}`,
    `Total Outflow: ${fmt(data.totalOutflow)}`,
    `Net Flow:      ${fmt(data.netFlow)}`,
    `Health Score:   ${data.healthScore}/100`,
    '',
    '── INFLOWS ──',
    ...data.inflows.map(f => `  ${f.name}: ${fmt(f.monthlyAmount)}`),
    '',
    '── OUTFLOWS ──',
    ...data.outflows.map(f => `  ${f.name}: ${fmt(f.monthlyAmount)} (${Math.round(f.percentOfIncome)}% of income) [${f.healthStatus}]`),
    '',
    '── TRANSFERS ──',
    ...data.transfers.map(f => `  ${f.name}: ${fmt(f.monthlyAmount)}`),
  ];

  if (data.leaks.length > 0) {
    lines.push('', '── MONEY LEAKS ──',
      `Total: ${fmt(data.totalLeakage)}/month`,
      ...data.leaks.map(l => `  💧 ${l.name}: ${fmt(l.amount)}/mo — ${l.description}`));
  }
  if (data.blockedFlows.length > 0) {
    lines.push('', '── MONEY LEFT ON THE TABLE ──',
      `Total: ${fmt(data.totalBlockedValue)}/year`,
      ...data.blockedFlows.map(b => `  🚫 ${b.name}: missing ${fmt(b.gap)}/mo — ${b.description}`));
  }

  const text = lines.join('\n');
  return { clipboard: text, formatted: text };
}

/* ══════════════════════════════════════════════════════════════════════
   MAIN COMPONENT
   ══════════════════════════════════════════════════════════════════════ */

export default function MoneyMapCard({ data }: { data: MoneyMapData }) {
  const [showHistory, setShowHistory] = useState(false);
  const [activeFlow, setActiveFlow] = useState<string | null>(null);
  const exportData = useMemo(() => buildExport(data), [data]);

  /* ── Build Sankey data ─────────────────────────────────────────── */
  const sankeyData = useMemo(() => {
    // Map node IDs to indices for Recharts Sankey (requires numeric source/target)
    const nodeMap = new Map<string, number>();
    const nodes = data.sankeyNodes.map((n, i) => {
      nodeMap.set(n.id, i);
      return { name: n.name, color: n.color, value: n.value };
    });
    const links = data.sankeyLinks
      .filter(l => nodeMap.has(l.source) && nodeMap.has(l.target))
      .map(l => ({
        source: nodeMap.get(l.source)!,
        target: nodeMap.get(l.target)!,
        value: Math.max(l.value, 1),
        color: l.color,
      }));
    return { nodes, links };
  }, [data.sankeyNodes, data.sankeyLinks]);

  const allOutflows = [...data.outflows, ...data.transfers].sort(
    (a, b) => b.monthlyAmount - a.monthlyAmount,
  );
  const maxOutflow = allOutflows[0]?.monthlyAmount || 1;
  const maxInflow = data.inflows[0]?.monthlyAmount || 1;
  const maxAmount = Math.max(maxOutflow, maxInflow);

  const hasSankey = sankeyData.nodes.length > 1 && sankeyData.links.length > 0;

  return (
    <ExportableCard title="Your Money Map" exportData={exportData}>
      <div className="bg-card border border-line rounded-t-card overflow-hidden">

        {/* ── 1. HEADER ──────────────────────────────────────────── */}
        <motion.div
          variants={stagger}
          initial="hidden"
          animate="show"
          className="bg-s1 p-6"
        >
          <motion.div variants={fadeUp} className="flex items-start justify-between">
            <div>
              <span className="font-mono text-accent text-xs tracking-label">YOUR MONEY MAP</span>
              <p className="text-txt text-lg font-semibold mt-1">{data.period}</p>
            </div>
            <HealthGauge score={data.healthScore} />
          </motion.div>

          {/* Stat pills */}
          <motion.div variants={fadeUp} className="flex flex-wrap gap-2 mt-4">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent/8 border border-accent/15 text-xs font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-accent" />
              <span className="text-accent">IN: {fmtShort(data.totalInflow)}</span>
            </span>
            <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono ${
              data.totalOutflow / data.totalInflow > 0.9
                ? 'bg-red-500/8 border border-red-500/15 text-red-400'
                : 'bg-amber-500/8 border border-amber-500/15 text-amber-400'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${
                data.totalOutflow / data.totalInflow > 0.9 ? 'bg-red-400' : 'bg-amber-400'
              }`} />
              OUT: {fmtShort(data.totalOutflow)}
            </span>
            <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono ${
              data.netFlow >= 0
                ? 'bg-accent/8 border border-accent/15 text-accent'
                : 'bg-red-500/8 border border-red-500/15 text-red-400'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${data.netFlow >= 0 ? 'bg-accent' : 'bg-red-400'}`} />
              NET: {data.netFlow >= 0 ? '+' : ''}{fmtShort(data.netFlow)}
            </span>
          </motion.div>
        </motion.div>

        {/* ── 2. SANKEY FLOW DIAGRAM ─────────────────────────────── */}
        {hasSankey && (
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="show"
            className="mt-1 bg-card border-t border-line p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="font-mono text-muted text-[10px] tracking-label">FLOW DIAGRAM</span>
              <span className="text-[10px] text-muted">Tap any flow for details</span>
            </div>

            {/* Desktop: Sankey */}
            <div className="hidden md:block">
              <div className="w-full overflow-x-auto" style={{ minHeight: 320 }}>
                <ResponsiveContainer width="100%" height={Math.max(320, sankeyData.nodes.length * 28)}>
                  <Sankey
                    data={sankeyData}
                    nodeWidth={10}
                    nodePadding={14}
                    linkCurvature={0.5}
                    iterations={64}
                    node={<SankeyNode />}
                    link={<SankeyLink />}
                    margin={{ top: 10, right: 120, bottom: 10, left: 120 }}
                  >
                    <Tooltip
                      content={({ payload }) => {
                        if (!payload || payload.length === 0) return null;
                        const item = payload[0]?.payload;
                        if (!item) return null;
                        return (
                          <div className="bg-s1 border border-line rounded-lg px-3 py-2 text-xs shadow-lg">
                            {item.source?.name && item.target?.name ? (
                              <>
                                <p className="text-txt font-medium">{item.source.name} → {item.target.name}</p>
                                <p className="text-muted font-mono mt-0.5">{fmtShort(item.value)}/mo</p>
                              </>
                            ) : (
                              <>
                                <p className="text-txt font-medium">{item.name}</p>
                                <p className="text-muted font-mono mt-0.5">{fmtShort(item.value)}/mo</p>
                              </>
                            )}
                          </div>
                        );
                      }}
                    />
                  </Sankey>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Mobile: Simplified flow list */}
            <motion.div
              variants={stagger}
              initial="hidden"
              animate="show"
              className="md:hidden space-y-1"
            >
              <span className="text-[10px] font-mono text-accent tracking-label">INCOME</span>
              {data.inflows.map(f => (
                <FlowBar key={f.id} flow={f} maxAmount={maxAmount} />
              ))}
              <div className="h-2" />
              <span className="text-[10px] font-mono text-amber-400 tracking-label">EXPENSES</span>
              {data.outflows.sort((a, b) => b.monthlyAmount - a.monthlyAmount).slice(0, 8).map(f => (
                <FlowBar key={f.id} flow={f} maxAmount={maxAmount} />
              ))}
              <div className="h-2" />
              <span className="text-[10px] font-mono text-accent tracking-label">SAVINGS & INVESTING</span>
              {data.transfers.map(f => (
                <FlowBar key={f.id} flow={f} maxAmount={maxAmount} />
              ))}
            </motion.div>
          </motion.div>
        )}

        {/* ── 3. FLOW BREAKDOWN ──────────────────────────────────── */}
        <motion.div
          variants={stagger}
          initial="hidden"
          animate="show"
          className="p-4 space-y-2"
        >
          <motion.div variants={fadeUp} className="flex items-center justify-between mb-1">
            <span className="font-mono text-muted text-[10px] tracking-label">ALL FLOWS — LARGEST FIRST</span>
            <span className="text-[10px] text-muted">{allOutflows.length} categories</span>
          </motion.div>

          {allOutflows.map(flow => (
            <FlowDetailRow key={flow.id} flow={flow} maxAmount={maxAmount} />
          ))}
        </motion.div>

        {/* ── 4. LEAKS SECTION ───────────────────────────────────── */}
        {data.leaks.length > 0 && (
          <motion.div
            variants={stagger}
            initial="hidden"
            animate="show"
            className="p-4 pt-0"
          >
            <motion.div variants={fadeUp}>
              <span className="font-mono text-red-400 text-xs tracking-label">💧 MONEY LEAKS</span>
              <p className="text-xs text-txt-off mt-1 mb-3">
                You have <span className="text-red-400 font-semibold">{fmt(data.totalLeakage)}/month</span> flowing to things giving you zero value
              </p>
            </motion.div>

            <div className="space-y-2">
              {data.leaks.map((leak, i) => (
                <motion.div
                  key={i}
                  variants={fadeUp}
                  className="bg-red-500/5 border border-red-500/20 rounded-lg p-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-txt font-medium">{leak.name}</span>
                        <span className="text-xs font-mono text-red-400">{fmt(leak.amount)}/mo</span>
                      </div>
                      <p className="text-xs text-txt-off mt-0.5">{leak.description}</p>
                      <p className="text-[10px] text-muted mt-1">
                        Annual impact: <span className="text-red-400 font-mono">{fmt(leak.annualImpact)}</span>
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                      <span className={`text-[9px] font-mono px-2 py-0.5 rounded-full ${
                        leak.fixDifficulty === 'easy'
                          ? 'bg-accent/10 text-accent'
                          : leak.fixDifficulty === 'medium'
                          ? 'bg-amber-500/10 text-amber-400'
                          : 'bg-red-500/10 text-red-400'
                      }`}>
                        {leak.fixDifficulty.toUpperCase()} FIX
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── 5. BLOCKED FLOWS ───────────────────────────────────── */}
        {data.blockedFlows.length > 0 && (
          <motion.div
            variants={stagger}
            initial="hidden"
            animate="show"
            className="p-4 pt-0"
          >
            <motion.div variants={fadeUp}>
              <span className="font-mono text-amber-400 text-xs tracking-label">🚫 MONEY LEFT ON THE TABLE</span>
              <p className="text-xs text-txt-off mt-1 mb-3">
                You&apos;re missing <span className="text-amber-400 font-semibold">{fmt(data.totalBlockedValue)}/year</span> in potential value
              </p>
            </motion.div>

            <div className="space-y-2">
              {data.blockedFlows.map((bf, i) => (
                <motion.div
                  key={i}
                  variants={fadeUp}
                  className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-3"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm text-txt font-medium">{bf.name}</span>
                      <span className="text-xs font-mono text-amber-400">
                        {fmt(bf.gap)}/mo gap
                      </span>
                    </div>
                    <p className="text-xs text-txt-off mt-0.5">{bf.description}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <div className="text-[10px]">
                        <span className="text-muted">Currently: </span>
                        <span className="text-txt font-mono">{fmt(bf.currentlyIs)}</span>
                      </div>
                      <span className="text-muted text-[10px]">→</span>
                      <div className="text-[10px]">
                        <span className="text-muted">Should be: </span>
                        <span className="text-accent font-mono">{fmt(bf.shouldBe)}</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── 6. VS LAST MONTH (collapsible) ─────────────────────── */}
        {data.vsLastMonth && (
          <div className="p-4 pt-0">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="w-full flex items-center justify-between bg-s1 border border-line rounded-lg px-4 py-3 cursor-pointer hover:border-line-hover transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm">📅</span>
                <span className="text-xs text-txt font-medium">vs Last Month</span>
                <div className="flex items-center gap-2 ml-2">
                  <span className={`text-[10px] font-mono ${data.vsLastMonth.netFlowChange >= 0 ? 'text-accent' : 'text-red-400'}`}>
                    Net {data.vsLastMonth.netFlowChange >= 0 ? '+' : ''}{fmt(data.vsLastMonth.netFlowChange)}
                  </span>
                </div>
              </div>
              <Chevron open={showHistory} />
            </button>

            <AnimatePresence>
              {showHistory && (
                <motion.div {...collapse} className="overflow-hidden">
                  <div className="mt-2 bg-s1 border border-line rounded-lg p-4 space-y-3">
                    <div className="grid grid-cols-3 gap-3">
                      <div className="text-center">
                        <span className="text-[10px] text-muted font-mono block">INCOME</span>
                        <span className={`text-sm font-mono font-bold ${data.vsLastMonth.inflowChange >= 0 ? 'text-accent' : 'text-red-400'}`}>
                          {data.vsLastMonth.inflowChange >= 0 ? '+' : ''}{fmtShort(data.vsLastMonth.inflowChange)}
                        </span>
                      </div>
                      <div className="text-center">
                        <span className="text-[10px] text-muted font-mono block">SPENDING</span>
                        <span className={`text-sm font-mono font-bold ${data.vsLastMonth.outflowChange <= 0 ? 'text-accent' : 'text-red-400'}`}>
                          {data.vsLastMonth.outflowChange >= 0 ? '+' : ''}{fmtShort(data.vsLastMonth.outflowChange)}
                        </span>
                      </div>
                      <div className="text-center">
                        <span className="text-[10px] text-muted font-mono block">NET</span>
                        <span className={`text-sm font-mono font-bold ${data.vsLastMonth.netFlowChange >= 0 ? 'text-accent' : 'text-red-400'}`}>
                          {data.vsLastMonth.netFlowChange >= 0 ? '+' : ''}{fmtShort(data.vsLastMonth.netFlowChange)}
                        </span>
                      </div>
                    </div>

                    {data.vsLastMonth.categoriesIncreased.length > 0 && (
                      <div>
                        <span className="text-[10px] font-mono text-red-400 tracking-label">↑ INCREASED</span>
                        <div className="mt-1 space-y-1">
                          {data.vsLastMonth.categoriesIncreased.map((c, i) => (
                            <div key={i} className="flex items-center justify-between text-xs">
                              <span className="text-txt-off">{c.category}</span>
                              <span className="text-red-400 font-mono">+{fmtShort(c.amount)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {data.vsLastMonth.categoriesDecreased.length > 0 && (
                      <div>
                        <span className="text-[10px] font-mono text-accent tracking-label">↓ DECREASED</span>
                        <div className="mt-1 space-y-1">
                          {data.vsLastMonth.categoriesDecreased.map((c, i) => (
                            <div key={i} className="flex items-center justify-between text-xs">
                              <span className="text-txt-off">{c.category}</span>
                              <span className="text-accent font-mono">-{fmtShort(c.amount)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

      </div>
    </ExportableCard>
  );
}
