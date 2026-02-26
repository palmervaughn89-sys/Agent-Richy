'use client';

import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { TopNav } from '@/components/layout';
import { useProfileStore } from '@/hooks/useFinancialProfile';

const REVEAL = {
  initial: { opacity: 0, y: 30 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.15 },
  transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] as number[] },
};

function fmt(n: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);
}

interface Goal {
  id: string;
  title: string;
  target: number;
  current: number;
  deadline?: string;
  emoji: string;
}

export default function PlanPage() {
  const { profile } = useProfileStore();
  const [activeSection, setActiveSection] = useState<'budget' | 'debt' | 'goals'>('budget');
  const [goals, setGoals] = useState<Goal[]>([
    { id: '1', title: 'Emergency Fund', target: 10000, current: profile?.emergency_fund ?? 0, emoji: '🛟' },
    { id: '2', title: 'Pay Off Debt', target: Object.values(profile?.debts ?? {}).reduce((s, v) => s + v, 0), current: 0, emoji: '💳' },
  ]);
  const [newGoalTitle, setNewGoalTitle] = useState('');
  const [newGoalTarget, setNewGoalTarget] = useState('');

  const income = profile?.monthly_income ?? 0;
  const expenses = profile?.monthly_expenses ?? 0;
  const debts = profile?.debts ?? {};
  const debtRates = profile?.debt_interest_rates ?? {};
  const totalDebt = Object.values(debts).reduce((s, v) => s + v, 0);
  const surplus = income - expenses;

  // 50/30/20 Budget
  const budget = useMemo(() => {
    if (income <= 0) return null;
    return {
      needs: { label: 'Needs', amount: income * 0.5, pct: 50, color: 'bg-accent/60', items: 'Housing, groceries, insurance, utilities, transportation' },
      wants: { label: 'Wants', amount: income * 0.3, pct: 30, color: 'bg-amber-500', items: 'Dining, entertainment, subscriptions, shopping' },
      savings: { label: 'Savings & Debt', amount: income * 0.2, pct: 20, color: 'bg-accent', items: 'Emergency fund, investments, debt payments' },
    };
  }, [income]);

  // Debt avalanche order (highest rate first)
  const debtPlan = useMemo(() => {
    const entries = Object.entries(debts).map(([name, balance]) => ({
      name,
      balance,
      rate: debtRates[name] ?? 0,
    }));
    return entries.sort((a, b) => b.rate - a.rate);
  }, [debts, debtRates]);

  const addGoal = () => {
    if (!newGoalTitle.trim() || !newGoalTarget) return;
    setGoals((prev) => [
      ...prev,
      { id: `g_${Date.now()}`, title: newGoalTitle, target: Number(newGoalTarget), current: 0, emoji: '🎯' },
    ]);
    setNewGoalTitle('');
    setNewGoalTarget('');
  };

  const removeGoal = (id: string) => setGoals((prev) => prev.filter((g) => g.id !== id));

  const TABS = [
    { key: 'budget' as const, label: '💰 Budget', disabled: false },
    { key: 'debt' as const, label: '💳 Debt Plan', disabled: false },
    { key: 'goals' as const, label: '🎯 Goals', disabled: false },
  ];

  return (
    <div className="flex flex-col h-full">
      <TopNav title="My Plan 🎯" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6 space-y-6">
        {/* Header */}
        <motion.div {...REVEAL}>
          <p className="section-label">GOAL PLANNING</p>
          <h1 className="section-title">
            Set targets. <span className="text-muted">Hit them.</span>
          </h1>
        </motion.div>

        {/* Tabs */}
        <motion.div {...REVEAL} className="flex gap-2 flex-wrap">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveSection(t.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${activeSection === t.key
                  ? 'bg-accent text-black shadow-sm'
                  : 'bg-card text-muted border border-line hover:text-txt'
                }`}
            >
              {t.label}
            </button>
          ))}
        </motion.div>

        {/* BUDGET SECTION */}
        {activeSection === 'budget' && (
          <motion.div {...REVEAL} className="space-y-4">
            {income > 0 && budget ? (
              <>
                <div className="rounded-card bg-card border border-line p-5">
                  <h3 className="text-sm font-semibold text-txt mb-1">50/30/20 Budget Breakdown</h3>
                  <p className="text-xs text-muted mb-4">Based on {fmt(income)}/month income</p>

                  {/* Bar chart */}
                  <div className="flex h-8 rounded-lg overflow-hidden mb-4">
                    {Object.values(budget).map((cat) => (
                      <div
                        key={cat.label}
                        className={`${cat.color} flex items-center justify-center text-[10px] font-bold text-black`}
                        style={{ width: `${cat.pct}%` }}
                      >
                        {cat.pct}%
                      </div>
                    ))}
                  </div>

                  {/* Details */}
                  <div className="space-y-3">
                    {Object.values(budget).map((cat) => (
                      <div key={cat.label} className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <div className={`w-3 h-3 rounded-full ${cat.color}`} />
                            <span className="text-sm font-medium text-txt">{cat.label}</span>
                          </div>
                          <p className="text-[10px] text-muted ml-5">{cat.items}</p>
                        </div>
                        <span className="text-sm font-bold text-off">{fmt(cat.amount)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Surplus indicator */}
                <div className={`rounded-card border p-4 ${
                  surplus >= 0
                    ? 'bg-accent/10 border-accent/20'
                    : 'bg-red-900/20 border-red-800/40'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-off">Monthly Surplus</span>
                    <span className={`text-lg font-bold ${surplus >= 0 ? 'text-accent' : 'text-red-400'}`}>
                      {fmt(surplus)}
                    </span>
                  </div>
                  <p className="text-xs text-muted mt-1">
                    {surplus >= 0
                      ? 'Great! You have money left after expenses.'
                      : 'Warning: You\'re spending more than you earn.'}
                  </p>
                </div>
              </>
            ) : (
              <div className="rounded-card bg-card/50 border border-line border-dashed p-6 text-center">
                <p className="text-2xl mb-2">📊</p>
                <p className="text-sm text-off">Set your income in your Profile to see a budget plan</p>
              </div>
            )}
          </motion.div>
        )}

        {/* DEBT SECTION */}
        {activeSection === 'debt' && (
          <motion.div {...REVEAL} className="space-y-4">
            {debtPlan.length > 0 ? (
              <>
                <div className="rounded-card bg-card border border-line p-5">
                  <h3 className="text-sm font-semibold text-txt mb-1">💳 Debt Avalanche Strategy</h3>
                  <p className="text-xs text-muted mb-4">
                    Pay minimums on all debts, then attack the highest interest rate first.
                    Total debt: <span className="text-red-400 font-bold">{fmt(totalDebt)}</span>
                  </p>

                  <div className="space-y-3">
                    {debtPlan.map((d, i) => (
                      <div key={d.name} className="rounded-lg bg-s1 border border-line p-3">
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2">
                            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                              i === 0 ? 'bg-red-900/50 text-red-400' : 'bg-s2 text-muted'
                            }`}>
                              #{i + 1}
                            </span>
                            <span className="text-sm font-medium text-txt">{d.name}</span>
                          </div>
                          <span className="text-sm font-bold text-off">{fmt(d.balance)}</span>
                        </div>
                        <div className="flex items-center justify-between text-[10px] text-muted">
                          <span>APR: {d.rate}%</span>
                          {i === 0 && <span className="text-red-400 font-medium">← Focus here first!</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-card bg-ghost border border-line p-4">
                  <h4 className="text-xs font-semibold text-accent mb-1">💡 Avalanche Method Tip</h4>
                  <p className="text-xs text-off">
                    By attacking high-interest debt first, you minimize total interest paid.
                    Even an extra $50/month toward #{debtPlan[0]?.name} can save you hundreds in interest!
                  </p>
                </div>
              </>
            ) : (
              <div className="rounded-card bg-accent/10 border border-accent/20 p-6 text-center">
                <p className="text-2xl mb-2">🎉</p>
                <p className="text-sm text-accent font-medium">No debts recorded!</p>
                <p className="text-xs text-muted mt-1">Add debts in your Profile if you have any.</p>
              </div>
            )}
          </motion.div>
        )}

        {/* GOALS SECTION */}
        {activeSection === 'goals' && (
          <motion.div {...REVEAL} className="space-y-4">
            {/* Overall progress */}
            {goals.length > 0 && (
              <div className="rounded-card bg-card border border-line p-5">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-txt">Overall Progress</h3>
                  <span className="text-sm font-bold text-accent">
                    {goals.length} goal{goals.length > 1 ? 's' : ''}
                  </span>
                </div>
                {goals.map((goal) => {
                  const pct = goal.target > 0 ? Math.min(100, (goal.current / goal.target) * 100) : 0;
                  return (
                    <div key={goal.id} className="mb-3 last:mb-0">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span>{goal.emoji}</span>
                          <span className="text-xs font-medium text-off">{goal.title}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted">{fmt(goal.current)} / {fmt(goal.target)}</span>
                          <button onClick={() => removeGoal(goal.id)} className="text-muted hover:text-red-400 text-xs">✕</button>
                        </div>
                      </div>
                      <div className="h-2 rounded-full bg-s2 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${pct}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                          className={`h-full rounded-full ${
                            pct >= 75 ? 'bg-accent' : pct >= 40 ? 'bg-amber-500' : 'bg-accent/60'
                          }`}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Add Goal */}
            <div className="rounded-card bg-card border border-line p-4">
              <h4 className="text-xs font-semibold text-off mb-3">+ Add New Goal</h4>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Goal name..."
                  value={newGoalTitle}
                  onChange={(e) => setNewGoalTitle(e.target.value)}
                  className="flex-1 rounded-lg bg-s2 border border-line px-3 py-2 text-sm text-txt placeholder-muted outline-none focus:ring-2 focus:ring-accent"
                />
                <input
                  type="number"
                  placeholder="$"
                  value={newGoalTarget}
                  onChange={(e) => setNewGoalTarget(e.target.value)}
                  className="w-28 rounded-lg bg-s2 border border-line px-3 py-2 text-sm text-txt placeholder-muted outline-none focus:ring-2 focus:ring-accent"
                />
                <button
                  onClick={addGoal}
                  className="btn-primary !py-2 !px-4 !text-sm"
                >
                  Add
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
