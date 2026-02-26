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
            <div key={i} className="rounded-xl border border-gray-100 dark:border-navy-700
                                    bg-white dark:bg-navy-800 p-4 shadow-sm">
              {chart.title && (
                <h4 className="text-sm font-semibold text-navy-700 dark:text-gray-200 mb-2">
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
        <div className="rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200
                        dark:border-green-800 p-4">
          <h4 className="text-sm font-semibold text-green-800 dark:text-green-300 mb-2">
            🧮 Calculator Result
          </h4>
          <pre className="text-xs text-green-700 dark:text-green-400 whitespace-pre-wrap">
            {typeof calculator_result === 'string'
              ? calculator_result
              : JSON.stringify(calculator_result, null, 2)}
          </pre>
        </div>
      )}

      {/* Time horizon */}
      {time_horizon && (
        <div className="rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200
                        dark:border-blue-800 p-4">
          <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-300 mb-1">
            ⏳ {time_horizon.label || `${time_horizon.start ?? ''} → ${time_horizon.end ?? ''}`}
          </h4>
          {time_horizon.months != null && (
            <div className="flex items-center gap-2 mt-2">
              <div className="flex-1 h-2 rounded-full bg-blue-200 dark:bg-blue-800 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(100, (time_horizon.months / 120) * 100)}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className="h-full rounded-full bg-blue-500"
                />
              </div>
              <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                {time_horizon.months < 12
                  ? `${time_horizon.months}mo`
                  : `${(time_horizon.months / 12).toFixed(1)}yr`}
              </span>
            </div>
          )}
          {time_horizon.milestones && time_horizon.milestones.length > 0 && (
            <div className="mt-3 space-y-1">
              {time_horizon.milestones.map((m, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-blue-700 dark:text-blue-300">
                  <span>🏁</span>
                  <span className="font-medium">{m.label}</span>
                  {m.month != null && <span className="text-blue-500">— month {m.month}</span>}
                  {m.date && <span className="text-blue-500">— {m.date}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Evidence cards */}
      {evidence && evidence.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
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
          <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            💡 Examples
          </h4>
          {examples.map((ex, i) => (
            <div
              key={i}
              className="rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-200
                         dark:border-purple-800 p-3 text-sm"
            >
              <p className="font-medium text-purple-800 dark:text-purple-300">{ex.title}</p>
              <p className="text-purple-600 dark:text-purple-400 mt-1 text-xs">{ex.description}</p>
              {ex.data && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {Object.entries(ex.data).map(([k, v]) => (
                    <span
                      key={k}
                      className="text-xs bg-purple-100 dark:bg-purple-800 text-purple-700
                                 dark:text-purple-200 px-2 py-0.5 rounded-full"
                    >
                      {k}: {typeof v === 'number' ? (v as number).toLocaleString() : String(v)}
                    </span>
                  ))}
                </div>
              )}
              {ex.projected_savings && (
                <p className="text-xs text-purple-500 mt-1">💰 Projected savings: {ex.projected_savings}</p>
              )}
              {ex.timeline && (
                <p className="text-xs text-purple-500">⏱️ Timeline: {ex.timeline}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
