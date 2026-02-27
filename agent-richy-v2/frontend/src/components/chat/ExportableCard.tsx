'use client';

import { useState, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/* ── Types ─────────────────────────────────────────────────────────── */

export interface ExportData {
  clipboard: string;   // Plain-text version for clipboard
  formatted: string;   // Nicely formatted text (notes app, print, etc.)
}

interface ExportableCardProps {
  title: string;
  children: ReactNode;
  exportData: ExportData;
}

/* ── Animation ─────────────────────────────────────────────────────── */

const toastVariants = {
  hidden: { opacity: 0, y: 8, scale: 0.95 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.2, ease: 'easeOut' } },
  exit: { opacity: 0, y: -4, scale: 0.95, transition: { duration: 0.15, ease: 'easeIn' } },
};

/* ── Icons ─────────────────────────────────────────────────────────── */

function CopyIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" className="shrink-0">
      <rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
      <path d="M11 5V3.5A1.5 1.5 0 0 0 9.5 2H3.5A1.5 1.5 0 0 0 2 3.5v6A1.5 1.5 0 0 0 3.5 11H5" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" className="shrink-0">
      <path d="M3 8.5L6.5 12L13 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ShareIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" className="shrink-0">
      <path d="M8 2v8M4 6l4-4 4 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M2 10v3a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}

function NotesIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" className="shrink-0">
      <rect x="2" y="1" width="12" height="14" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
      <path d="M5 5h6M5 8h6M5 11h3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}

/* ── Component ─────────────────────────────────────────────────────── */

export default function ExportableCard({
  title,
  children,
  exportData,
}: ExportableCardProps) {
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2000);
  };

  const copyClipboard = async () => {
    try {
      await navigator.clipboard.writeText(exportData.clipboard);
      showToast('Copied!');
    } catch {
      showToast('Copy failed');
    }
  };

  const copyFormatted = async () => {
    try {
      await navigator.clipboard.writeText(exportData.formatted);
      showToast('Copied formatted!');
    } catch {
      showToast('Copy failed');
    }
  };

  const share = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title,
          text: exportData.formatted,
        });
      } catch {
        /* user cancelled — no-op */
      }
    } else {
      // Fallback: copy formatted text
      await copyFormatted();
    }
  };

  return (
    <div className="relative">
      {/* Card content */}
      {children}

      {/* Export toolbar */}
      <div className="bg-s2 rounded-b-card border-t border-line px-4 py-2 flex items-center gap-2">
        <span className="text-muted text-[11px] font-mono uppercase tracking-wider mr-auto">
          Export
        </span>

        <button
          onClick={copyClipboard}
          className="btn-secondary text-xs inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md hover:bg-s1 transition-colors cursor-pointer"
          title="Copy to clipboard"
        >
          <CopyIcon />
          Copy
        </button>

        <button
          onClick={copyFormatted}
          className="btn-secondary text-xs inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md hover:bg-s1 transition-colors cursor-pointer"
          title="Copy formatted (for notes)"
        >
          <NotesIcon />
          Notes
        </button>

        <button
          onClick={share}
          className="btn-secondary text-xs inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md hover:bg-s1 transition-colors cursor-pointer"
          title="Share"
        >
          <ShareIcon />
          Share
        </button>
      </div>

      {/* Toast notification */}
      <AnimatePresence>
        {toast && (
          <motion.div
            key="toast"
            variants={toastVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="absolute bottom-14 left-1/2 -translate-x-1/2 bg-accent text-bg text-xs font-medium px-3 py-1.5 rounded-full inline-flex items-center gap-1.5 whitespace-nowrap shadow-lg z-10"
          >
            <CheckIcon />
            {toast}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
