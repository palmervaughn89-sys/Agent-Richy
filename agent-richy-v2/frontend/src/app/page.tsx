'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { RichyAvatar } from '@/components/avatar';

const FEATURES = [
  { icon: '💬', title: 'AI Chat Coaching', desc: '6 specialist agents for every financial topic' },
  { icon: '📊', title: 'Smart Charts', desc: 'Interactive visualizations powered by your data' },
  { icon: '🎓', title: 'Kids Zone', desc: 'Age-appropriate financial education with videos & quizzes' },
  { icon: '🧮', title: 'Calculators', desc: 'Compound interest, debt payoff, budgeting, and more' },
  { icon: '🎯', title: 'Goal Planning', desc: 'Track milestones and hit your financial targets' },
  { icon: '🤖', title: 'Smart Avatar', desc: 'Richy watches you type and reacts in real time' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-navy-900 via-navy-800 to-navy-950">
      {/* Hero */}
      <header className="relative overflow-hidden">
        <div className="max-w-5xl mx-auto px-6 py-20 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex flex-col items-center"
          >
            <RichyAvatar size="lg" />

            <h1 className="mt-8 text-4xl md:text-6xl font-bold text-white tracking-tight">
              Meet <span className="text-gold-400">Agent Richy</span>
            </h1>

            <p className="mt-4 text-lg md:text-xl text-gray-300 max-w-2xl">
              Your AI-powered financial coach. Get personalized advice on budgeting,
              investing, debt, and more — with an interactive avatar that watches
              you type and reacts in real time.
            </p>

            <div className="mt-8 flex gap-4">
              <Link href="/chat">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-3 rounded-xl bg-gold-500 hover:bg-gold-600 text-white
                             font-semibold shadow-lg shadow-gold-500/30 transition-colors"
                >
                  Start Chatting
                </motion.button>
              </Link>
              <Link href="/dashboard">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-3 rounded-xl border border-gray-600 text-gray-300
                             hover:bg-navy-700 font-medium transition-colors"
                >
                  View Dashboard
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>

        {/* Background orbs */}
        <div className="absolute top-10 left-10 w-72 h-72 bg-gold-400/10 rounded-full blur-3xl" />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
      </header>

      {/* Features grid */}
      <section className="max-w-5xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-white text-center mb-10">
          Everything you need to level up your finances
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map((feat, i) => (
            <motion.div
              key={feat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="rounded-xl bg-navy-800/60 border border-navy-700 p-6
                         hover:border-gold-500/40 transition-colors"
            >
              <span className="text-3xl">{feat.icon}</span>
              <h3 className="mt-3 text-base font-semibold text-white">{feat.title}</h3>
              <p className="mt-1 text-sm text-gray-400">{feat.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA footer */}
      <section className="text-center pb-20">
        <p className="text-gray-500 text-sm">
          Built with Next.js, FastAPI, and a whole lot of financial wisdom.
        </p>
      </section>
    </div>
  );
}
