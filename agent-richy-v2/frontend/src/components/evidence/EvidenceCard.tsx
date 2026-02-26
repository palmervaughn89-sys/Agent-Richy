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
      className="rounded-lg border border-line bg-s1 overflow-hidden"
    >
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between px-3 py-2 text-left
                   hover:bg-card transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-xs">📎</span>
          <span className="text-xs font-medium text-txt">
            {evidence.source}
          </span>
          {evidence.confidence && (
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                evidence.confidence > 0.8
                  ? 'bg-accent/15 text-accent'
                  : evidence.confidence > 0.5
                  ? 'bg-amber-500/15 text-amber-400'
                  : 'bg-red-500/15 text-red-400'
              }`}
            >
              {(evidence.confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>
        <motion.span
          animate={{ rotate: expanded ? 180 : 0 }}
          className="text-muted text-xs"
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
            <p className="text-xs text-muted leading-relaxed">
              {evidence.snippet || evidence.fact}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
