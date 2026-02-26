"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Clipboard, Check, ExternalLink } from "lucide-react";
import type { Coupon } from "@/types/coupon";

interface CouponCardProps {
  coupon: Coupon;
}

function ConfidenceBadge({ confidence }: { confidence: Coupon["confidence"] }) {
  const styles: Record<Coupon["confidence"], string> = {
    verified: "bg-accent/15 text-accent",
    likely_valid: "bg-amber-500/15 text-amber-400",
    unverified: "bg-white/10 text-txt-muted",
  };

  const labels: Record<Coupon["confidence"], string> = {
    verified: "Verified",
    likely_valid: "Likely Valid",
    unverified: "Unverified",
  };

  return (
    <span
      className={`font-mono text-[11px] uppercase tracking-label px-2 py-0.5 rounded-full ${styles[confidence]}`}
    >
      {labels[confidence]}
    </span>
  );
}

function formatDiscount(coupon: Coupon): string {
  switch (coupon.discountType) {
    case "percentage":
      return `${coupon.discountValue}% OFF`;
    case "fixed":
      return `$${coupon.discountValue} OFF`;
    case "bogo":
      return "BOGO";
    case "free_shipping":
      return "FREE SHIPPING";
  }
}

function formatExpiry(date?: string): string {
  if (!date) return "No expiration";
  const d = new Date(date);
  return `Expires ${d.toLocaleDateString("en-US", { month: "short", day: "numeric" })}`;
}

export default function CouponCard({ coupon }: CouponCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(coupon.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const dealUrl = coupon.affiliateUrl || coupon.sourceUrl;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border border-line rounded-card p-4 space-y-3"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-txt font-semibold">{coupon.store}</span>
        <ConfidenceBadge confidence={coupon.confidence} />
      </div>

      {/* Discount */}
      <p className="text-2xl font-bold text-accent">{formatDiscount(coupon)}</p>

      {/* Description */}
      <p className="text-txt-off text-sm line-clamp-2">{coupon.description}</p>

      {/* Code box */}
      <div className="bg-s2 border border-line rounded-lg px-4 py-3 flex items-center justify-between">
        <span className="font-mono text-accent text-lg tracking-wider">
          {coupon.code}
        </span>
        <button
          onClick={handleCopy}
          className="relative hover:bg-accent/10 rounded-lg p-2 transition"
          aria-label="Copy coupon code"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-accent" />
              <span className="absolute -top-7 left-1/2 -translate-x-1/2 text-accent text-xs font-medium whitespace-nowrap">
                Copied!
              </span>
            </>
          ) : (
            <Clipboard className="w-4 h-4 text-txt-muted" />
          )}
        </button>
      </div>

      {/* Footer */}
      <div className="flex justify-between text-txt-muted text-xs">
        <span>{formatExpiry(coupon.expiresAt)}</span>
        {coupon.restrictions && <span>Min. {coupon.restrictions}</span>}
      </div>

      {/* Deal link */}
      <a
        href={dealUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1 text-accent text-sm font-medium hover:underline"
      >
        Use Deal <ExternalLink className="w-3.5 h-3.5" />
      </a>
    </motion.div>
  );
}
