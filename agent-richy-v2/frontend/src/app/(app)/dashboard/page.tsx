'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { TopNav } from '@/components/layout';
import { AGENTS, AGENT_KEYS } from '@/lib/constants';
import { useProfileStore } from '@/hooks/useFinancialProfile';
import type { AgentKey } from '@/lib/types';

function formatCurrency(n: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);
}

function pct(n: number) {
  return `${(n * 100).toFixed(1)}%`;
}

export default function DashboardPage() {
  const { profile } = useProfileStore();

  const income = profile?.monthly_income ?? 0;
  const expenses = profile?.monthly_expenses ?? 0;
  const savings = profile?.savings_balance ?? 0;
  const emergencyFund = profile?.emergency_fund ?? 0;
  const debts = profile?.debts ?? {};
  const totalDebt = Object.values(debts).reduce((s, v) => s + v, 0);
  const netWorth = savings + emergencyFund - totalDebt;
  const savingsRate = income > 0 ? (income - expenses) / income : 0;
  const dti = income > 0 ? totalDebt / (income * 12) : 0;
  const emergencyMonths = expenses > 0 ? emergencyFund / expenses : 0;
  const hasProfile = profile && income > 0;

  const METRICS = [
    { label: 'Net Worth', value: hasProfile ? formatCurrency(netWorth) : '–', icon: '💰', color: netWorth >= 0 ? 'text-green-500' : 'text-red-500' },
    { label: 'Savings Rate', value: hasProfile ? pct(savingsRate) : '–', icon: '📊', color: savingsRate >= 0.2 ? 'text-green-500' : savingsRate >= 0.1 ? 'text-gold-500' : 'text-red-500' },
    { label: 'Debt-to-Income', value: hasProfile ? pct(dti) : '–', icon: '💳', color: dti <= 0.3 ? 'text-green-500' : dti <= 0.5 ? 'text-gold-500' : 'text-red-500' },
    { label: 'Emergency Fund', value: hasProfile ? `${emergencyMonths.toFixed(1)} mo` : '–', icon: '🛟', color: emergencyMonths >= 6 ? 'text-green-500' : emergencyMonths >= 3 ? 'text-gold-500' : 'text-red-500' },
  ];

  const HEALTH_INDICATORS = [
    { label: 'Budget Health', score: hasProfile ? Math.min(1, savingsRate / 0.2) : 0, tip: savingsRate >= 0.2 ? 'Great! You\'re saving 20%+' : 'Try to save at least 20% of income' },
    { label: 'Debt Health', score: hasProfile ? Math.max(0, 1 - dti / 0.5) : 0, tip: dti <= 0.3 ? 'Healthy debt level' : 'Work on reducing debt-to-income ratio' },
    { label: 'Emergency Ready', score: hasProfile ? Math.min(1, emergencyMonths / 6) : 0, tip: emergencyMonths >= 6 ? 'Fully funded!' : `Target: 6 months (you have ${emergencyMonths.toFixed(1)})` },
    { label: 'Savings Score', score: hasProfile ? Math.min(1, savings / 10000) : 0, tip: savings >= 10000 ? 'Strong savings base' : 'Keep building your savings cushion' },
  ];

  return (
    <div className="flex flex-col h-full">
      <TopNav title="Dashboard" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6 space-y-6">
        {/* Quick stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {METRICS.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              whileHover={{ y: -2 }}
              className="rounded-xl bg-navy-800 border border-navy-700 p-4 shadow-sm"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">{stat.icon}</span>
                <span className={`text-2xl font-bold ${stat.color}`}>{stat.value}</span>
              </div>
              <p className="text-xs text-gray-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Financial Health */}
        {hasProfile && (
          <div className="rounded-xl bg-navy-800 border border-navy-700 p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-white mb-4">📈 Financial Health</h3>
            <div className="space-y-3">
              {HEALTH_INDICATORS.map((ind) => (
                <div key={ind.label}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-gray-300">{ind.label}</span>
                    <span className="text-xs text-gray-400">{(ind.score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-navy-700 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${ind.score * 100}%` }}
                      transition={{ duration: 1, ease: 'easeOut' }}
                      className={`h-full rounded-full ${
                        ind.score >= 0.7 ? 'bg-green-500' : ind.score >= 0.4 ? 'bg-gold-500' : 'bg-red-500'
                      }`}
                    />
                  </div>
                  <p className="text-[10px] text-gray-500 mt-0.5">{ind.tip}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No profile prompt */}
        {!hasProfile && (
          <div className="rounded-xl bg-navy-800/50 border border-navy-700 border-dashed p-6 text-center">
            <p className="text-2xl mb-2">👤</p>
            <p className="text-sm text-gray-300 font-medium mb-1">Set up your profile to see real metrics</p>
            <p className="text-xs text-gray-500 mb-4">We&apos;ll calculate your net worth, savings rate, and financial health score.</p>
            <Link href="/profile" className="inline-block px-5 py-2 rounded-lg bg-gold-500 hover:bg-gold-600 text-white font-semibold text-sm transition-colors">
              Set Up Profile →
            </Link>
          </div>
        )}

        {/* Agents */}
        <div>
          <h3 className="text-sm font-semibold text-gray-200 mb-3">🤖 Your Financial Team</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {AGENT_KEYS.map((key) => {
              const agent = AGENTS[key];
              return (
                <Link key={key} href={`/chat?agent=${key}`}>
                  <motion.div whileHover={{ y: -2, scale: 1.01 }} className="rounded-xl bg-navy-800 border border-navy-700 p-4 shadow-sm hover:border-gold-500/30 transition-colors cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg" style={{ backgroundColor: `${agent.color}20`, border: `1px solid ${agent.color}40` }}>
                        {agent.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-white truncate">{agent.name}</p>
                        <p className="text-[10px] text-gray-400 truncate">{agent.specialty}</p>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-2 italic">&ldquo;{agent.tagline}&rdquo;</p>
                  </motion.div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { href: '/chat', label: 'Start Chat', icon: '💬', desc: 'Talk to an agent' },
            { href: '/kids', label: 'Kids Zone', icon: '🎓', desc: 'Video lessons' },
            { href: '/calculators', label: 'Calculators', icon: '🧮', desc: 'Crunch numbers' },
            { href: '/plan', label: 'My Plan', icon: '🎯', desc: 'Goals & budget' },
          ].map((a) => (
            <Link key={a.href} href={a.href}>
              <motion.div whileHover={{ y: -2 }} className="rounded-xl bg-navy-800 border border-navy-700 p-4 text-center hover:border-gold-500/30 transition-colors cursor-pointer">
                <span className="text-2xl block mb-1">{a.icon}</span>
                <p className="text-xs font-semibold text-white">{a.label}</p>
                <p className="text-[10px] text-gray-500">{a.desc}</p>
              </motion.div>
            </Link>
          ))}
        </div>

        {/* CTA */}
        <div className="rounded-xl bg-gradient-to-r from-gold-500/20 to-gold-600/10 border border-gold-500/30 p-6">
          <h3 className="text-lg font-bold text-white mb-2">🚀 Ready to level up?</h3>
          <p className="text-sm text-gray-300 mb-4">Chat with Coach Richy about your financial situation. He&apos;ll route you to the right specialist automatically.</p>
          <Link href="/chat" className="inline-block px-5 py-2 rounded-lg bg-gold-500 hover:bg-gold-600 text-white font-semibold text-sm shadow-sm transition-colors">
            Open Chat →
          </Link>
        </div>
      </div>
    </div>
  );
}
