"use client";

import React from "react";
import { motion } from "framer-motion";
import { ChevronRight } from "lucide-react";
import type { SavingsReport, SavingsAction } from "@/types/spending";

interface SavingsReportCardProps {
  report: SavingsReport;
}

const TIME_LABELS: Record<SavingsAction["timeToRealize"], string> = {
  immediate: "Immediate",
  next_cycle: "Next billing cycle",
  "1_month": "~1 month",
  "3_months": "~3 months",
};

const TYPE_LABELS: Record<SavingsAction["type"], string> = {
  cancel: "Cancel",
  downgrade: "Downgrade",
  negotiate: "Negotiate",
  switch_annual: "Switch Annual",
  bundle: "Bundle",
  spend_to_save: "Spend to Save",
  free_alternative: "Free Alt",
  timing: "Timing",
  loyalty: "Loyalty",
};

function EffortDots({ level }: { level: number }) {
  return (
    <div className="flex gap-1" aria-label={`Effort level ${level} of 5`}>
      {Array.from({ length: 5 }, (_, i) => (
        <div
          key={i}
          className={`w-2 h-2 rounded-full ${
            i < level ? "bg-accent" : "bg-s2 border border-line"
          }`}
        />
      ))}
    </div>
  );
}

function BenchmarkBar({
  expense,
  userPays,
  marketAverage,
  potential,
}: {
  expense: string;
  userPays: number;
  marketAverage: number;
  potential: number;
}) {
  const maxVal = Math.max(userPays, marketAverage);

  return (
    <div className="space-y-1.5">
      <span className="text-txt-off text-sm">{expense}</span>
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-s2 rounded-full h-3 overflow-hidden">
            <div
              className="bg-accent/40 h-full rounded-full"
              style={{ width: `${(userPays / maxVal) * 100}%` }}
            />
          </div>
          <span className="text-txt text-xs w-16 text-right">${userPays}/mo</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-s2 rounded-full h-3 overflow-hidden">
            <div
              className="bg-accent h-full rounded-full"
              style={{ width: `${(marketAverage / maxVal) * 100}%` }}
            />
          </div>
          <span className="text-black bg-accent text-xs w-16 text-right rounded px-1">${marketAverage}/mo</span>
        </div>
      </div>
      <p className="text-accent text-xs font-medium text-right">
        Save ${potential}/mo
      </p>
    </div>
  );
}

export default function SavingsReportCard({ report }: SavingsReportCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Hero */}
      <div className="bg-s1 rounded-card p-6 text-center mb-4">
        <p className="text-txt-muted text-sm font-mono uppercase tracking-label mb-2">
          Your Potential Savings
        </p>
        <p className="text-4xl font-bold text-accent">
          ${report.totalPotentialAnnualSavings.toLocaleString()}/year
        </p>
        <p className="text-txt-off text-sm mt-1">
          That&apos;s ${Math.round(report.totalPotentialMonthlySavings).toLocaleString()}/month back
          in your pocket
        </p>
      </div>

      {/* Action list */}
      <div className="space-y-3">
        {report.actions.map((action, idx) => (
          <motion.div
            key={action.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="bg-card border border-line rounded-card p-4 space-y-2"
          >
            {/* Top row */}
            <div className="flex justify-between items-start">
              <span className="text-txt font-medium">{action.title}</span>
              <span className="text-accent font-semibold whitespace-nowrap ml-3">
                ${action.estimatedAnnualSavings}/yr
              </span>
            </div>

            {/* Description */}
            <p className="text-txt-off text-sm">{action.description}</p>

            {/* Bottom row */}
            <div className="flex gap-3 items-center flex-wrap">
              <EffortDots level={action.effortLevel} />
              <span className="font-mono tracking-label uppercase text-[11px] bg-accent/15 text-accent px-2 py-0.5 rounded-full">
                {TIME_LABELS[action.timeToRealize]}
              </span>
              <span className="font-mono tracking-label uppercase text-[11px] bg-ghost text-accent px-2 py-0.5 rounded-full">
                {TYPE_LABELS[action.type]}
              </span>
            </div>

            {/* Script link */}
            {action.script && (
              <a
                href="#"
                className="inline-flex items-center gap-1 text-accent text-sm hover:underline mt-1"
              >
                View negotiation script <ChevronRight className="w-3.5 h-3.5" />
              </a>
            )}
          </motion.div>
        ))}
      </div>

      {/* Redundancies */}
      {report.subscriptionRedundancies.length > 0 && (
        <div className="bg-s1 rounded-card p-4 mt-4 space-y-3">
          <h4 className="font-mono text-accent text-sm uppercase tracking-label">
            Subscription Overlaps
          </h4>
          {report.subscriptionRedundancies.map((r, i) => (
            <div key={i} className="space-y-1">
              <p className="text-txt text-sm">
                {r.services.join(", ")}{" "}
                <span className="text-txt-muted">— ${r.combinedCost.toFixed(2)}/mo combined</span>
              </p>
              <p className="text-txt-off text-sm">{r.suggestion}</p>
            </div>
          ))}
        </div>
      )}

      {/* Benchmarks */}
      {report.benchmarkComparisons.length > 0 && (
        <div className="bg-s1 rounded-card p-4 mt-4 space-y-4">
          <h4 className="font-mono text-accent text-sm uppercase tracking-label">
            How Your Bills Compare
          </h4>
          {report.benchmarkComparisons.map((b, i) => (
            <BenchmarkBar
              key={i}
              expense={b.expense}
              userPays={b.userPays}
              marketAverage={b.marketAverage}
              potential={b.potential}
            />
          ))}
        </div>
      )}

      {/* Summary footer */}
      <div className="border-t border-line pt-4 mt-4">
        <p className="text-txt font-semibold text-lg">
          If you did everything:{" "}
          <span className="text-accent">
            ${report.totalPotentialAnnualSavings.toLocaleString()}/year saved
          </span>
        </p>
      </div>
    </motion.div>
  );
}
