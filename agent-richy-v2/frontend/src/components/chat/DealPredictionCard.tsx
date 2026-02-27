'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { DealPrediction } from '@/types/economicIntel';

/* ── Animation ─────────────────────────────────────────────────────── */

const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
};

const collapse = {
  initial: { height: 0, opacity: 0 },
  animate: { height: 'auto', opacity: 1, transition: { duration: 0.25, ease: 'easeOut' } },
  exit: { height: 0, opacity: 0, transition: { duration: 0.2, ease: 'easeIn' } },
};

/* ── Helpers ───────────────────────────────────────────────────────── */

function ConfidenceBadge({ level }: { level: 'high' | 'medium' | 'low' }) {
  const styles: Record<string, string> = {
    high: 'text-accent bg-accent/10 border-accent/20',
    medium: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    low: 'text-muted bg-white/5 border-white/10',
  };
  return (
    <span className={`text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full border ${styles[level]}`}>
      {level} confidence
    </span>
  );
}

function ActionDisplay({ action }: { action: string }) {
  const map: Record<string, { label: string; cls: string }> = {
    wait: { label: 'WAIT TO BUY', cls: 'text-amber-400' },
    buy_now: { label: 'BUY NOW', cls: 'text-accent' },
    stock_up: { label: 'STOCK UP', cls: 'text-accent' },
    watch: { label: 'WATCH & WAIT', cls: 'text-blue-400' },
    lock_in: { label: 'LOCK IN NOW', cls: 'text-emerald-400' },
  };
  const { label, cls } = map[action] ?? { label: action.toUpperCase(), cls: 'text-muted' };
  return <span className={`font-mono text-2xl font-bold ${cls}`}>{label}</span>;
}

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      width="14" height="14" viewBox="0 0 16 16" fill="none"
      className={`text-muted transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
    >
      <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/* ── Reasoning Step ────────────────────────────────────────────────── */

function ReasoningStep({ step, isLast }: {
  step: { dataPoint: string; source: string; implication: string };
  isLast: boolean;
}) {
  return (
    <div className="relative pl-6">
      {/* Connector dot + line */}
      <div className="absolute left-0 top-1 flex flex-col items-center">
        <div className="w-2.5 h-2.5 rounded-full bg-accent/50 border border-accent/30" />
        {!isLast && <div className="w-px flex-1 bg-accent/15 mt-0.5" style={{ minHeight: '2rem' }} />}
      </div>

      <div className="pb-4">
        <p className="text-txt text-sm leading-snug">{step.dataPoint}</p>
        <p className="text-muted text-[10px] font-mono mt-0.5">{step.source}</p>
        <p className="text-off text-sm italic mt-1">→ {step.implication}</p>
      </div>
    </div>
  );
}

/* ── Main Component ────────────────────────────────────────────────── */

interface DealPredictionCardProps {
  prediction: DealPrediction;
}

export default function DealPredictionCard({ prediction }: DealPredictionCardProps) {
  const [showReasoning, setShowReasoning] = useState(false);

  return (
    <motion.div
      variants={fadeUp}
      initial="hidden"
      animate="show"
      className="bg-card border border-line rounded-[14px] overflow-hidden"
    >
      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="p-4 border-b border-line flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-txt font-semibold text-sm">{prediction.category}</p>
          <p className="text-off text-xs mt-0.5 leading-relaxed">{prediction.prediction}</p>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          <ConfidenceBadge level={prediction.confidence} />
          <span className="text-muted text-[10px] font-mono">{prediction.timeframe}</span>
        </div>
      </div>

      {/* ── Action ─────────────────────────────────────────────── */}
      <div className="bg-s1 p-4">
        <ActionDisplay action={prediction.action} />
        <p className="text-off text-sm mt-2">{prediction.actionDescription}</p>
        <p className="text-accent font-medium text-sm mt-2">💰 {prediction.potentialSavings}</p>
      </div>

      {/* ── Reasoning Chain ────────────────────────────────────── */}
      {prediction.reasoning.length > 0 && (
        <div className="border-t border-line">
          <button
            onClick={() => setShowReasoning(!showReasoning)}
            className="w-full flex items-center justify-between px-4 py-3 hover:bg-s1/50 transition-colors"
          >
            <span className="text-off text-xs font-medium">Why? — See the reasoning chain</span>
            <Chevron open={showReasoning} />
          </button>
          <AnimatePresence>
            {showReasoning && (
              <motion.div {...collapse} className="overflow-hidden">
                <div className="px-4 pb-4">
                  {prediction.reasoning.map((step, i) => (
                    <ReasoningStep
                      key={i}
                      step={step}
                      isLast={i === prediction.reasoning.length - 1}
                    />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* ── Affected Products ──────────────────────────────────── */}
      {prediction.affectedProducts.length > 0 && (
        <div className="flex gap-2 flex-wrap p-4 border-t border-line">
          {prediction.affectedProducts.map((product) => (
            <span
              key={product}
              className="text-xs text-off bg-white/5 border border-white/10 rounded-full px-3 py-1"
            >
              {product}
            </span>
          ))}
        </div>
      )}

      {/* ── Risk ───────────────────────────────────────────────── */}
      {prediction.riskOfAction && (
        <div className="px-4 pb-4">
          <p className="text-muted text-xs">
            ⚠️ Risk: {prediction.riskOfAction}
          </p>
        </div>
      )}
    </motion.div>
  );
}
