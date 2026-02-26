"use client";

import React from "react";
import { motion } from "framer-motion";

interface SpendToSaveCardProps {
  title: string;
  upfrontCost: number;
  monthlySavings: number;
  roiMonths: number;
  description: string;
}

export default function SpendToSaveCard({
  title,
  upfrontCost,
  monthlySavings,
  roiMonths,
  description,
}: SpendToSaveCardProps) {
  // Clamp fill to 100% max for display
  const fillPercent = Math.min((1 / roiMonths) * 100, 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border border-line rounded-card p-4"
    >
      {/* Title */}
      <h4 className="text-txt font-medium">{title}</h4>

      {/* Description */}
      <p className="text-txt-off text-sm mt-1">{description}</p>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mt-3">
        <div className="bg-s1 rounded-lg p-3 text-center">
          <p className="text-accent font-bold text-lg">${upfrontCost}</p>
          <p className="text-txt-muted text-xs font-mono uppercase tracking-label mt-0.5">
            Upfront Cost
          </p>
        </div>
        <div className="bg-s1 rounded-lg p-3 text-center">
          <p className="text-accent font-bold text-lg">${monthlySavings}</p>
          <p className="text-txt-muted text-xs font-mono uppercase tracking-label mt-0.5">
            Monthly Savings
          </p>
        </div>
        <div className="bg-s1 rounded-lg p-3 text-center">
          <p className="text-accent font-bold text-lg">{roiMonths}</p>
          <p className="text-txt-muted text-xs font-mono uppercase tracking-label mt-0.5">
            Months to ROI
          </p>
        </div>
      </div>

      {/* ROI progress bar */}
      <div className="mt-3">
        <p className="text-txt-muted text-xs mb-1.5">Break-even timeline</p>
        <div className="relative bg-s2 rounded-full h-2">
          <div
            className="bg-accent rounded-full h-2 transition-all"
            style={{ width: `${fillPercent}%` }}
          />
          {/* Break-even marker */}
          <div
            className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-accent border-2 border-card"
            style={{ left: `${fillPercent}%`, transform: `translate(-50%, -50%)` }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-txt-muted font-mono mt-1">
          <span>Now</span>
          <span>{roiMonths}mo</span>
        </div>
      </div>
    </motion.div>
  );
}
