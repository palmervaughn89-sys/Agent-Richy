'use client';

import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { TopNav } from '@/components/layout';
import { useProfileStore } from '@/hooks/useFinancialProfile';

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
      needs: { label: 'Needs', amount: income * 0.5, pct: 50, color: 'bg-blue-500', items: 'Housing, groceries, insurance, utilities, transportation' },
      wants: { label: 'Wants', amount: income * 0.3, pct: 30, color: 'bg-gold-500', items: 'Dining, entertainment, subscriptions, shopping' },
      savings: { label: 'Savings & Debt', amount: income * 0.2, pct: 20, color: 'bg-green-500', items: 'Emergency fund, investments, debt payments' },
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
        {/* Tabs */}
        <div className="flex gap-2 flex-wrap">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveSection(t.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${activeSection === t.key
                  ? 'bg-gold-500 text-white shadow-sm'
                  : 'bg-navy-800 text-gray-400 border border-navy-700 hover:text-white'
                }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* BUDGET SECTION */}
        {activeSection === 'budget' && (
          <div className="space-y-4">
            {income > 0 && budget ? (
              <>
                <div className="rounded-xl bg-navy-800 border border-navy-700 p-5">
                  <h3 className="text-sm font-semibold text-white mb-1">50/30/20 Budget Breakdown</h3>
                  <p className="text-xs text-gray-400 mb-4">Based on {fmt(income)}/month income</p>

                  {/* Bar chart */}
                  <div className="flex h-8 rounded-lg overflow-hidden mb-4">
                    {Object.values(budget).map((cat) => (
                      <div
                        key={cat.label}
                        className={`${cat.color} flex items-center justify-center text-[10px] font-bold text-white`}
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
                            <span className="text-sm font-medium text-white">{cat.label}</span>
                          </div>
                          <p className="text-[10px] text-gray-500 ml-5">{cat.items}</p>
                        </div>
                        <span className="text-sm font-bold text-gray-200">{fmt(cat.amount)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Surplus indicator */}
                <div className={`rounded-xl border p-4 ${
                  surplus >= 0
                    ? 'bg-green-900/20 border-green-800/40'
                    : 'bg-red-900/20 border-red-800/40'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-300">Monthly Surplus</span>
                    <span className={`text-lg font-bold ${surplus >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {fmt(surplus)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {surplus >= 0
                      ? 'Great! You have money left after expenses.'
                      : 'Warning: You\'re spending more than you earn.'}
                  </p>
                </div>
              </>
            ) : (
              <div className="rounded-xl bg-navy-800/50 border border-navy-700 border-dashed p-6 text-center">
                <p className="text-2xl mb-2">📊</p>
                <p className="text-sm text-gray-300">Set your income in your Profile to see a budget plan</p>
              </div>
            )}
          </div>
        )}

        {/* DEBT SECTION */}
        {activeSection === 'debt' && (
          <div className="space-y-4">
            {debtPlan.length > 0 ? (
              <>
                <div className="rounded-xl bg-navy-800 border border-navy-700 p-5">
                  <h3 className="text-sm font-semibold text-white mb-1">💳 Debt Avalanche Strategy</h3>
                  <p className="text-xs text-gray-400 mb-4">
                    Pay minimums on all debts, then attack the highest interest rate first.
                    Total debt: <span className="text-red-400 font-bold">{fmt(totalDebt)}</span>
                  </p>

                  <div className="space-y-3">
                    {debtPlan.map((d, i) => (
                      <div key={d.name} className="rounded-lg bg-navy-700/50 border border-navy-600 p-3">
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2">
                            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                              i === 0 ? 'bg-red-900/50 text-red-400' : 'bg-navy-600 text-gray-400'
                            }`}>
                              #{i + 1}
                            </span>
                            <span className="text-sm font-medium text-white">{d.name}</span>
                          </div>
                          <span className="text-sm font-bold text-gray-200">{fmt(d.balance)}</span>
                        </div>
                        <div className="flex items-center justify-between text-[10px] text-gray-500">
                          <span>APR: {d.rate}%</span>
                          {i === 0 && <span className="text-red-400 font-medium">← Focus here first!</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-xl bg-blue-900/20 border border-blue-800/40 p-4">
                  <h4 className="text-xs font-semibold text-blue-300 mb-1">💡 Avalanche Method Tip</h4>
                  <p className="text-xs text-blue-400/80">
                    By attacking high-interest debt first, you minimize total interest paid.
                    Even an extra $50/month toward #{debtPlan[0]?.name} can save you hundreds in interest!
                  </p>
                </div>
              </>
            ) : (
              <div className="rounded-xl bg-green-900/20 border border-green-800/40 p-6 text-center">
                <p className="text-2xl mb-2">🎉</p>
                <p className="text-sm text-green-300 font-medium">No debts recorded!</p>
                <p className="text-xs text-gray-500 mt-1">Add debts in your Profile if you have any.</p>
              </div>
            )}
          </div>
        )}

        {/* GOALS SECTION */}
        {activeSection === 'goals' && (
          <div className="space-y-4">
            {/* Overall progress */}
            {goals.length > 0 && (
              <div className="rounded-xl bg-navy-800 border border-navy-700 p-5">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-white">Overall Progress</h3>
                  <span className="text-sm font-bold text-gold-400">
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
                          <span className="text-xs font-medium text-gray-200">{goal.title}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-400">{fmt(goal.current)} / {fmt(goal.target)}</span>
                          <button onClick={() => removeGoal(goal.id)} className="text-gray-600 hover:text-red-400 text-xs">✕</button>
                        </div>
                      </div>
                      <div className="h-2 rounded-full bg-navy-700 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${pct}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                          className={`h-full rounded-full ${
                            pct >= 75 ? 'bg-green-500' : pct >= 40 ? 'bg-gold-500' : 'bg-blue-500'
                          }`}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Add Goal */}
            <div className="rounded-xl bg-navy-800 border border-navy-700 p-4">
              <h4 className="text-xs font-semibold text-gray-300 mb-3">+ Add New Goal</h4>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Goal name..."
                  value={newGoalTitle}
                  onChange={(e) => setNewGoalTitle(e.target.value)}
                  className="flex-1 rounded-lg bg-navy-700 border border-navy-600 px-3 py-2 text-sm text-white placeholder-gray-500 outline-none focus:ring-2 focus:ring-gold-500"
                />
                <input
                  type="number"
                  placeholder="$"
                  value={newGoalTarget}
                  onChange={(e) => setNewGoalTarget(e.target.value)}
                  className="w-28 rounded-lg bg-navy-700 border border-navy-600 px-3 py-2 text-sm text-white placeholder-gray-500 outline-none focus:ring-2 focus:ring-gold-500"
                />
                <button
                  onClick={addGoal}
                  className="px-4 py-2 rounded-lg bg-gold-500 hover:bg-gold-600 text-white text-sm font-semibold transition-colors"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
