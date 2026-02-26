'use client';

import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { TopNav } from '@/components/layout';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  BarChart, Bar, PieChart, Pie, Cell,
} from 'recharts';
import {
  TrendingUp,
  CreditCard,
  PiggyBank,
  ShieldCheck,
} from 'lucide-react';

/* ══════════════════════════════════════════════════════════════════════
   CALCULATOR DEFINITIONS
   ══════════════════════════════════════════════════════════════════════ */

/* ── Compound Interest ─────────────────────────────────────────────── */
function CompoundInterestCalc() {
  const [principal, setPrincipal] = useState(5000);
  const [monthly, setMonthly] = useState(200);
  const [rate, setRate] = useState(7);
  const [years, setYears] = useState(20);
  const [extra, setExtra] = useState(false);

  const contribution = extra ? monthly + 100 : monthly;

  const data = useMemo(() => {
    const pts: { year: number; contributions: number; interest: number; total: number }[] = [];
    let bal = principal;
    let totalContrib = principal;
    for (let y = 0; y <= years; y++) {
      const interest = bal - totalContrib;
      pts.push({ year: y, contributions: Math.round(totalContrib), interest: Math.round(interest < 0 ? 0 : interest), total: Math.round(bal) });
      for (let m = 0; m < 12; m++) {
        bal = bal * (1 + rate / 100 / 12) + contribution;
        totalContrib += contribution;
      }
    }
    return pts;
  }, [principal, contribution, rate, years]);

  const final = data[data.length - 1];

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Initial Amount" prefix="$" value={principal} onChange={setPrincipal} />
        <Field label="Monthly Contribution" prefix="$" value={monthly} onChange={setMonthly} />
        <Field label="Annual Return (%)" suffix="%" value={rate} onChange={setRate} step={0.5} />
        <Field label="Years" value={years} onChange={setYears} />
      </div>

      <label className="flex items-center gap-2 text-xs text-txt-off cursor-pointer select-none">
        <input
          type="checkbox"
          checked={extra}
          onChange={() => setExtra(!extra)}
          className="rounded border-line bg-s2 text-accent focus:ring-accent"
        />
        What if you invested $100 more per month?
      </label>

      {/* Results */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <ResultCard label="Final Amount" value={fmt(final.total)} color="text-accent" />
        <ResultCard label="Total Contributed" value={fmt(final.contributions)} color="text-txt-off" />
        <ResultCard label="Interest Earned" value={fmt(final.interest)} color="text-amber-400" />
      </div>

      {/* Chart */}
      <div className="h-52 mt-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.06)" />
            <XAxis dataKey="year" tick={{ fill: '#B8C9C0', fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#B8C9C0', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
            <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`$${v.toLocaleString()}`, '']} />
            <Line type="monotone" dataKey="contributions" stroke="#5E736A" strokeWidth={2} dot={false} name="Contributions" />
            <Line type="monotone" dataKey="total" stroke="#00E87B" strokeWidth={2} dot={false} name="Total" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

/* ── Debt Payoff ───────────────────────────────────────────────────── */
function DebtPayoffCalc() {
  const [balance, setBalance] = useState(8000);
  const [apr, setApr] = useState(18);
  const [minPay, setMinPay] = useState(200);
  const [extraPay, setExtraPay] = useState(100);

  const calc = (payment: number) => {
    let bal = balance;
    let months = 0;
    let totalInterest = 0;
    const monthlyRate = apr / 100 / 12;
    while (bal > 0 && months < 600) {
      const interest = bal * monthlyRate;
      totalInterest += interest;
      bal = bal + interest - payment;
      if (bal < 0) bal = 0;
      months++;
    }
    return { months, totalInterest: Math.round(totalInterest) };
  };

  const minResult = calc(minPay);
  const extraResult = calc(minPay + extraPay);
  const saved = minResult.totalInterest - extraResult.totalInterest;

  const barData = [
    { label: 'Min Only', months: minResult.months, interest: minResult.totalInterest },
    { label: '+ Extra', months: extraResult.months, interest: extraResult.totalInterest },
  ];

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Total Debt" prefix="$" value={balance} onChange={setBalance} />
        <Field label="Interest Rate (APR)" suffix="%" value={apr} onChange={setApr} step={0.5} />
        <Field label="Minimum Payment" prefix="$" value={minPay} onChange={setMinPay} />
        <Field label="Extra Payment" prefix="$" value={extraPay} onChange={setExtraPay} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <ResultCard label="Min-Only Payoff" value={`${minResult.months} mo`} color="text-red-400" />
        <ResultCard label="With Extra" value={`${extraResult.months} mo`} color="text-accent" />
        <ResultCard label="Interest Saved" value={fmt(saved)} color="text-amber-400" />
      </div>

      <div className="h-44">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={barData} layout="vertical" barGap={8}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.06)" horizontal={false} />
            <XAxis type="number" tick={{ fill: '#B8C9C0', fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="label" tick={{ fill: '#B8C9C0', fontSize: 11 }} axisLine={false} tickLine={false} width={60} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="months" fill="#EF4444" name="Months" radius={[0, 6, 6, 0]} barSize={20} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

/* ── 50/30/20 Budget Builder ───────────────────────────────────────── */
function BudgetBuilderCalc() {
  const [income, setIncome] = useState(5000);
  const [needs, setNeeds] = useState(50);
  const [wants, setWants] = useState(30);
  const savings = 100 - needs - wants;

  const pieData = [
    { name: 'Needs', value: needs, color: '#5E736A' },
    { name: 'Wants', value: wants, color: '#F59E0B' },
    { name: 'Savings', value: Math.max(savings, 0), color: '#00E87B' },
  ];

  return (
    <div className="space-y-5">
      <Field label="Monthly Take-Home Income" prefix="$" value={income} onChange={setIncome} />

      <div className="space-y-3">
        <SliderField label="Needs" value={needs} onChange={setNeeds} max={100 - wants} color="bg-txt-muted" amount={Math.round(income * needs / 100)} />
        <SliderField label="Wants" value={wants} onChange={setWants} max={100 - needs} color="bg-amber-500" amount={Math.round(income * wants / 100)} />
        <div className="flex items-center justify-between text-xs">
          <span className="text-txt-off font-medium">Savings: {savings}%</span>
          <span className="text-accent font-semibold">{fmt(Math.round(income * savings / 100))}</span>
        </div>
      </div>

      <div className="w-40 h-40 mx-auto">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={pieData} cx="50%" cy="50%" innerRadius={30} outerRadius={60} paddingAngle={3} dataKey="value">
              {pieData.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`${v}%`, '']} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <ResultCard label="Needs" value={fmt(Math.round(income * needs / 100))} color="text-txt-off" />
        <ResultCard label="Wants" value={fmt(Math.round(income * wants / 100))} color="text-amber-400" />
        <ResultCard label="Savings" value={fmt(Math.round(income * savings / 100))} color="text-accent" />
      </div>
    </div>
  );
}

/* ── Emergency Fund ────────────────────────────────────────────────── */
function EmergencyFundCalc() {
  const [monthlyExp, setMonthlyExp] = useState(3000);
  const [currentSav, setCurrentSav] = useState(5000);

  const target = monthlyExp * 6;
  const coverage = monthlyExp > 0 ? currentSav / monthlyExp : 0;
  const gap = Math.max(target - currentSav, 0);
  const pct = Math.min((currentSav / target) * 100, 100);

  const savPerMonth = 500;
  const monthsToFill = gap > 0 ? Math.ceil(gap / savPerMonth) : 0;

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Monthly Essential Expenses" prefix="$" value={monthlyExp} onChange={setMonthlyExp} />
        <Field label="Current Savings" prefix="$" value={currentSav} onChange={setCurrentSav} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <ResultCard label="Months Covered" value={`${coverage.toFixed(1)} mo`} color={coverage >= 6 ? 'text-accent' : coverage >= 3 ? 'text-amber-400' : 'text-red-400'} />
        <ResultCard label="Target (6 mo)" value={fmt(target)} color="text-txt-off" />
        <ResultCard label="Gap to Fill" value={fmt(gap)} color="text-amber-400" />
      </div>

      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-xs text-txt-muted mb-1">
          <span>Progress</span>
          <span>{pct.toFixed(0)}%</span>
        </div>
        <div className="h-4 rounded-full bg-s2 overflow-hidden border border-line">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={`h-full rounded-full ${pct >= 100 ? 'bg-accent' : pct >= 50 ? 'bg-amber-500' : 'bg-red-500'}`}
          />
        </div>
      </div>

      {gap > 0 && (
        <p className="text-xs text-txt-off bg-ghost rounded-card p-3 border border-line">
          At <span className="text-txt font-semibold">{fmt(savPerMonth)}/month</span> in savings, you&apos;ll hit your target in{' '}
          <span className="text-accent font-semibold">{monthsToFill} months</span>.
        </p>
      )}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════
   SHARED UI COMPONENTS
   ══════════════════════════════════════════════════════════════════════ */

const tooltipStyle = { backgroundColor: '#101A15', border: '1px solid rgba(255,255,255,.06)', borderRadius: '14px', fontSize: '11px', color: '#F2F8F5' };

function fmt(n: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);
}

function Field({ label, value, onChange, prefix, suffix, step }: {
  label: string; value: number; onChange: (v: number) => void;
  prefix?: string; suffix?: string; step?: number;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-txt-muted mb-1">{label}</label>
      <div className="relative">
        {prefix && <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-txt-muted">{prefix}</span>}
        <input
          type="number"
          value={value}
          step={step}
          onChange={(e) => onChange(Number(e.target.value))}
          className={`w-full rounded-card border border-line bg-s2 py-2.5 text-sm text-txt
                      outline-none focus:ring-2 focus:ring-accent focus:border-transparent
                      ${prefix ? 'pl-7' : 'pl-3'} ${suffix ? 'pr-8' : 'pr-3'}`}
        />
        {suffix && <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-txt-muted">{suffix}</span>}
      </div>
    </div>
  );
}

function SliderField({ label, value, onChange, max, color, amount }: {
  label: string; value: number; onChange: (v: number) => void; max: number; color: string; amount: number;
}) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs mb-1">
        <span className="text-txt-off font-medium">{label}: {value}%</span>
        <span className="text-txt-muted">{fmt(amount)}</span>
      </div>
      <input
        type="range"
        min={0}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className={`w-full h-1.5 rounded-full appearance-none cursor-pointer ${color}`}
        style={{ accentColor: color === 'bg-txt-muted' ? '#5E736A' : '#F59E0B' }}
      />
    </div>
  );
}

function ResultCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-card bg-s1 border border-line p-3 text-center">
      <p className={`text-lg font-bold ${color}`}>{value}</p>
      <p className="text-[10px] text-txt-muted mt-0.5">{label}</p>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════
   CALCULATORS PAGE
   ══════════════════════════════════════════════════════════════════════ */

const CALCS = [
  { id: 'compound', label: 'Compound Interest', icon: TrendingUp, component: CompoundInterestCalc },
  { id: 'debt', label: 'Debt Payoff', icon: CreditCard, component: DebtPayoffCalc },
  { id: 'budget', label: '50/30/20 Budget', icon: PiggyBank, component: BudgetBuilderCalc },
  { id: 'emergency', label: 'Emergency Fund', icon: ShieldCheck, component: EmergencyFundCalc },
];

export default function CalculatorsPage() {
  const [active, setActive] = useState('compound');
  const current = CALCS.find((c) => c.id === active)!;
  const ActiveComponent = current.component;

  return (
    <div className="flex flex-col h-full">
      <TopNav title="Financial Calculators" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6 space-y-6">
        <div>
          <p className="section-label">CALCULATORS</p>
          <h2 className="text-2xl font-extrabold text-txt tracking-tight mb-1">Run the Numbers</h2>
          <p className="text-sm text-txt-off">Make data-driven decisions before committing.</p>

          {/* Calc selector */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.15 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-6 mb-8"
          >
            {CALCS.map((calc) => {
              const isActive = calc.id === active;
              return (
                <button
                  key={calc.id}
                  onClick={() => setActive(calc.id)}
                  className={`flex items-center gap-3 rounded-card border p-4 text-left transition-all ${
                    isActive
                      ? 'bg-ghost border-line-hover text-txt'
                      : 'bg-card border-line text-txt-off hover:border-line-hover hover:text-txt'
                  }`}
                >
                  <calc.icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-accent' : ''}`} />
                  <span className="text-xs font-semibold">{calc.label}</span>
                </button>
              );
            })}
          </motion.div>

          {/* Active calculator */}
          <motion.div
            key={active}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.15 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="rounded-card bg-card border border-line p-5 md:p-6"
          >
            <h3 className="text-base font-semibold text-txt mb-5 flex items-center gap-2">
              <current.icon className="w-5 h-5 text-accent" />
              {current.label}
            </h3>
            <ActiveComponent />
          </motion.div>
        </div>
      </div>
    </div>
  );
}
