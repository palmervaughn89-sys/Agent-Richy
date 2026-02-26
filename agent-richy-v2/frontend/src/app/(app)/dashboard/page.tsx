'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { TopNav } from '@/components/layout';
import {
  PieChart, Pie, Cell, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Wallet,
  PiggyBank,
  MessageSquare,
  BarChart3,
  Calendar,
  Search,
  Lightbulb,
  AlertTriangle,
  ShieldCheck,
} from 'lucide-react';

/* ── Demo Data ───────────────────────────────────────────────────────── */
const DEMO_INCOME = 4500;
const DEMO_EXPENSES = 3200;
const DEMO_NET = DEMO_INCOME - DEMO_EXPENSES;
const DEMO_SAVINGS_RATE = ((DEMO_NET / DEMO_INCOME) * 100).toFixed(1);

const SPENDING_DATA = [
  { name: 'Housing', value: 35, color: '#00E87B' },
  { name: 'Food', value: 20, color: '#00C968' },
  { name: 'Transport', value: 15, color: '#F59E0B' },
  { name: 'Entertainment', value: 10, color: '#8B5CF6' },
  { name: 'Subscriptions', value: 8, color: '#EF4444' },
  { name: 'Other', value: 12, color: '#5E736A' },
];

const SAVINGS_TREND = [
  { month: 'Sep', amount: 800 },
  { month: 'Oct', amount: 950 },
  { month: 'Nov', amount: 1100 },
  { month: 'Dec', amount: 1050 },
  { month: 'Jan', amount: 1200 },
  { month: 'Feb', amount: 1300 },
];

const HEALTH_SCORE = 72;

const INSIGHTS = [
  {
    icon: AlertTriangle,
    color: 'text-amber-400',
    text: 'You spent $47 more on food this month. Here\'s how to fix that.',
  },
  {
    icon: ShieldCheck,
    color: 'text-accent',
    text: 'Your car insurance renews next month. Time to compare rates.',
  },
  {
    icon: Lightbulb,
    color: 'text-accent',
    text: 'You have 3 unused subscriptions totaling $34/month.',
  },
];

function fmt(n: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);
}

/* ── Health Score Ring ────────────────────────────────────────────────── */
function HealthRing({ score }: { score: number }) {
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;
  const color = score > 70 ? '#00E87B' : score >= 40 ? '#F59E0B' : '#EF4444';
  return (
    <div className="relative w-36 h-36 mx-auto">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,.06)" strokeWidth="10" />
        <motion.circle
          cx="60" cy="60" r="54" fill="none" stroke={color} strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-txt">{score}</span>
        <span className="text-xs text-txt-muted">/ 100</span>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <div className="flex flex-col h-full">
      <TopNav title="Dashboard" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6 space-y-6">
        {/* Section label */}
        <div>
          <p className="section-label">DASHBOARD</p>
          <h2 className="text-2xl font-extrabold text-txt tracking-tight">
            Your Financial Overview
          </h2>
        </div>

        {/* ── ROW 1: Key metrics ─────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.15 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="grid grid-cols-1 sm:grid-cols-3 gap-4"
        >
          {[
            {
              label: 'Monthly Income',
              value: fmt(DEMO_INCOME),
              icon: DollarSign,
              change: '+3% vs last month',
              changeColor: 'text-accent',
              changeIcon: TrendingUp,
            },
            {
              label: 'Monthly Expenses',
              value: fmt(DEMO_EXPENSES),
              icon: Wallet,
              change: 'Across 6 categories',
              changeColor: 'text-txt-muted',
              changeIcon: BarChart3,
            },
            {
              label: 'Net Savings',
              value: fmt(DEMO_NET),
              icon: PiggyBank,
              change: `${DEMO_SAVINGS_RATE}% savings rate`,
              changeColor: 'text-accent',
              changeIcon: TrendingUp,
            },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="rounded-card bg-card border border-line p-5 hover:border-line-hover transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <stat.icon className="w-5 h-5 text-txt-muted" />
                <div className={`flex items-center gap-1 text-xs ${stat.changeColor}`}>
                  <stat.changeIcon className="w-3 h-3" />
                  <span>{stat.change}</span>
                </div>
              </div>
              <p className="text-2xl font-bold text-txt">{stat.value}</p>
              <p className="text-xs text-txt-muted mt-1">{stat.label}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* ── ROW 2: Charts ──────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.15 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-4"
        >
          {/* Spending Breakdown */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.15 }}
            className="rounded-card bg-card border border-line p-5"
          >
            <h3 className="text-sm font-semibold text-txt mb-4">Spending Breakdown</h3>
            <div className="flex flex-col sm:flex-row items-center gap-6">
              <div className="w-40 h-40 flex-shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={SPENDING_DATA}
                      cx="50%"
                      cy="50%"
                      innerRadius={35}
                      outerRadius={65}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {SPENDING_DATA.map((entry) => (
                        <Cell key={entry.name} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 flex-1">
                {SPENDING_DATA.map((cat) => (
                  <div key={cat.name} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cat.color }} />
                      <span className="text-txt-off">{cat.name}</span>
                    </div>
                    <span className="text-txt-muted font-medium">{cat.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Savings Trend */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="rounded-card bg-card border border-line p-5"
          >
            <h3 className="text-sm font-semibold text-txt mb-4">Savings Trend (6 months)</h3>
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={SAVINGS_TREND}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.06)" />
                  <XAxis dataKey="month" tick={{ fill: '#B8C9C0', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#B8C9C0', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v}`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#101A15', border: '1px solid rgba(255,255,255,.06)', borderRadius: '14px', fontSize: '12px', color: '#F2F8F5' }}
                    labelStyle={{ color: '#B8C9C0' }}
                    formatter={(value: number) => [`$${value}`, 'Saved']}
                  />
                  <Line type="monotone" dataKey="amount" stroke="#00E87B" strokeWidth={2.5} dot={{ fill: '#00E87B', strokeWidth: 0, r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </motion.div>

        {/* ── ROW 3: Health Score + Quick Actions ────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.15 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-4"
        >
          {/* Financial Health Score */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.25 }}
            className="rounded-card bg-card border border-line p-5 text-center"
          >
            <h3 className="text-sm font-semibold text-txt mb-4">Financial Health Score</h3>
            <HealthRing score={HEALTH_SCORE} />
            <p className="text-xs text-txt-off mt-3">
              {HEALTH_SCORE > 70 ? 'Great job! You\'re on a solid path.' : HEALTH_SCORE >= 40 ? 'Room for improvement — let Richy help.' : 'Let\'s make a plan to improve this.'}
            </p>
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="rounded-card bg-card border border-line p-5"
          >
            <h3 className="text-sm font-semibold text-txt mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'Chat with Richy', icon: MessageSquare, href: '/chat', color: 'bg-ghost text-accent border-line' },
                { label: 'Run Budget Analysis', icon: BarChart3, href: '/calculators', color: 'bg-ghost text-accent border-line' },
                { label: 'Check Tax Calendar', icon: Calendar, href: '/plan', color: 'bg-ghost text-amber-400 border-line' },
                { label: 'Find Savings', icon: Search, href: '/chat?agent=savings_sage', color: 'bg-ghost text-accent border-line' },
              ].map((action) => (
                <Link key={action.label} href={action.href}>
                  <div className={`flex items-center gap-3 rounded-card border p-4 hover:border-line-hover hover:scale-[1.02] transition-all cursor-pointer ${action.color}`}>
                    <action.icon className="w-5 h-5 flex-shrink-0" />
                    <span className="text-xs font-medium">{action.label}</span>
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>
        </motion.div>

        {/* ── ROW 4: Recent Insights ─────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.15 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="rounded-card bg-card border border-line p-5"
        >
          <h3 className="text-sm font-semibold text-txt mb-4">Recent Insights from Richy</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {INSIGHTS.map((insight, i) => (
              <div key={i} className="rounded-card bg-s1 border border-line p-4 hover:border-line-hover transition-colors">
                <insight.icon className={`w-5 h-5 ${insight.color} mb-2`} />
                <p className="text-xs text-txt-off leading-relaxed">{insight.text}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
