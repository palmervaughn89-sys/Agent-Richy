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
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-navy-800 dark:text-white">
            Level Up Your Financial Game
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Unlock all agents, unlimited calculators, and premium features.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {PLANS.map((plan) => (
            <motion.div
              key={plan.name}
              whileHover={{ y: -4 }}
              className={`rounded-xl p-6 shadow-sm ${
                plan.highlighted
                  ? 'bg-gradient-to-b from-gold-50 to-white dark:from-gold-900/20 dark:to-navy-800 border-2 border-gold-400 ring-2 ring-gold-200 dark:ring-gold-800'
                  : 'bg-white dark:bg-navy-800 border border-gray-200 dark:border-navy-700'
              }`}
            >
              {plan.highlighted && (
                <span className="inline-block text-[10px] font-bold uppercase tracking-wider
                                 text-gold-600 bg-gold-100 dark:bg-gold-900/40 px-2 py-0.5
                                 rounded-full mb-3">
                  Most Popular
                </span>
              )}

              <h3 className="text-lg font-bold text-navy-800 dark:text-white">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mt-2">
                <span className="text-3xl font-bold text-navy-800 dark:text-white">
                  {plan.price}
                </span>
                <span className="text-sm text-gray-400">{plan.period}</span>
              </div>

              <ul className="mt-5 space-y-2">
                {plan.features.map((feat) => (
                  <li key={feat} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                    <span className="text-green-500">✓</span>
                    {feat}
                  </li>
                ))}
              </ul>

              <button
                className={`w-full mt-6 py-2.5 rounded-lg text-sm font-semibold transition-colors
                  ${
                    plan.current
                      ? 'bg-gray-100 dark:bg-navy-700 text-gray-400 cursor-default'
                      : plan.highlighted
                      ? 'bg-gold-500 hover:bg-gold-600 text-white shadow-md'
                      : 'bg-navy-800 dark:bg-navy-600 hover:bg-navy-700 text-white'
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
