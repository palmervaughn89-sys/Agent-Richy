'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { StructuredResponse, ChartConfig } from '@/lib/types';
import FinancialChart from '@/components/charts/FinancialChart';
import EvidenceCard from '@/components/evidence/EvidenceCard';

interface Props {
  data: StructuredResponse;
}

/** Renders structured content blocks: charts, evidence, examples, time_horizon */
export default function ResponseRenderer({ data }: Props) {
  const { charts, evidence, examples, time_horizon, calculator_result } = data;

  const hasExtra =
    (charts && charts.length > 0) ||
    (evidence && evidence.length > 0) ||
    (examples && examples.length > 0) ||
    time_horizon ||
    calculator_result;

  if (!hasExtra) return null;

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      className="mt-3 space-y-4"
    >
      {/* Charts */}
      {charts && charts.length > 0 && (
        <div className="space-y-3">
          {charts.map((chart: ChartConfig, i: number) => (
            <div key={i} className="rounded-card border border-line bg-card p-4">
              {chart.title && (
                <h4 className="text-sm font-semibold text-txt mb-2">
                  📊 {chart.title}
                </h4>
              )}
              <FinancialChart config={chart} />
            </div>
          ))}
        </div>
      )}

      {/* Calculator result summary */}
      {calculator_result && (
        <div className="rounded-card bg-accent/10 border border-accent/20 p-4">
          <h4 className="text-sm font-semibold text-accent mb-2">
            🧮 Calculator Result
          </h4>
          <pre className="text-xs text-accent/80 whitespace-pre-wrap">
            {typeof calculator_result === 'string'
              ? calculator_result
              : JSON.stringify(calculator_result, null, 2)}
          </pre>
        </div>
      )}

      {/* Time horizon */}
      {time_horizon && (
        <div className="rounded-card bg-ghost border border-line p-4">
          <h4 className="text-sm font-semibold text-accent mb-1">
            ⏳ {time_horizon.label || `${time_horizon.start ?? ''} → ${time_horizon.end ?? ''}`}
          </h4>
          {time_horizon.months != null && (
            <div className="flex items-center gap-2 mt-2">
              <div className="flex-1 h-2 rounded-full bg-s2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(100, (time_horizon.months / 120) * 100)}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className="h-full rounded-full bg-accent"
                />
              </div>
              <span className="text-xs text-accent font-medium">
                {time_horizon.months < 12
                  ? `${time_horizon.months}mo`
                  : `${(time_horizon.months / 12).toFixed(1)}yr`}
              </span>
            </div>
          )}
          {time_horizon.milestones && time_horizon.milestones.length > 0 && (
            <div className="mt-3 space-y-1">
              {time_horizon.milestones.map((m, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-off">
                  <span>🏁</span>
                  <span className="font-medium">{m.label}</span>
                  {m.month != null && <span className="text-accent">— month {m.month}</span>}
                  {m.date && <span className="text-accent">— {m.date}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Evidence cards */}
      {evidence && evidence.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-muted uppercase tracking-wider">
            📑 Sources & Evidence
          </h4>
          {evidence.map((ev, i) => (
            <EvidenceCard key={i} evidence={ev} />
          ))}
        </div>
      )}

      {/* Examples */}
      {examples && examples.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-muted uppercase tracking-wider">
            💡 Examples
          </h4>
          {examples.map((ex, i) => (
            <div
              key={i}
              className="rounded-card bg-ghost border border-line p-3 text-sm"
            >
              <p className="font-medium text-accent">{ex.title}</p>
              <p className="text-off mt-1 text-xs">{ex.description}</p>
              {ex.data && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {Object.entries(ex.data).map(([k, v]) => (
                    <span
                      key={k}
                      className="text-xs bg-accent/10 text-accent px-2 py-0.5 rounded-full"
                    >
                      {k}: {typeof v === 'number' ? (v as number).toLocaleString() : String(v)}
                    </span>
                  ))}
                </div>
              )}
              {ex.projected_savings && (
                <p className="text-xs text-accent/70 mt-1">💰 Projected savings: {ex.projected_savings}</p>
              )}
              {ex.timeline && (
                <p className="text-xs text-accent/70">⏱️ Timeline: {ex.timeline}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
