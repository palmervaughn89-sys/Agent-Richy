'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { TopNav } from '@/components/layout';
import { FinancialChart } from '@/components/charts';
import * as api from '@/lib/api';
import type { ChartConfig } from '@/lib/types';

interface CalculatorDef {
  id: string;
  label: string;
  emoji: string;
  fields: { key: string; label: string; prefix?: string; suffix?: string; default?: number }[];
  apiCall: (params: Record<string, number>) => Promise<any>;
}

const CALCULATORS: CalculatorDef[] = [
  {
    id: 'compound',
    label: 'Compound Interest',
    emoji: '📈',
    fields: [
      { key: 'principal', label: 'Starting Amount', prefix: '$', default: 1000 },
      { key: 'monthly_contribution', label: 'Monthly Contribution', prefix: '$', default: 200 },
      { key: 'annual_rate', label: 'Annual Rate', suffix: '%', default: 7 },
      { key: 'years', label: 'Years', default: 10 },
    ],
    apiCall: (p) => api.calcCompoundInterest({ principal: p.principal, monthly_contribution: p.monthly_contribution, annual_rate: p.annual_rate, years: p.years }),
  },
  {
    id: 'budget',
    label: '50/30/20 Budget',
    emoji: '💰',
    fields: [
      { key: 'monthly_income', label: 'Monthly Income', prefix: '$', default: 5000 },
    ],
    apiCall: (p) => api.calcBudget({ monthly_income: p.monthly_income }),
  },
  {
    id: 'emergency',
    label: 'Emergency Fund',
    emoji: '🛟',
    fields: [
      { key: 'monthly_expenses', label: 'Monthly Expenses', prefix: '$', default: 3000 },
      { key: 'current_savings', label: 'Current Savings', prefix: '$', default: 2000 },
    ],
    apiCall: (p) => api.calcEmergencyFund({ monthly_expenses: p.monthly_expenses, current_savings: p.current_savings }),
  },
  {
    id: 'savings_goal',
    label: 'Savings Timeline',
    emoji: '🎯',
    fields: [
      { key: 'goal_amount', label: 'Goal Amount', prefix: '$', default: 10000 },
      { key: 'monthly_contribution', label: 'Monthly Contribution', prefix: '$', default: 500 },
      { key: 'current_savings', label: 'Starting Amount', prefix: '$', default: 0 },
    ],
    apiCall: (p) => api.calcSavingsGoal({ goal_amount: p.goal_amount, monthly_contribution: p.monthly_contribution, current_savings: p.current_savings }),
  },
  {
    id: 'debt_payoff',
    label: 'Debt Payoff',
    emoji: '💳',
    fields: [
      { key: 'balance', label: 'Balance Owed', prefix: '$', default: 5000 },
      { key: 'apr', label: 'Interest Rate (APR)', suffix: '%', default: 18 },
      { key: 'monthly_payment', label: 'Monthly Payment', prefix: '$', default: 200 },
    ],
    apiCall: (p) => api.calcDebtPayoff({ balance: p.balance, apr: p.apr, monthly_payment: p.monthly_payment }),
  },
];

export default function CalculatorsPage() {
  const [activeCalc, setActiveCalc] = useState<string>(CALCULATORS[0].id);
  const [values, setValues] = useState<Record<string, Record<string, number>>>({});
  const [result, setResult] = useState<any>(null);
  const [charts, setCharts] = useState<ChartConfig[]>([]);
  const [loading, setLoading] = useState(false);

  const calc = CALCULATORS.find((c) => c.id === activeCalc)!;

  const getVal = (key: string) => values[activeCalc]?.[key] ?? calc.fields.find((f) => f.key === key)?.default ?? 0;

  const setVal = (key: string, v: number) => {
    setValues((prev) => ({
      ...prev,
      [activeCalc]: { ...prev[activeCalc], [key]: v },
    }));
  };

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const params: Record<string, number> = {};
      calc.fields.forEach((f) => { params[f.key] = getVal(f.key); });
      const res = await calc.apiCall(params);
      // Backend returns charts as an array, strip it from display result
      const { charts: resCharts, ...rest } = res;
      setResult(rest);
      setCharts(resCharts ?? []);
    } catch {
      setResult({ error: 'Calculation failed. Is the backend running?' });
      setCharts([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <TopNav title="Calculators 🧮" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6">
        {/* Calculator tabs */}
        <div className="flex flex-wrap gap-2 mb-6">
          {CALCULATORS.map((c) => (
            <button
              key={c.id}
              onClick={() => { setActiveCalc(c.id); setResult(null); setCharts([]); }}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors
                ${
                  activeCalc === c.id
                    ? 'bg-gold-500 text-white shadow-sm'
                    : 'bg-navy-800 border border-navy-700 text-gray-400 hover:text-white'
                }`}
            >
              {c.emoji} {c.label}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Inputs */}
          <div className="rounded-xl bg-navy-800 border border-navy-700 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-white">
              {calc.emoji} {calc.label}
            </h3>

            {calc.fields.map((field) => (
              <div key={field.key}>
                <label className="block text-xs font-medium text-gray-400 mb-1">
                  {field.label}
                </label>
                <div className="relative">
                  {field.prefix && (
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">
                      {field.prefix}
                    </span>
                  )}
                  <input
                    type="number"
                    value={getVal(field.key)}
                    onChange={(e) => setVal(field.key, Number(e.target.value))}
                    className={`w-full rounded-lg border border-navy-600
                                bg-navy-700 py-2 text-sm text-white outline-none
                                focus:ring-2 focus:ring-gold-500 focus:border-transparent
                                ${field.prefix ? 'pl-7' : 'pl-3'} ${field.suffix ? 'pr-8' : 'pr-3'}`}
                  />
                  {field.suffix && (
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">
                      {field.suffix}
                    </span>
                  )}
                </div>
              </div>
            ))}

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleCalculate}
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-white
                         font-semibold text-sm shadow-sm disabled:opacity-50 transition-colors"
            >
              {loading ? 'Calculating...' : 'Calculate'}
            </motion.button>
          </div>

          {/* Results */}
          <div className="space-y-4">
            {charts.map((c, i) => (
              <div key={i} className="rounded-xl bg-navy-800 border border-navy-700 p-5">
                {c.title && (
                  <h4 className="text-sm font-semibold text-gray-200 mb-3">
                    📊 {c.title}
                  </h4>
                )}
                <FinancialChart config={c} />
              </div>
            ))}

            {result && (
              <div className="rounded-xl bg-navy-800 border border-navy-700 p-5">
                <h4 className="text-sm font-semibold text-gray-200 mb-2">
                  Results
                </h4>
                <pre className="text-xs text-gray-400 whitespace-pre-wrap">
                  {typeof result === 'string' ? result : JSON.stringify(result, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
