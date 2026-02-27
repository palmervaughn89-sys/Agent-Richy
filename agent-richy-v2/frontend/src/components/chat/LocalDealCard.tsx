'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { LocalDeal, LocalDealReport } from '@/types/tools';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return iso;
  }
}

/* ── Animation variants ────────────────────────────────────────────── */

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
};

const collapse = {
  initial: { height: 0, opacity: 0 },
  animate: { height: 'auto', opacity: 1, transition: { duration: 0.25, ease: 'easeOut' } },
  exit: { height: 0, opacity: 0, transition: { duration: 0.2, ease: 'easeIn' } },
};

/* ── Chevron SVG ───────────────────────────────────────────────────── */

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      width="16"
      height="16"
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

/* ── Deal Card (reused for matched + top deals) ────────────────────── */

function DealCard({
  deal,
  compact = false,
}: {
  deal: LocalDeal;
  compact?: boolean;
}) {
  return (
    <motion.div
      variants={fadeUp}
      className="bg-card border border-line rounded-lg p-4"
    >
      {/* Top row: store + distance */}
      <div className="flex items-center justify-between gap-2 mb-1">
        <span className="text-txt font-medium truncate">{deal.storeName}</span>
        {deal.distanceMiles != null && (
          <span className="text-muted text-xs shrink-0">
            {deal.distanceMiles} mi
          </span>
        )}
      </div>

      {/* Product name */}
      <p className={`text-off ${compact ? 'text-sm' : ''}`}>
        {deal.productName}
      </p>

      {/* Price row */}
      <div className="flex items-center gap-3 mt-2 flex-wrap">
        <span className="text-muted line-through text-sm">
          {fmt(deal.originalPrice)}
        </span>
        <span className="text-accent text-xl font-bold">
          {fmt(deal.salePrice)}
        </span>
        <span className="bg-accent/15 text-accent text-xs px-2 py-1 rounded-full whitespace-nowrap">
          Save {fmt(deal.savings)} ({deal.savingsPercent}%)
        </span>
      </div>

      {/* Badges row */}
      <div className="flex items-center gap-2 mt-2 flex-wrap">
        {deal.isHistoricLow && (
          <span className="bg-red-500/15 text-red-400 text-[10px] font-mono px-2 py-0.5 rounded">
            🔥 HISTORIC LOW
          </span>
        )}
        {deal.dealType !== 'sale' && (
          <span className="bg-s2 text-off text-[10px] font-mono px-2 py-0.5 rounded uppercase">
            {deal.dealType}
          </span>
        )}
      </div>

      {/* Usual price context */}
      {deal.userBuysThis && deal.usualPrice > 0 && (
        <p className="text-muted text-xs mt-2">
          You usually pay {fmt(deal.usualPrice)}
        </p>
      )}

      {/* Footer: dates + source + loyalty */}
      <div className="flex items-center gap-2 mt-2 flex-wrap text-muted text-[11px]">
        <span>
          {fmtDate(deal.validFrom)} – {fmtDate(deal.validUntil)}
        </span>
        <span>·</span>
        <span>{deal.source}</span>
        {deal.requiresLoyaltyCard && (
          <>
            <span>·</span>
            <span>Loyalty card required</span>
          </>
        )}
        {deal.requiresMembership && (
          <>
            <span>·</span>
            <span>Membership required</span>
          </>
        )}
        {deal.limitPerCustomer != null && (
          <>
            <span>·</span>
            <span>Limit {deal.limitPerCustomer}</span>
          </>
        )}
      </div>
    </motion.div>
  );
}

/* ── Accordion for weekly ad highlights ────────────────────────────── */

function WeeklyAdAccordion({
  ad,
}: {
  ad: LocalDealReport['weeklyAdHighlights'][number];
}) {
  const [open, setOpen] = useState(false);

  return (
    <motion.div variants={fadeUp} className="bg-card border border-line rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-s1/50 transition-colors"
      >
        <span className="text-txt font-medium">{ad.storeName}</span>
        <div className="flex items-center gap-2">
          <span className="text-muted text-sm">
            {ad.topDeals.length} top deal{ad.topDeals.length !== 1 ? 's' : ''}
          </span>
          <Chevron open={open} />
        </div>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            key="content"
            variants={collapse}
            initial="initial"
            animate="animate"
            exit="exit"
            className="overflow-hidden"
          >
            <div className="px-4 pb-3 space-y-1">
              {ad.topDeals.map((deal, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-off truncate mr-3">{deal.item}</span>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-accent font-medium">
                      {fmt(deal.salePrice)}
                    </span>
                    <span className="text-muted text-xs">{deal.savings}</span>
                  </div>
                </div>
              ))}
              <p className="text-muted text-[11px] pt-1">{ad.adValidDates}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ── Main Component ────────────────────────────────────────────────── */

export default function LocalDealCard({
  report,
}: {
  report: LocalDealReport;
}) {
  const totalDeals = report.topDeals.length + report.matchedDeals.length;

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={stagger}
      className="bg-card border border-line rounded-card overflow-hidden"
    >
      {/* ── 1. HEADER ─────────────────────────────────────────────── */}
      <motion.div variants={fadeUp} className="bg-s1 rounded-t-card p-5">
        <p className="font-mono text-accent text-xs uppercase tracking-widest">
          DEAL RADAR
        </p>
        <h3 className="text-xl font-bold text-txt mt-1">
          Deals Near {report.zipCode}
        </h3>
        <p className="text-muted text-sm mt-1">
          Within {report.radius} miles · {totalDeals} deal
          {totalDeals !== 1 ? 's' : ''} found
        </p>
        {report.totalPotentialSavings > 0 && (
          <p className="text-accent font-medium mt-1">
            Up to {fmt(report.totalPotentialSavings)} in savings this week
          </p>
        )}
      </motion.div>

      <div className="p-5 space-y-4">
        {/* ── 2. MATCHED DEALS ──────────────────────────────────────── */}
        {report.matchedDeals.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">
              DEALS ON THINGS YOU BUY
            </p>
            <div className="space-y-3">
              {report.matchedDeals.map((deal) => (
                <DealCard key={deal.id} deal={deal} />
              ))}
            </div>
          </motion.div>
        )}

        {/* ── 3. WEEKLY AD HIGHLIGHTS ───────────────────────────────── */}
        {report.weeklyAdHighlights.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">
              THIS WEEK&apos;S ADS
            </p>
            <div className="space-y-2">
              {report.weeklyAdHighlights.map((ad) => (
                <WeeklyAdAccordion key={ad.store} ad={ad} />
              ))}
            </div>
          </motion.div>
        )}

        {/* ── 4. TOP DEALS ──────────────────────────────────────────── */}
        {report.topDeals.length > 0 && (
          <motion.div variants={fadeUp}>
            <p className="font-mono text-accent text-xs uppercase tracking-widest mb-3">
              BEST DEALS NEARBY
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {report.topDeals.map((deal) => (
                <DealCard key={deal.id} deal={deal} compact />
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
