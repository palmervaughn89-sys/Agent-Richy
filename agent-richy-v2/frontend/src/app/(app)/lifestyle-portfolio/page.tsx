'use client';

import React, { useState, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import {
  ChevronRight,
  ChevronLeft,
  Check,
  Minus,
  Plus,
  TrendingUp,
  ShieldAlert,
  BarChart3,
  ArrowRight,
  Sparkles,
  PieChart as PieChartIcon,
  MessageSquare,
  Info,
} from 'lucide-react';

import {
  BRANDS,
  CATEGORIES,
  RELATED_ETFS,
  deduplicateBrands,
  type Brand,
  type Category,
} from '@/data/lifestyle-brands';

/* ─── Design tokens (inline to avoid import issues) ─────────────── */
const CHART_GREENS = [
  '#00E87B',
  '#00C968',
  '#009E52',
  '#34D399',
  '#00E87B',
  '#059669',
  '#047857',
  '#065F46',
  '#5E736A',
  '#B8C9C0',
];
const tooltipStyle = {
  backgroundColor: '#101A15',
  border: '1px solid rgba(255,255,255,.06)',
  borderRadius: 14,
  color: '#F2F8F5',
  fontSize: 13,
};

/* ─── Helpers ────────────────────────────────────────────────────── */
function fmt(n: number): string {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(1)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(1)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
  return `$${n.toLocaleString()}`;
}

function pct(n: number): string {
  const sign = n >= 0 ? '+' : '';
  return `${sign}${n.toFixed(1)}%`;
}

/* Category icon emoji map */
const CAT_ICON: Record<Category, string> = {
  'Tech & Devices': '🖥️',
  'Shopping & Retail': '🛍️',
  'Food & Beverage': '🍔',
  'Streaming & Entertainment': '🎬',
  Transportation: '🚗',
  'Finance & Payments': '💳',
  'Health & Fitness': '💪',
  Telecom: '📱',
};

/* ─── Types ──────────────────────────────────────────────────────── */
interface SelectedBrand {
  brand: Brand;
  monthlySpend: number;
}

/* ================================================================== */
/*  PAGE                                                               */
/* ================================================================== */
export default function LifestylePortfolioPage() {
  const [step, setStep] = useState<1 | 2>(1);
  const [activeCategory, setActiveCategory] = useState<Category>(CATEGORIES[0]);
  const [selections, setSelections] = useState<Map<string, SelectedBrand>>(
    new Map(),
  );

  /* ── Selection logic ────────────────────────────────────────────── */
  const toggleBrand = useCallback(
    (brand: Brand) => {
      setSelections((prev) => {
        const next = new Map(prev);
        if (next.has(brand.name)) {
          next.delete(brand.name);
        } else {
          next.set(brand.name, { brand, monthlySpend: 50 });
        }
        return next;
      });
    },
    [],
  );

  const updateSpend = useCallback(
    (name: string, amount: number) => {
      setSelections((prev) => {
        const next = new Map(prev);
        const entry = next.get(name);
        if (entry) {
          next.set(name, { ...entry, monthlySpend: Math.max(5, amount) });
        }
        return next;
      });
    },
    [],
  );

  const selectedArray = useMemo(
    () => Array.from(selections.values()),
    [selections],
  );
  const canProceed = selectedArray.length >= 3;

  /* ── Portfolio computations ─────────────────────────────────────── */
  const portfolio = useMemo(() => {
    if (selectedArray.length === 0) return null;

    const deduped = deduplicateBrands(selectedArray);
    const totalSpend = deduped.reduce((s, e) => s + e.monthlySpend, 0);

    /* Allocation */
    const allocation = deduped.map((e) => ({
      ...e,
      weight: totalSpend > 0 ? (e.monthlySpend / totalSpend) * 100 : 0,
    }));

    /* Sector breakdown */
    const sectorMap = new Map<string, number>();
    for (const a of allocation) {
      sectorMap.set(
        a.brand.sector,
        (sectorMap.get(a.brand.sector) || 0) + a.weight,
      );
    }
    const sectors = Array.from(sectorMap.entries()).map(([name, value]) => ({
      name,
      value: Math.round(value * 10) / 10,
    }));

    /* Weighted stats */
    const weightedReturn1y =
      allocation.reduce((s, a) => s + a.brand.return1y * (a.weight / 100), 0);
    const weightedReturn5y =
      allocation.reduce((s, a) => s + a.brand.return5y * (a.weight / 100), 0);
    const weightedBeta =
      allocation.reduce((s, a) => s + a.brand.beta * (a.weight / 100), 0);
    const weightedDividend =
      allocation.reduce(
        (s, a) => s + a.brand.dividendYield * (a.weight / 100),
        0,
      );
    const weightedPE =
      allocation.reduce(
        (s, a) => s + (a.brand.pe > 0 ? a.brand.pe : 0) * (a.weight / 100),
        0,
      );

    /* Diversification score: 0-100 based on number of unique sectors & brands */
    const uniqueSectors = sectorMap.size;
    const uniqueTickers = new Set(allocation.map((a) => a.brand.ticker)).size;
    const diversification = Math.min(
      100,
      Math.round(
        uniqueSectors * 12 + uniqueTickers * 5 + (uniqueSectors >= 4 ? 15 : 0),
      ),
    );

    /* Related ETFs */
    const etfs = Array.from(
      new Map(
        sectors
          .flatMap((s) => RELATED_ETFS[s.name] || [])
          .map((e) => [e.ticker, e]),
      ).values(),
    ).slice(0, 6);

    return {
      allocation,
      sectors,
      totalSpend,
      weightedReturn1y,
      weightedReturn5y,
      weightedBeta,
      weightedDividend,
      weightedPE,
      diversification,
      uniqueSectors,
      uniqueTickers,
      etfs,
    };
  }, [selectedArray]);

  /* ── Render ─────────────────────────────────────────────────────── */
  return (
    <div className="flex-1 overflow-y-auto scroll-smooth">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <p className="section-label">LIFESTYLE PORTFOLIO</p>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-txt tracking-tight">
            Your Spending = A Portfolio
          </h1>
          <p className="text-off mt-2 max-w-2xl">
            Select the brands you spend money with and see how your lifestyle
            maps to the stock market. Richy turns your everyday purchases into
            portfolio insights.
          </p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center gap-3 mb-8">
          <StepPill active={step === 1} number={1} label="Select Brands" />
          <ChevronRight className="w-4 h-4 text-muted" />
          <StepPill active={step === 2} number={2} label="Your Portfolio" />
        </div>

        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.div
              key="step1"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25 }}
            >
              <StepOne
                activeCategory={activeCategory}
                setActiveCategory={setActiveCategory}
                selections={selections}
                toggleBrand={toggleBrand}
                updateSpend={updateSpend}
                selectedCount={selectedArray.length}
                canProceed={canProceed}
                onProceed={() => setStep(2)}
              />
            </motion.div>
          ) : (
            <motion.div
              key="step2"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25 }}
            >
              {portfolio && (
                <StepTwo portfolio={portfolio} onBack={() => setStep(1)} />
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Disclaimer */}
        <Disclaimer />
      </div>
    </div>
  );
}

/* ================================================================== */
/*  STEP PILL                                                          */
/* ================================================================== */
function StepPill({
  active,
  number,
  label,
}: {
  active: boolean;
  number: number;
  label: string;
}) {
  return (
    <div
      className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
        active
          ? 'bg-accent/10 text-accent border border-accent/30'
          : 'bg-card text-off border border-line'
      }`}
    >
      <span
        className={`w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold ${
          active ? 'bg-accent text-black' : 'bg-s2 text-muted'
        }`}
      >
        {number}
      </span>
      {label}
    </div>
  );
}

/* ================================================================== */
/*  STEP ONE — Brand Selector                                          */
/* ================================================================== */
interface StepOneProps {
  activeCategory: Category;
  setActiveCategory: (c: Category) => void;
  selections: Map<string, SelectedBrand>;
  toggleBrand: (b: Brand) => void;
  updateSpend: (name: string, amount: number) => void;
  selectedCount: number;
  canProceed: boolean;
  onProceed: () => void;
}

function StepOne({
  activeCategory,
  setActiveCategory,
  selections,
  toggleBrand,
  updateSpend,
  selectedCount,
  canProceed,
  onProceed,
}: StepOneProps) {
  const brandsInCategory = BRANDS.filter(
    (b) => b.category === activeCategory,
  );

  return (
    <div className="space-y-6">
      {/* Category tabs */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => {
          const count = BRANDS.filter(
            (b) => b.category === cat && selections.has(b.name),
          ).length;
          return (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`flex items-center gap-2 px-4 py-2 rounded-card text-sm font-medium transition-all ${
                activeCategory === cat
                  ? 'bg-accent/10 text-accent border border-accent/30'
                  : 'bg-card border border-line text-off hover:border-line-hover'
              }`}
            >
              <span>{CAT_ICON[cat]}</span>
              <span>{cat}</span>
              {count > 0 && (
                <span className="ml-1 w-5 h-5 flex items-center justify-center rounded-full bg-accent text-black text-[10px] font-bold">
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Brand grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {brandsInCategory.map((brand) => {
          const selected = selections.has(brand.name);
          const entry = selections.get(brand.name);
          return (
            <div
              key={brand.name}
              className={`rounded-card border p-4 transition-all cursor-pointer ${
                selected
                  ? 'bg-accent/5 border-accent/30'
                  : 'bg-card border-line hover:border-line-hover'
              }`}
            >
              {/* Top row: name + ticker + checkbox */}
              <div
                className="flex items-start justify-between"
                onClick={() => toggleBrand(brand)}
              >
                <div>
                  <p className="font-semibold text-txt">{brand.name}</p>
                  <p className="text-xs font-mono tracking-label text-accent/70 mt-0.5">
                    {brand.ticker} · {brand.sector}
                  </p>
                </div>
                <div
                  className={`w-6 h-6 rounded-md flex items-center justify-center border transition-colors ${
                    selected
                      ? 'bg-accent border-accent'
                      : 'border-line bg-s2'
                  }`}
                >
                  {selected && <Check className="w-3.5 h-3.5 text-black" />}
                </div>
              </div>

              {/* Price row */}
              <div className="flex items-center gap-3 mt-3 text-xs text-off">
                <span>${brand.price.toFixed(2)}</span>
                <span className="text-muted">|</span>
                <span>{brand.marketCap}</span>
                <span className="text-muted">|</span>
                <span
                  className={
                    brand.return1y >= 0 ? 'text-accent' : 'text-red-400'
                  }
                >
                  {pct(brand.return1y)} 1Y
                </span>
              </div>

              {/* Spend slider (shown when selected) */}
              <AnimatePresence>
                {selected && entry && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="mt-4 pt-3 border-t border-line/50">
                      <label className="text-xs font-mono tracking-label text-muted uppercase">
                        Monthly spend
                      </label>
                      <div className="flex items-center gap-3 mt-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            updateSpend(brand.name, entry.monthlySpend - 25);
                          }}
                          className="w-8 h-8 rounded-lg bg-s2 border border-line flex items-center justify-center text-off hover:text-txt hover:border-line-hover transition"
                        >
                          <Minus className="w-3.5 h-3.5" />
                        </button>
                        <div className="flex-1">
                          <input
                            type="range"
                            min={5}
                            max={2000}
                            step={5}
                            value={entry.monthlySpend}
                            onChange={(e) =>
                              updateSpend(brand.name, Number(e.target.value))
                            }
                            onClick={(e) => e.stopPropagation()}
                            className="w-full h-1.5 rounded-full appearance-none bg-s2 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-accent [&::-webkit-slider-thumb]:cursor-pointer"
                          />
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            updateSpend(brand.name, entry.monthlySpend + 25);
                          }}
                          className="w-8 h-8 rounded-lg bg-s2 border border-line flex items-center justify-center text-off hover:text-txt hover:border-line-hover transition"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                        <span className="w-20 text-right font-mono text-sm text-accent font-semibold">
                          ${entry.monthlySpend.toLocaleString()}/mo
                        </span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>

      {/* Selected summary + proceed */}
      <div className="flex items-center justify-between bg-s1 border border-line rounded-card p-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
            <PieChartIcon className="w-5 h-5 text-accent" />
          </div>
          <div>
            <p className="text-sm font-semibold text-txt">
              {selectedCount} brand{selectedCount !== 1 ? 's' : ''} selected
            </p>
            <p className="text-xs text-muted">
              {canProceed
                ? 'Ready to build your portfolio'
                : `Select at least 3 brands to continue`}
            </p>
          </div>
        </div>
        <button
          disabled={!canProceed}
          onClick={onProceed}
          className="btn-primary flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Build My Lifestyle Portfolio
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

/* ================================================================== */
/*  STEP TWO — Portfolio Results                                       */
/* ================================================================== */
interface Portfolio {
  allocation: (SelectedBrand & { weight: number })[];
  sectors: { name: string; value: number }[];
  totalSpend: number;
  weightedReturn1y: number;
  weightedReturn5y: number;
  weightedBeta: number;
  weightedDividend: number;
  weightedPE: number;
  diversification: number;
  uniqueSectors: number;
  uniqueTickers: number;
  etfs: { ticker: string; name: string }[];
}

function StepTwo({
  portfolio,
  onBack,
}: {
  portfolio: Portfolio;
  onBack: () => void;
}) {
  return (
    <div className="space-y-8">
      {/* Back */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-off hover:text-accent transition"
      >
        <ChevronLeft className="w-4 h-4" />
        Edit selections
      </button>

      {/* ── Section A: Donut + Allocation Table ───────────────────── */}
      <section>
        <p className="section-label">PORTFOLIO ALLOCATION</p>
        <h2 className="text-2xl font-extrabold text-txt tracking-tight mb-6">
          Where Your Money Goes
        </h2>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Donut */}
          <div className="rounded-card bg-card border border-line p-6 flex items-center justify-center min-h-[320px]">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={portfolio.allocation.map((a) => ({
                    name: a.brand.name,
                    value: Math.round(a.weight * 10) / 10,
                  }))}
                  cx="50%"
                  cy="50%"
                  innerRadius={72}
                  outerRadius={120}
                  paddingAngle={2}
                  dataKey="value"
                  stroke="transparent"
                >
                  {portfolio.allocation.map((_, i) => (
                    <Cell
                      key={i}
                      fill={CHART_GREENS[i % CHART_GREENS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => [`${value.toFixed(1)}%`, 'Weight']}
                  contentStyle={tooltipStyle}
                />
                <Legend
                  wrapperStyle={{ fontSize: 12, color: '#B8C9C0' }}
                  iconType="circle"
                  iconSize={8}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Table */}
          <div className="rounded-card bg-card border border-line overflow-hidden">
            <div className="grid grid-cols-[1fr_auto_auto_auto] gap-x-4 px-4 py-3 bg-s1 border-b border-line text-[11px] font-mono tracking-label uppercase text-muted">
              <span>Brand / Ticker</span>
              <span className="text-right">Monthly</span>
              <span className="text-right">Weight</span>
              <span className="text-right">1Y Return</span>
            </div>
            <div className="max-h-[280px] overflow-y-auto">
              {portfolio.allocation
                .sort((a, b) => b.weight - a.weight)
                .map((a, i) => (
                  <div
                    key={i}
                    className="grid grid-cols-[1fr_auto_auto_auto] gap-x-4 px-4 py-3 border-b border-line/50 last:border-0 text-sm"
                  >
                    <div>
                      <span className="text-txt font-medium">
                        {a.brand.name}
                      </span>
                      <span className="ml-2 text-xs font-mono text-muted">
                        {a.brand.ticker}
                      </span>
                    </div>
                    <span className="text-right text-off">
                      ${a.monthlySpend}
                    </span>
                    <span className="text-right text-accent font-semibold">
                      {a.weight.toFixed(1)}%
                    </span>
                    <span
                      className={`text-right ${
                        a.brand.return1y >= 0 ? 'text-accent' : 'text-red-400'
                      }`}
                    >
                      {pct(a.brand.return1y)}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Section B: Per-company data cards ─────────────────────── */}
      <section>
        <p className="section-label">PUBLIC MARKET DATA</p>
        <h2 className="text-2xl font-extrabold text-txt tracking-tight mb-6">
          Company Snapshots
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {portfolio.allocation
            .sort((a, b) => b.weight - a.weight)
            .map((a, i) => (
              <div
                key={i}
                className="rounded-card bg-card border border-line p-5 hover:border-line-hover transition"
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="font-semibold text-txt">{a.brand.name}</p>
                    <p className="text-xs font-mono tracking-label text-accent/70">
                      {a.brand.ticker} · {a.brand.sector}
                    </p>
                  </div>
                  <span className="badge-pill">{a.weight.toFixed(1)}%</span>
                </div>

                {/* Row 1 */}
                <div className="grid grid-cols-3 gap-3 text-center">
                  <MetricMini label="Price" value={`$${a.brand.price}`} />
                  <MetricMini label="Mkt Cap" value={a.brand.marketCap} />
                  <MetricMini
                    label="P/E"
                    value={a.brand.pe > 0 ? a.brand.pe.toFixed(1) : 'N/A'}
                  />
                </div>
                {/* Row 2 */}
                <div className="grid grid-cols-3 gap-3 text-center mt-3">
                  <MetricMini
                    label="Rev Growth"
                    value={pct(a.brand.revenueGrowth)}
                    accent={a.brand.revenueGrowth >= 0}
                  />
                  <MetricMini
                    label="Div Yield"
                    value={
                      a.brand.dividendYield > 0
                        ? `${a.brand.dividendYield.toFixed(2)}%`
                        : '—'
                    }
                  />
                  <MetricMini
                    label="Beta"
                    value={a.brand.beta.toFixed(2)}
                  />
                </div>
                {/* Row 3 */}
                <div className="grid grid-cols-3 gap-3 text-center mt-3">
                  <MetricMini
                    label="1Y Return"
                    value={pct(a.brand.return1y)}
                    accent={a.brand.return1y >= 0}
                  />
                  <MetricMini
                    label="5Y Return"
                    value={pct(a.brand.return5y)}
                    accent={a.brand.return5y >= 0}
                  />
                  <MetricMini
                    label="52W High"
                    value={`$${a.brand.high52}`}
                  />
                </div>
              </div>
            ))}
        </div>
      </section>

      {/* ── Section C: Aggregate stats + Diversification ──────────── */}
      <section>
        <p className="section-label">PORTFOLIO STATISTICS</p>
        <h2 className="text-2xl font-extrabold text-txt tracking-tight mb-6">
          Aggregate Metrics
        </h2>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-6">
          {/* Stats grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <StatCard
              label="Monthly Total"
              value={`$${portfolio.totalSpend.toLocaleString()}`}
              sub="per month"
            />
            <StatCard
              label="Annual Spend"
              value={`$${(portfolio.totalSpend * 12).toLocaleString()}`}
              sub="projected"
            />
            <StatCard
              label="Weighted 1Y Return"
              value={pct(portfolio.weightedReturn1y)}
              accent={portfolio.weightedReturn1y >= 0}
            />
            <StatCard
              label="Weighted 5Y Return"
              value={pct(portfolio.weightedReturn5y)}
              accent={portfolio.weightedReturn5y >= 0}
            />
            <StatCard
              label="Portfolio Beta"
              value={portfolio.weightedBeta.toFixed(2)}
              sub={
                portfolio.weightedBeta > 1.2
                  ? 'Higher volatility'
                  : portfolio.weightedBeta < 0.8
                    ? 'Lower volatility'
                    : 'Moderate volatility'
              }
            />
            <StatCard
              label="Avg Dividend Yield"
              value={`${portfolio.weightedDividend.toFixed(2)}%`}
              sub="weighted"
            />
            <StatCard
              label="Avg P/E Ratio"
              value={portfolio.weightedPE.toFixed(1)}
              sub="weighted"
            />
            <StatCard
              label="Unique Sectors"
              value={`${portfolio.uniqueSectors}`}
              sub={`${portfolio.uniqueTickers} unique stocks`}
            />
            {/* Sector breakdown pie */}
            <div className="rounded-card bg-card border border-line p-5 sm:col-span-1">
              <p className="text-xs font-mono tracking-label text-muted uppercase mb-3">
                Sector Mix
              </p>
              <ResponsiveContainer width="100%" height={150}>
                <PieChart>
                  <Pie
                    data={portfolio.sectors}
                    cx="50%"
                    cy="50%"
                    outerRadius={55}
                    dataKey="value"
                    stroke="transparent"
                  >
                    {portfolio.sectors.map((_, i) => (
                      <Cell
                        key={i}
                        fill={CHART_GREENS[i % CHART_GREENS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number) => [
                      `${value.toFixed(1)}%`,
                      'Weight',
                    ]}
                    contentStyle={tooltipStyle}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Diversification gauge */}
          <div className="rounded-card bg-card border border-line p-6 flex flex-col items-center justify-center">
            <p className="text-xs font-mono tracking-label text-muted uppercase mb-4">
              Diversification Score
            </p>
            <DiversificationGauge score={portfolio.diversification} />
            <p className="text-sm text-off mt-4 text-center">
              {portfolio.diversification >= 80
                ? 'Excellent diversification across sectors and companies.'
                : portfolio.diversification >= 55
                  ? 'Good mix, but adding more sectors could help.'
                  : 'Consider spreading your spending across more categories.'}
            </p>
          </div>
        </div>
      </section>

      {/* ── Section D: Insight text ───────────────────────────────── */}
      <section className="rounded-card bg-accent/5 border border-accent/20 p-6">
        <div className="flex gap-3">
          <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-5 h-5 text-accent" />
          </div>
          <div>
            <p className="font-semibold text-accent mb-2">
              Richy&apos;s Lifestyle Insight
            </p>
            <p className="text-off text-sm leading-relaxed">
              {generateInsight(portfolio)}
            </p>
          </div>
        </div>
      </section>

      {/* ── Section E: Explore Further ────────────────────────────── */}
      <section>
        <p className="section-label">EXPLORE FURTHER</p>
        <h2 className="text-2xl font-extrabold text-txt tracking-tight mb-6">
          Next Steps
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Related ETFs */}
          <div className="rounded-card bg-card border border-line p-5 hover:border-line-hover transition">
            <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-3">
              <BarChart3 className="w-5 h-5 text-accent" />
            </div>
            <h3 className="font-semibold text-txt mb-2">Related ETFs</h3>
            <p className="text-xs text-muted mb-3">
              ETFs that cover your lifestyle sectors
            </p>
            <div className="space-y-2">
              {portfolio.etfs.slice(0, 4).map((etf) => (
                <div
                  key={etf.ticker}
                  className="flex items-center justify-between text-xs"
                >
                  <span className="font-mono text-accent">{etf.ticker}</span>
                  <span className="text-off">{etf.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Compare to S&P */}
          <div className="rounded-card bg-card border border-line p-5 hover:border-line-hover transition">
            <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-3">
              <TrendingUp className="w-5 h-5 text-accent" />
            </div>
            <h3 className="font-semibold text-txt mb-2">
              S&P 500 Comparison
            </h3>
            <p className="text-xs text-muted mb-3">
              How does your lifestyle portfolio compare?
            </p>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-off">Your 1Y Return</span>
                <span
                  className={
                    portfolio.weightedReturn1y >= 0
                      ? 'text-accent'
                      : 'text-red-400'
                  }
                >
                  {pct(portfolio.weightedReturn1y)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-off">S&P 500 1Y Return</span>
                <span className="text-accent">+24.5%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-off">Your Beta</span>
                <span className="text-txt">
                  {portfolio.weightedBeta.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-off">S&P 500 Beta</span>
                <span className="text-txt">1.00</span>
              </div>
            </div>
          </div>

          {/* Chat with Richy */}
          <a
            href="/chat"
            className="rounded-card bg-card border border-line p-5 hover:border-line-hover transition block"
          >
            <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-3">
              <MessageSquare className="w-5 h-5 text-accent" />
            </div>
            <h3 className="font-semibold text-txt mb-2">
              Ask Richy
            </h3>
            <p className="text-xs text-muted mb-3">
              Get personalized advice on turning spending into investing
            </p>
            <span className="text-accent text-sm font-medium flex items-center gap-1">
              Open Chat <ArrowRight className="w-3.5 h-3.5" />
            </span>
          </a>
        </div>
      </section>
    </div>
  );
}

/* ================================================================== */
/*  SUB-COMPONENTS                                                     */
/* ================================================================== */

function MetricMini({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className="rounded-lg bg-s1 p-2">
      <p className="text-[10px] font-mono tracking-label text-muted uppercase">
        {label}
      </p>
      <p
        className={`text-sm font-semibold mt-0.5 ${
          accent === true
            ? 'text-accent'
            : accent === false
              ? 'text-red-400'
              : 'text-txt'
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function StatCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: boolean;
}) {
  return (
    <div className="rounded-card bg-card border border-line p-5">
      <p className="text-xs font-mono tracking-label text-muted uppercase">
        {label}
      </p>
      <p
        className={`text-2xl font-extrabold mt-1 ${
          accent === true
            ? 'text-accent'
            : accent === false
              ? 'text-red-400'
              : 'text-txt'
        }`}
      >
        {value}
      </p>
      {sub && <p className="text-xs text-muted mt-1">{sub}</p>}
    </div>
  );
}

/* ── Diversification Gauge (SVG) ──────────────────────────────────── */
function DiversificationGauge({ score }: { score: number }) {
  const r = 70;
  const circumference = Math.PI * r; // semicircle
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative">
      <svg width="180" height="100" viewBox="0 0 180 100">
        {/* Background arc */}
        <path
          d="M 10 90 A 70 70 0 0 1 170 90"
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="12"
          strokeLinecap="round"
        />
        {/* Value arc */}
        <path
          d="M 10 90 A 70 70 0 0 1 170 90"
          fill="none"
          stroke="#00E87B"
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={`${circumference}`}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex items-end justify-center pb-1">
        <span className="text-3xl font-extrabold text-txt">{score}</span>
        <span className="text-sm text-muted ml-1 mb-1">/100</span>
      </div>
    </div>
  );
}

/* ── Disclaimer ───────────────────────────────────────────────────── */
function Disclaimer() {
  return (
    <div className="mt-12 mb-6 rounded-card bg-s1 border border-line p-4 flex gap-3">
      <ShieldAlert className="w-5 h-5 text-muted flex-shrink-0 mt-0.5" />
      <div className="text-xs text-muted leading-relaxed">
        <p className="font-semibold text-off mb-1 flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5" />
          Important Disclaimer
        </p>
        <p>
          This tool is for <strong className="text-off">educational and
          entertainment purposes only</strong>. It is{' '}
          <strong className="text-off">NOT investment advice</strong>. The
          &ldquo;portfolio&rdquo; shown maps your everyday spending to publicly
          traded companies — it does not represent actual stock ownership, a
          recommendation to buy or sell securities, or a substitute for
          professional financial advice. All market data shown is placeholder /
          approximate and may not reflect current prices. Past performance does
          not guarantee future results. Always consult a licensed financial
          advisor before making investment decisions.
        </p>
      </div>
    </div>
  );
}

/* ── Dynamic insight generator ────────────────────────────────────── */
function generateInsight(p: Portfolio): string {
  const lines: string[] = [];

  // Spend insight
  lines.push(
    `You spend about $${p.totalSpend.toLocaleString()} per month across ${p.uniqueTickers} publicly traded companies in ${p.uniqueSectors} sectors.`,
  );

  // Annual projection
  const annual = p.totalSpend * 12;
  lines.push(
    `That's $${annual.toLocaleString()} per year flowing directly to the brands in your lifestyle.`,
  );

  // Return comparison
  if (p.weightedReturn1y > 20) {
    lines.push(
      `If you had invested that same amount proportionally, your lifestyle portfolio would have returned ${pct(p.weightedReturn1y)} over the past year — outperforming many benchmarks.`,
    );
  } else if (p.weightedReturn1y > 0) {
    lines.push(
      `Your lifestyle portfolio shows a ${pct(p.weightedReturn1y)} weighted 1-year return — solid, though comparing to a broad index like the S&P 500 can put that in perspective.`,
    );
  } else {
    lines.push(
      `Your lifestyle portfolio shows a ${pct(p.weightedReturn1y)} weighted 1-year return. Some of the brands you support have had a tough year — diversification can help smooth that out.`,
    );
  }

  // Beta insight
  if (p.weightedBeta > 1.3) {
    lines.push(
      `With a beta of ${p.weightedBeta.toFixed(2)}, your portfolio is more volatile than the market. High-beta spending means bigger swings — both up and down.`,
    );
  } else if (p.weightedBeta < 0.8) {
    lines.push(
      `With a beta of ${p.weightedBeta.toFixed(2)}, your spending leans toward stable, defensive companies — they tend to hold up better in downturns.`,
    );
  }

  // Dividend insight
  if (p.weightedDividend > 2) {
    lines.push(
      `Good news: your brands pay a weighted ${p.weightedDividend.toFixed(2)}% dividend yield, meaning some of your spending could come back as passive income if invested.`,
    );
  }

  return lines.join(' ');
}
