'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { ProactiveAlert } from '@/lib/predictiveEngine';

/* ── Animation ─────────────────────────────────────────────────────── */

const slideIn = {
  hidden: { opacity: 0, y: -16, scale: 0.97 },
  show: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.4, ease: 'easeOut' } },
  exit: { opacity: 0, y: -10, scale: 0.97, transition: { duration: 0.25, ease: 'easeIn' } },
};

const collapse = {
  initial: { height: 0, opacity: 0 },
  animate: { height: 'auto', opacity: 1, transition: { duration: 0.25, ease: 'easeOut' } },
  exit: { height: 0, opacity: 0, transition: { duration: 0.2, ease: 'easeIn' } },
};

/* ── Priority config ───────────────────────────────────────────────── */

const PRIORITY_STYLES: Record<
  ProactiveAlert['priority'],
  { border: string; badge: string; badgeText: string }
> = {
  urgent: {
    border: 'border-l-red-500',
    badge: 'bg-red-500/15 text-red-400',
    badgeText: 'URGENT',
  },
  high: {
    border: 'border-l-accent',
    badge: 'bg-accent/15 text-accent',
    badgeText: 'HIGH',
  },
  medium: {
    border: 'border-l-amber-400',
    badge: 'bg-amber-400/15 text-amber-400',
    badgeText: 'MEDIUM',
  },
  low: {
    border: 'border-l-muted',
    badge: 'bg-s2 text-muted',
    badgeText: 'LOW',
  },
};

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

/* ── Chevron ───────────────────────────────────────────────────────── */

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 16 16"
      fill="none"
      className={`text-muted transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
    >
      <path
        d="M4 6L8 10L12 6"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/* ── Component ─────────────────────────────────────────────────────── */

interface Props {
  alert: ProactiveAlert;
  compact?: boolean;
  onDismiss?: (id: string) => void;
  onAction?: (action: string) => void;
}

export default function ProactiveAlertCard({
  alert,
  compact = false,
  onDismiss,
  onAction,
}: Props) {
  const [showReasoning, setShowReasoning] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  const style = PRIORITY_STYLES[alert.priority];

  if (dismissed) return null;

  return (
    <AnimatePresence>
      <motion.div
        variants={slideIn}
        initial="hidden"
        animate="show"
        exit="exit"
        className={`bg-card border-l-4 ${style.border} border border-line rounded-card ${compact ? 'p-3' : 'p-4'} relative`}
      >
        {/* Priority badge — top right */}
        <span
          className={`absolute top-3 right-3 text-[10px] font-mono px-2 py-0.5 rounded uppercase tracking-wider ${style.badge}`}
        >
          {style.badgeText}
        </span>

        {/* Title */}
        <h4 className={`text-txt font-semibold pr-20 ${compact ? 'text-sm' : ''}`}>
          {alert.title}
        </h4>

        {/* Message */}
        <p className={`text-off mt-1 ${compact ? 'text-xs' : 'text-sm'}`}>
          {alert.message}
        </p>

        {/* Reasoning — collapsible */}
        {alert.reasoning && !compact && (
          <div className="mt-2">
            <button
              onClick={() => setShowReasoning(!showReasoning)}
              className="text-muted text-xs hover:text-off transition-colors inline-flex items-center gap-1 cursor-pointer"
            >
              <Chevron open={showReasoning} />
              Why am I seeing this?
            </button>

            <AnimatePresence>
              {showReasoning && (
                <motion.div
                  key="reasoning"
                  variants={collapse}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  className="overflow-hidden"
                >
                  <p className="text-muted text-xs italic mt-1 pl-4 border-l-2 border-line">
                    {alert.reasoning}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Estimated value */}
        {alert.estimatedValue > 0 && (
          <p className="text-accent font-medium mt-2 text-sm">
            Potential value: {fmt(alert.estimatedValue)}/year
          </p>
        )}

        {/* Actions row */}
        <div className={`flex items-center gap-3 ${compact ? 'mt-2' : 'mt-3'}`}>
          {/* Action button */}
          {alert.actionButton && (
            <button
              onClick={() => onAction?.(alert.actionButton!.action)}
              className="btn-primary text-sm px-4 py-1.5 rounded-md font-medium cursor-pointer"
            >
              {alert.actionButton.label}
            </button>
          )}

          {/* Suggested action text (if no button) */}
          {!alert.actionButton && alert.suggestedAction && !compact && (
            <p className="text-off text-xs flex-1">{alert.suggestedAction}</p>
          )}

          {/* Dismiss */}
          {alert.dismissable && (
            <button
              onClick={() => {
                setDismissed(true);
                onDismiss?.(alert.id);
              }}
              className="text-muted text-xs hover:text-off transition-colors ml-auto cursor-pointer"
            >
              Dismiss
            </button>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
