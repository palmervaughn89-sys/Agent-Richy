'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface QuizOption {
  label: string;
  correct?: boolean;
}

interface Props {
  question: string;
  options: QuizOption[];
  explanation?: string;
  onAnswer?: (correct: boolean) => void;
}

export default function QuizCard({ question, options, explanation, onAnswer }: Props) {
  const [selected, setSelected] = useState<number | null>(null);
  const [revealed, setRevealed] = useState(false);

  const handleSelect = (i: number) => {
    if (revealed) return;
    setSelected(i);
    setRevealed(true);
    onAnswer?.(!!options[i].correct);
  };

  return (
    <div className="rounded-xl border border-gray-200 dark:border-navy-700
                    bg-white dark:bg-navy-800 p-5 shadow-sm">
      <div className="flex items-start gap-2 mb-4">
        <span className="text-lg">❓</span>
        <h3 className="text-sm font-semibold text-navy-800 dark:text-white leading-snug">
          {question}
        </h3>
      </div>

      <div className="space-y-2">
        {options.map((opt, i) => {
          let style = 'border-gray-200 dark:border-navy-600 hover:border-gold-400';
          if (revealed) {
            if (opt.correct) style = 'border-green-500 bg-green-50 dark:bg-green-900/20';
            else if (i === selected && !opt.correct)
              style = 'border-red-500 bg-red-50 dark:bg-red-900/20';
            else style = 'border-gray-200 dark:border-navy-700 opacity-50';
          }

          return (
            <motion.button
              key={i}
              whileHover={!revealed ? { scale: 1.01 } : {}}
              whileTap={!revealed ? { scale: 0.99 } : {}}
              onClick={() => handleSelect(i)}
              disabled={revealed}
              className={`w-full text-left px-4 py-2.5 rounded-lg border text-sm
                         transition-all ${style}`}
            >
              <span className="font-medium text-navy-700 dark:text-gray-200">
                {String.fromCharCode(65 + i)}.{' '}
              </span>
              <span className="text-navy-600 dark:text-gray-300">{opt.label}</span>
              {revealed && opt.correct && <span className="ml-2">✅</span>}
              {revealed && i === selected && !opt.correct && <span className="ml-2">❌</span>}
            </motion.button>
          );
        })}
      </div>

      {revealed && explanation && (
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 px-3 py-2 rounded-lg bg-blue-50 dark:bg-blue-900/20
                     border border-blue-200 dark:border-blue-800 text-xs
                     text-blue-700 dark:text-blue-300"
        >
          💡 {explanation}
        </motion.div>
      )}
    </div>
  );
}
