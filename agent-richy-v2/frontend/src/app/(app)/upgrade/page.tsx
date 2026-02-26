'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TopNav } from '@/components/layout';

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    period: '/forever',
    features: [
      'Basic chat with Coach Richy',
      '3 calculator uses/day',
      'Kids Zone (limited)',
      'Community tips',
    ],
    current: true,
  },
  {
    name: 'Pro',
    price: '$9.99',
    period: '/month',
    features: [
      'All 6 specialist agents',
      'Unlimited calculators',
      'Full Kids Zone + quizzes',
      'Portfolio builder',
      'Smart charts & evidence',
      'Priority responses',
    ],
    highlighted: true,
  },
  {
    name: 'Family',
    price: '$14.99',
    period: '/month',
    features: [
      'Everything in Pro',
      'Up to 5 family members',
      'Kid progress tracking',
      'Family financial dashboard',
      'Shared goals',
      'Video lessons',
    ],
  },
];

export default function UpgradePage() {
  return (
    <div className="flex flex-col h-full">
      <TopNav title="Upgrade ⭐" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-10"
        >
          <p className="section-label">UPGRADE</p>
          <h1 className="section-title">
            Unlock everything. <span className="text-muted">Go Pro.</span>
          </h1>
          <p className="text-sm text-off mt-2">
            Unlock all agents, unlimited calculators, and premium features.
          </p>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {PLANS.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: i * 0.1 }}
              whileHover={{ y: -4 }}
              className={`rounded-card p-6 ${
                plan.highlighted
                  ? 'bg-ghost border-2 border-accent/40 ring-1 ring-accent/20'
                  : 'bg-card border border-line'
              }`}
            >
              {plan.highlighted && (
                <span className="badge-pill mb-3">
                  Most Popular
                </span>
              )}

              <h3 className="text-lg font-bold text-txt">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mt-2">
                <span className="text-3xl font-bold text-txt">
                  {plan.price}
                </span>
                <span className="text-sm text-muted">{plan.period}</span>
              </div>

              <ul className="mt-5 space-y-2">
                {plan.features.map((feat) => (
                  <li key={feat} className="flex items-center gap-2 text-sm text-off">
                    <span className="text-accent">✓</span>
                    {feat}
                  </li>
                ))}
              </ul>

              <button
                className={`w-full mt-6 ${
                  plan.current
                    ? 'py-2.5 rounded-lg text-sm font-semibold bg-s2 text-muted cursor-default'
                    : plan.highlighted
                    ? 'btn-primary'
                    : 'btn-secondary'
                }`}
                disabled={plan.current}
              >
                {plan.current ? 'Current Plan' : `Get ${plan.name}`}
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
