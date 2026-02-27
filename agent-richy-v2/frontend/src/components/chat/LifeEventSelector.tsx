'use client';

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { LifeEventType } from '@/lib/financialTwin';
import { LIFE_EVENT_TEMPLATES } from '@/lib/financialTwin';

/* ── Category groupings ────────────────────────────────────────────── */

interface EventGroup {
  label: string;
  emoji: string;
  types: LifeEventType[];
}

const CATEGORIES: EventGroup[] = [
  {
    label: 'Career',
    emoji: '💼',
    types: ['job_change', 'raise', 'job_loss', 'career_switch', 'start_business', 'side_hustle', 'freelance'],
  },
  {
    label: 'Housing',
    emoji: '🏠',
    types: ['move_city', 'move_state', 'buy_home', 'sell_home', 'downsize'],
  },
  {
    label: 'Family',
    emoji: '👨‍👩‍👧',
    types: ['marriage', 'divorce', 'baby', 'child_college'],
  },
  {
    label: 'Transportation',
    emoji: '🚗',
    types: ['car_purchase', 'car_payoff', 'go_carless'],
  },
  {
    label: 'Financial',
    emoji: '💰',
    types: ['debt_payoff', 'take_loan', 'refinance', 'inheritance', 'windfall', 'lawsuit'],
  },
  {
    label: 'Life Events',
    emoji: '🩺',
    types: ['health_event', 'disability'],
  },
  {
    label: 'Retirement',
    emoji: '🏖️',
    types: ['retirement', 'early_retirement', 'semi_retirement'],
  },
  {
    label: 'Education',
    emoji: '🎓',
    types: ['education', 'certification', 'grad_school'],
  },
  {
    label: 'Other',
    emoji: '✨',
    types: ['custom'],
  },
];

/* ── Component ─────────────────────────────────────────────────────── */

interface Props {
  onSelect: (event: LifeEventType) => void;
}

export default function LifeEventSelector({ onSelect }: Props) {
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  /* Filtered categories based on search */
  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    if (!q) return CATEGORIES;

    return CATEGORIES
      .map((cat) => ({
        ...cat,
        types: cat.types.filter((t) => {
          const template = LIFE_EVENT_TEMPLATES[t];
          return (
            template.name.toLowerCase().includes(q) ||
            t.replace(/_/g, ' ').includes(q) ||
            cat.label.toLowerCase().includes(q)
          );
        }),
      }))
      .filter((cat) => cat.types.length > 0);
  }, [search]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="bg-card border border-line rounded-card p-5 w-full"
    >
      {/* ── Header ─────────────────────────────────────────────────── */}
      <p className="font-mono text-accent text-xs tracking-widest">FINANCIAL TWIN</p>
      <h3 className="text-txt text-xl font-bold mt-1">What life event do you want to simulate?</h3>
      <p className="text-off text-sm mt-1">
        Pick an event and Richy will show you the full financial ripple effects.
      </p>

      {/* ── Search ─────────────────────────────────────────────────── */}
      <div className="mt-4 relative">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search events..."
          className="w-full bg-s1 border border-line rounded-lg px-4 py-2.5 text-sm text-txt placeholder:text-muted focus:outline-none focus:border-accent/40 transition-colors"
        />
        {search && (
          <button
            onClick={() => setSearch('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-txt text-sm"
          >
            ✕
          </button>
        )}
      </div>

      {/* ── Category pills ─────────────────────────────────────────── */}
      <div className="flex flex-wrap gap-2 mt-4">
        <button
          onClick={() => setActiveCategory(null)}
          className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
            activeCategory === null
              ? 'bg-accent/10 border-accent/30 text-accent'
              : 'border-line text-muted hover:border-accent/20 hover:text-off'
          }`}
        >
          All
        </button>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.label}
            onClick={() => setActiveCategory(activeCategory === cat.label ? null : cat.label)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
              activeCategory === cat.label
                ? 'bg-accent/10 border-accent/30 text-accent'
                : 'border-line text-muted hover:border-accent/20 hover:text-off'
            }`}
          >
            {cat.emoji} {cat.label}
          </button>
        ))}
      </div>

      {/* ── Event Grid ─────────────────────────────────────────────── */}
      <div className="mt-5 space-y-5">
        <AnimatePresence mode="wait">
          {filtered
            .filter((cat) => !activeCategory || cat.label === activeCategory)
            .map((cat) => (
              <motion.div
                key={cat.label}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.3 }}
              >
                <p className="text-off text-xs font-medium mb-2 flex items-center gap-1.5">
                  <span>{cat.emoji}</span> {cat.label}
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {cat.types.map((type) => {
                    const template = LIFE_EVENT_TEMPLATES[type];
                    const hasCosts = template.typicalCosts.length > 0;
                    const hasEffects = template.cascadingEffects.length > 0;

                    return (
                      <motion.button
                        key={type}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => onSelect(type)}
                        className="bg-card border border-line rounded-card p-4 text-left hover:border-accent/30 transition-colors cursor-pointer group"
                      >
                        <p className="text-txt text-sm font-medium group-hover:text-accent transition-colors leading-tight">
                          {template.name}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          {hasCosts && (
                            <span className="text-[9px] font-mono text-muted bg-s2 rounded px-1.5 py-0.5">
                              {template.typicalCosts.length} costs
                            </span>
                          )}
                          {hasEffects && (
                            <span className="text-[9px] font-mono text-muted bg-s2 rounded px-1.5 py-0.5">
                              {template.cascadingEffects.length} effects
                            </span>
                          )}
                          {template.questionsToAsk.length > 0 && (
                            <span className="text-[9px] font-mono text-accent/60 bg-accent/5 rounded px-1.5 py-0.5">
                              guided
                            </span>
                          )}
                        </div>
                      </motion.button>
                    );
                  })}
                </div>
              </motion.div>
            ))}
        </AnimatePresence>

        {filtered.length === 0 && (
          <div className="text-center py-8">
            <p className="text-muted text-sm">No events match &quot;{search}&quot;</p>
            <button
              onClick={() => setSearch('')}
              className="text-accent text-sm mt-2 hover:underline"
            >
              Clear search
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
}
