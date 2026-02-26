"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Clipboard, Check } from "lucide-react";

interface NegotiationScriptCardProps {
  serviceName: string;
  currentCost: number;
  targetCost: number;
  steps: string[];
  competitorPrices: { name: string; price: number }[];
}

export default function NegotiationScriptCard({
  serviceName,
  currentCost,
  targetCost,
  steps,
  competitorPrices,
}: NegotiationScriptCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const fullScript = [
    `Call ${serviceName} Customer Retention`,
    `Goal: ${currentCost}/mo → ${targetCost}/mo`,
    "",
    ...steps.map((s, i) => `${i + 1}. ${s}`),
    "",
    "Competitor prices to mention:",
    ...competitorPrices.map((c) => `  - ${c.name}: $${c.price}/mo`),
  ].join("\n");

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await navigator.clipboard.writeText(fullScript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-card border rounded-card overflow-hidden transition ${
        expanded ? "border-line-hover" : "border-line hover:border-line-hover cursor-pointer"
      }`}
    >
      {/* Collapsed header — always visible */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between p-4 text-left"
      >
        <div>
          <p className="text-txt font-medium">
            📞 Negotiation Script: {serviceName}
          </p>
          {!expanded && (
            <p className="text-txt-muted text-xs mt-0.5">Tap to expand</p>
          )}
        </div>
        <ChevronDown
          className={`w-5 h-5 text-txt-muted transition-transform ${
            expanded ? "rotate-180" : ""
          }`}
        />
      </button>

      {/* Expanded body */}
      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            key="body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-4">
              {/* Sub-header */}
              <p className="text-accent font-mono text-sm uppercase tracking-label">
                Call {serviceName} Customer Retention
              </p>

              {/* Cost target */}
              <p className="text-txt text-lg font-semibold">
                ${currentCost}/mo{" "}
                <span className="text-txt-muted">→</span>{" "}
                <span className="text-accent">${targetCost}/mo</span>
              </p>

              {/* Steps */}
              <div className="space-y-2">
                {steps.map((step, i) => (
                  <div
                    key={i}
                    className="bg-s1 rounded-lg p-3 flex gap-3"
                  >
                    <span className="text-accent font-mono font-bold text-sm shrink-0">
                      {i + 1}.
                    </span>
                    <span className="text-txt-off text-sm">{step}</span>
                  </div>
                ))}
              </div>

              {/* Competitor pricing */}
              {competitorPrices.length > 0 && (
                <div className="bg-s2 rounded-lg p-3 space-y-2">
                  <p className="font-mono text-[11px] text-accent uppercase tracking-label">
                    Mention these competitor prices:
                  </p>
                  {competitorPrices.map((c, i) => (
                    <div key={i} className="flex justify-between text-sm">
                      <span className="text-txt-off">{c.name}</span>
                      <span className="text-txt font-medium">${c.price}/mo</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Copy button */}
              <button
                onClick={handleCopy}
                className="w-full bg-card border border-line rounded-lg py-2.5 text-sm font-medium text-txt hover:bg-card-hover transition flex items-center justify-center gap-2"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4 text-accent" /> Copied!
                  </>
                ) : (
                  <>
                    <Clipboard className="w-4 h-4" /> Copy Full Script
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
