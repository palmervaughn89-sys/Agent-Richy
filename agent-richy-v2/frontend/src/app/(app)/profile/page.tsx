'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TopNav } from '@/components/layout';
import { useFinancialProfileStore } from '@/hooks/useFinancialProfile';
import { EMPLOYMENT_STATUS, RISK_TOLERANCE_OPTIONS, FINANCIAL_GOALS } from '@/lib/constants';
import type { FinancialProfile } from '@/lib/types';

const SESSION = 'default';

const REVEAL = {
  initial: { opacity: 0, y: 30 } as const,
  whileInView: { opacity: 1, y: 0 } as const,
  viewport: { once: true, amount: 0.15 } as const,
  transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] as number[] },
};

function fmt(n: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);
}

// ── Field Section for simple key/value fields ───────────────────────────

function NumberField({ label, value, prefix = '', onChange }: {
  label: string; value: number | undefined; prefix?: string; onChange: (v: number) => void;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-muted mb-1">{label}</label>
      <div className="relative">
        {prefix && (
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-muted">{prefix}</span>
        )}
        <input
          type="number"
          value={value ?? ''}
          onChange={(e) => onChange(e.target.value ? Number(e.target.value) : 0)}
          className={`w-full rounded-lg border border-line bg-s2 py-2 text-sm text-txt
                      focus:ring-2 focus:ring-accent outline-none transition-shadow
                      ${prefix ? 'pl-7 pr-3' : 'px-3'}`}
        />
      </div>
    </div>
  );
}

function SelectField({ label, value, options, onChange }: {
  label: string; value: string | undefined; options: { value: string; label: string }[]; onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-muted mb-1">{label}</label>
      <select
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-line bg-s2 px-3 py-2 text-sm text-txt
                   focus:ring-2 focus:ring-accent outline-none transition-shadow"
      >
        <option value="">Select...</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}

// ── Main Page ───────────────────────────────────────────────────────────

export default function ProfilePage() {
  const { profile, fetchProfile, updateField, isLoading } = useFinancialProfileStore();

  useEffect(() => {
    fetchProfile(SESSION);
  }, [fetchProfile]);

  // Local inputs for debt/goal add forms
  const [newDebtName, setNewDebtName] = useState('');
  const [newDebtBalance, setNewDebtBalance] = useState('');
  const [newDebtRate, setNewDebtRate] = useState('');
  const [newGoal, setNewGoal] = useState('');
  const [saved, setSaved] = useState(false);

  const patch = (update: Partial<FinancialProfile>) => {
    updateField(SESSION, update);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  const addDebt = () => {
    if (!newDebtName.trim() || !newDebtBalance) return;
    const debts = { ...(profile?.debts ?? {}), [newDebtName]: Number(newDebtBalance) };
    const rates = { ...(profile?.debt_interest_rates ?? {}), [newDebtName]: Number(newDebtRate || 0) };
    patch({ debts, debt_interest_rates: rates });
    setNewDebtName('');
    setNewDebtBalance('');
    setNewDebtRate('');
  };

  const removeDebt = (name: string) => {
    const debts = { ...(profile?.debts ?? {}) };
    const rates = { ...(profile?.debt_interest_rates ?? {}) };
    delete debts[name];
    delete rates[name];
    patch({ debts, debt_interest_rates: rates });
  };

  const addGoal = () => {
    if (!newGoal.trim()) return;
    const goals = [...(profile?.goals ?? []), newGoal];
    patch({ goals });
    setNewGoal('');
  };

  const removeGoal = (g: string) => {
    const goals = (profile?.goals ?? []).filter((x) => x !== g);
    patch({ goals });
  };

  const totalDebt = Object.values(profile?.debts ?? {}).reduce((s, v) => s + v, 0);
  const surplus = (profile?.monthly_income ?? 0) - (profile?.monthly_expenses ?? 0);

  const employmentOptions = EMPLOYMENT_STATUS.map((s) => ({ value: s, label: s }));
  const riskOptions = RISK_TOLERANCE_OPTIONS.map((r) => ({ value: r.value, label: r.label }));

  return (
    <div className="flex flex-col h-full">
      <TopNav title="Financial Profile 👤" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6 space-y-6">
        {/* Header */}
        <motion.div {...REVEAL}>
          <p className="section-label">PROFILE</p>
          <h1 className="section-title">
            Your account. <span className="text-muted">Your data.</span>
          </h1>
        </motion.div>

        {/* Save indicator */}
        {saved && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="fixed top-4 right-4 z-50 bg-accent text-black text-xs font-semibold px-3 py-1.5 rounded-lg shadow"
          >
            ✓ Saved
          </motion.div>
        )}

        {/* ── Personal Info ─────────────────────────────────────────── */}
        <motion.section {...REVEAL} className="rounded-card bg-card border border-line p-5">
          <h3 className="text-sm font-semibold text-txt mb-4">👤 Personal Info</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-muted mb-1">Name</label>
              <input
                type="text"
                value={profile?.name ?? ''}
                onChange={(e) => patch({ name: e.target.value })}
                className="w-full rounded-lg border border-line bg-s2 px-3 py-2 text-sm text-txt focus:ring-2 focus:ring-accent outline-none"
              />
            </div>
            <NumberField label="Age" value={profile?.age} onChange={(v) => patch({ age: v })} />
            <SelectField
              label="Employment"
              value={profile?.employment_status}
              options={employmentOptions}
              onChange={(v) => patch({ employment_status: v })}
            />
          </div>
        </motion.section>

        {/* ── Income & Expenses ─────────────────────────────────────── */}
        <motion.section {...REVEAL} className="rounded-card bg-card border border-line p-5">
          <h3 className="text-sm font-semibold text-txt mb-4">💰 Income & Expenses</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <NumberField label="Monthly Income" value={profile?.monthly_income} prefix="$" onChange={(v) => patch({ monthly_income: v })} />
            <NumberField label="Monthly Expenses" value={profile?.monthly_expenses} prefix="$" onChange={(v) => patch({ monthly_expenses: v })} />
          </div>
          <div className={`rounded-lg p-3 ${surplus >= 0 ? 'bg-accent/10 border border-accent/20' : 'bg-red-900/20 border border-red-800/40'}`}>
            <div className="flex justify-between items-center">
              <span className="text-xs text-off">Monthly Surplus</span>
              <span className={`text-sm font-bold ${surplus >= 0 ? 'text-accent' : 'text-red-400'}`}>{fmt(surplus)}</span>
            </div>
          </div>
        </motion.section>

        {/* ── Savings & Emergency ───────────────────────────────────── */}
        <motion.section {...REVEAL} className="rounded-card bg-card border border-line p-5">
          <h3 className="text-sm font-semibold text-txt mb-4">🏦 Savings</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <NumberField label="Savings Balance" value={profile?.savings_balance} prefix="$" onChange={(v) => patch({ savings_balance: v })} />
            <NumberField label="Emergency Fund" value={profile?.emergency_fund} prefix="$" onChange={(v) => patch({ emergency_fund: v })} />
          </div>
          {(profile?.monthly_expenses ?? 0) > 0 && (
            <p className="text-xs text-muted mt-3">
              Emergency fund covers <span className="font-bold text-accent">
                {((profile?.emergency_fund ?? 0) / (profile?.monthly_expenses ?? 1)).toFixed(1)} months
              </span> of expenses (3-6 months recommended)
            </p>
          )}
        </motion.section>

        {/* ── Debts ─────────────────────────────────────────────────── */}
        <motion.section {...REVEAL} className="rounded-card bg-card border border-line p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-txt">💳 Debts</h3>
            {totalDebt > 0 && (
              <span className="text-xs font-bold text-red-400">Total: {fmt(totalDebt)}</span>
            )}
          </div>

          {/* Existing debts */}
          {Object.entries(profile?.debts ?? {}).length > 0 ? (
            <div className="space-y-2 mb-4">
              {Object.entries(profile?.debts ?? {}).map(([name, balance]) => (
                <div key={name} className="flex items-center justify-between rounded-lg bg-s1 border border-line px-3 py-2">
                  <div>
                    <span className="text-sm text-txt font-medium">{name}</span>
                    <span className="text-xs text-muted ml-2">
                      {(profile?.debt_interest_rates?.[name] ?? 0)}% APR
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-off">{fmt(balance)}</span>
                    <button onClick={() => removeDebt(name)} className="text-muted hover:text-red-400 text-xs">✕</button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted mb-4">No debts recorded. 🎉</p>
          )}

          {/* Add debt form */}
          <div className="flex gap-2 flex-wrap">
            <input
              type="text"
              placeholder="Debt name"
              value={newDebtName}
              onChange={(e) => setNewDebtName(e.target.value)}
              className="flex-1 min-w-[120px] rounded-lg bg-s2 border border-line px-3 py-2 text-sm text-txt placeholder-muted outline-none focus:ring-2 focus:ring-accent"
            />
            <input
              type="number"
              placeholder="Balance"
              value={newDebtBalance}
              onChange={(e) => setNewDebtBalance(e.target.value)}
              className="w-28 rounded-lg bg-s2 border border-line px-3 py-2 text-sm text-txt placeholder-muted outline-none focus:ring-2 focus:ring-accent"
            />
            <input
              type="number"
              placeholder="APR %"
              value={newDebtRate}
              onChange={(e) => setNewDebtRate(e.target.value)}
              className="w-20 rounded-lg bg-s2 border border-line px-3 py-2 text-sm text-txt placeholder-muted outline-none focus:ring-2 focus:ring-accent"
            />
            <button
              onClick={addDebt}
              className="btn-primary !py-2 !px-4 !text-sm"
            >
              Add
            </button>
          </div>
        </motion.section>

        {/* ── Credit Score ──────────────────────────────────────────── */}
        <motion.section {...REVEAL} className="rounded-card bg-card border border-line p-5">
          <h3 className="text-sm font-semibold text-txt mb-4">📊 Credit Score</h3>
          <div className="max-w-xs">
            <NumberField label="Score (300-850)" value={profile?.credit_score} onChange={(v) => patch({ credit_score: Math.min(850, Math.max(300, v)) })} />
          </div>
          {profile?.credit_score != null && profile.credit_score > 0 && (
            <div className="mt-3">
              <div className="h-3 rounded-full bg-s2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${((profile.credit_score - 300) / 550) * 100}%` }}
                  transition={{ duration: 0.6 }}
                  className={`h-full rounded-full ${
                    profile.credit_score >= 740 ? 'bg-accent'
                    : profile.credit_score >= 670 ? 'bg-amber-500'
                    : profile.credit_score >= 580 ? 'bg-orange-500'
                    : 'bg-red-500'
                  }`}
                />
              </div>
              <div className="flex justify-between text-[10px] text-muted mt-1">
                <span>300</span>
                <span className={`font-bold ${
                  profile.credit_score >= 740 ? 'text-accent'
                  : profile.credit_score >= 670 ? 'text-amber-400'
                  : profile.credit_score >= 580 ? 'text-orange-400'
                  : 'text-red-400'
                }`}>
                  {profile.credit_score >= 740 ? 'Excellent'
                   : profile.credit_score >= 670 ? 'Good'
                   : profile.credit_score >= 580 ? 'Fair'
                   : 'Poor'}
                </span>
                <span>850</span>
              </div>
            </div>
          )}
        </motion.section>

        {/* ── Goals ─────────────────────────────────────────────────── */}
        <motion.section {...REVEAL} className="rounded-card bg-card border border-line p-5">
          <h3 className="text-sm font-semibold text-txt mb-4">🎯 Financial Goals</h3>

          {(profile?.goals ?? []).length > 0 ? (
            <div className="flex flex-wrap gap-2 mb-4">
              {profile!.goals.map((g) => (
                <span key={g} className="inline-flex items-center gap-1 bg-s1 border border-line rounded-full px-3 py-1 text-xs text-off">
                  {g}
                  <button onClick={() => removeGoal(g)} className="text-muted hover:text-red-400 ml-1">✕</button>
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted mb-4">No goals yet — add some below.</p>
          )}

          {/* Quick pick goals */}
          <p className="text-[10px] text-muted mb-2">Quick add:</p>
          <div className="flex flex-wrap gap-1.5 mb-3">
            {FINANCIAL_GOALS
              .filter((g) => !(profile?.goals ?? []).includes(g))
              .slice(0, 6)
              .map((g) => (
                <button
                  key={g}
                  onClick={() => patch({ goals: [...(profile?.goals ?? []), g] })}
                  className="px-2 py-1 rounded-full bg-s1/50 border border-line/50 text-[10px] text-muted hover:text-accent hover:border-accent/50 transition-colors"
                >
                  + {g}
                </button>
              ))}
          </div>

          {/* Custom goal */}
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Custom goal..."
              value={newGoal}
              onChange={(e) => setNewGoal(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addGoal()}
              className="flex-1 rounded-lg bg-s2 border border-line px-3 py-2 text-sm text-txt placeholder-muted outline-none focus:ring-2 focus:ring-accent"
            />
            <button onClick={addGoal} className="btn-primary !py-2 !px-4 !text-sm">
              Add
            </button>
          </div>
        </motion.section>

        {/* ── Risk Tolerance ────────────────────────────────────────── */}
        <motion.section {...REVEAL} className="rounded-card bg-card border border-line p-5">
          <h3 className="text-sm font-semibold text-txt mb-4">⚖️ Risk Tolerance</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {RISK_TOLERANCE_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => patch({ risk_tolerance: opt.value })}
                className={`rounded-card p-4 border text-left transition-all ${
                  profile?.risk_tolerance === opt.value
                    ? 'bg-accent/10 border-accent ring-1 ring-accent/30'
                    : 'bg-s1 border-line hover:border-line-hover'
                }`}
              >
                <p className={`text-sm font-semibold ${profile?.risk_tolerance === opt.value ? 'text-accent' : 'text-txt'}`}>
                  {opt.label}
                </p>
                <p className="text-[10px] text-muted mt-1">{opt.description}</p>
              </button>
            ))}
          </div>
        </motion.section>
      </div>
    </div>
  );
}
