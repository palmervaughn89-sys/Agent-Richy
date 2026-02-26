'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Evidence } from '@/lib/types';

interface Props {
  evidence: Evidence;
}

export default function EvidenceCard({ evidence }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      layout
      className="rounded-lg border border-gray-200 dark:border-navy-700
                 bg-gray-50 dark:bg-navy-800/50 overflow-hidden"
    >
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between px-3 py-2 text-left
                   hover:bg-gray-100 dark:hover:bg-navy-700/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-xs">📎</span>
          <span className="text-xs font-medium text-navy-700 dark:text-gray-200">
            {evidence.source}
          </span>
          {evidence.confidence && (
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                evidence.confidence > 0.8
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                  : evidence.confidence > 0.5
                  ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                  : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
              }`}
            >
              {(evidence.confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>
        <motion.span
          animate={{ rotate: expanded ? 180 : 0 }}
          className="text-gray-400 text-xs"
        >
          ▼
        </motion.span>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="px-3 pb-3"
          >
            <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
              {evidence.snippet || evidence.fact}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
