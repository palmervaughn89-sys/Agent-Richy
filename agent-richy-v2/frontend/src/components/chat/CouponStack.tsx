"use client";

import React, { useState } from "react";
import type { Coupon } from "@/types/coupon";
import CouponCard from "./CouponCard";

interface CouponStackProps {
  coupons: Coupon[];
  storeName: string;
}

const INITIAL_VISIBLE = 3;

export default function CouponStack({ coupons, storeName }: CouponStackProps) {
  const [expanded, setExpanded] = useState(false);

  const visibleCoupons =
    expanded || coupons.length <= INITIAL_VISIBLE
      ? coupons
      : coupons.slice(0, INITIAL_VISIBLE);

  const hiddenCount = coupons.length - INITIAL_VISIBLE;

  return (
    <div className="rounded-card overflow-hidden">
      {/* Header */}
      <div className="bg-s1 rounded-t-card border border-line px-4 py-3 flex items-center justify-between">
        <span className="text-lg font-semibold text-txt">{storeName}</span>
        <span className="font-mono tracking-label uppercase text-[13px] bg-accent/15 text-accent px-2.5 py-0.5 rounded-full">
          {coupons.length} deal{coupons.length !== 1 ? "s" : ""} found
        </span>
      </div>

      {/* Cards */}
      <div className="space-y-2 p-2 border-x border-b border-line rounded-b-card bg-s2">
        {visibleCoupons.map((coupon) => (
          <CouponCard key={coupon.id} coupon={coupon} />
        ))}

        {/* Toggle button */}
        {hiddenCount > 0 && !expanded && (
          <button
            onClick={() => setExpanded(true)}
            className="w-full py-2 text-sm font-medium text-accent bg-card border border-line rounded-lg hover:bg-card-hover transition"
          >
            Show {hiddenCount} more deal{hiddenCount !== 1 ? "s" : ""}
          </button>
        )}

        {expanded && hiddenCount > 0 && (
          <button
            onClick={() => setExpanded(false)}
            className="w-full py-2 text-sm font-medium text-txt-muted bg-card border border-line rounded-lg hover:bg-card-hover transition"
          >
            Show less
          </button>
        )}
      </div>
    </div>
  );
}
