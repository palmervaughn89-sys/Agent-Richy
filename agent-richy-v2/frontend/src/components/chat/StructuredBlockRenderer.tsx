"use client";

import React, { useMemo } from "react";
import type { Coupon } from "@/types/coupon";
import type { SavingsReport, RecurringExpense } from "@/types/spending";
import CouponStack from "./CouponStack";
import ExpenseInputCard from "./ExpenseInputCard";
import SavingsReportCard from "./SavingsReportCard";
import NegotiationScriptCard from "./NegotiationScriptCard";
import SpendToSaveCard from "./SpendToSaveCard";
import { useChatStore } from "@/hooks/useChat";

/* ── Type guards for each structured block ─────────────────────────── */

interface CouponResultsBlock {
  type: "coupon_results";
  store: string;
  coupons: Coupon[];
}

interface ExpenseInputBlock {
  type: "expense_input";
}

interface SavingsReportBlock {
  type: "savings_report";
  report: SavingsReport;
}

interface NegotiationScriptBlock {
  type: "negotiation_script";
  serviceName: string;
  currentCost: number;
  targetCost: number;
  steps: string[];
  competitorPrices: { name: string; price: number }[];
}

interface SpendToSaveBlock {
  type: "spend_to_save";
  title: string;
  upfrontCost: number;
  monthlySavings: number;
  roiMonths: number;
  description: string;
}

type StructuredBlock =
  | CouponResultsBlock
  | ExpenseInputBlock
  | SavingsReportBlock
  | NegotiationScriptBlock
  | SpendToSaveBlock;

const KNOWN_TYPES = new Set([
  "coupon_results",
  "expense_input",
  "savings_report",
  "negotiation_script",
  "spend_to_save",
]);

/* ── Segment: either plain text or a parsed structured block ───────── */

type Segment =
  | { kind: "text"; content: string }
  | { kind: "block"; data: StructuredBlock };

/**
 * Match JSON objects that contain a "type" field. Handles both raw JSON and
 * markdown-fenced JSON (```json ... ``` or ``` ... ```).
 *
 * The regex captures everything between the outermost { } (non-greedy within
 * fences, greedy-balanced for raw JSON). We do a secondary parse + validation.
 */
const FENCED_RE =
  /```(?:json)?\s*\n?\s*(\{[\s\S]*?\})\s*\n?\s*```/g;

const RAW_JSON_RE =
  /(?:^|\n)\s*(\{[^{}]*"type"\s*:\s*"[^"]+?"[^{}]*(?:\{[^{}]*\}[^{}]*)*\})/g;

function parseSegments(text: string): Segment[] {
  // Collect all candidate JSON substrings with their positions
  const candidates: { start: number; end: number; json: string }[] = [];

  // 1. Fenced code blocks (higher priority)
  let m: RegExpExecArray | null;
  FENCED_RE.lastIndex = 0;
  while ((m = FENCED_RE.exec(text)) !== null) {
    candidates.push({ start: m.index, end: m.index + m[0].length, json: m[1] });
  }

  // 2. Raw JSON (only if not already inside a fence)
  RAW_JSON_RE.lastIndex = 0;
  while ((m = RAW_JSON_RE.exec(text)) !== null) {
    const matchStart = m.index + (m[0].length - m[1].length); // offset to actual JSON
    const matchEnd = m.index + m[0].length;
    const overlaps = candidates.some((c) => matchStart < c.end && matchEnd > c.start);
    if (!overlaps) {
      candidates.push({ start: m.index, end: matchEnd, json: m[1] });
    }
  }

  if (candidates.length === 0) {
    return [{ kind: "text", content: text }];
  }

  // Sort by position
  candidates.sort((a, b) => a.start - b.start);

  const segments: Segment[] = [];
  let cursor = 0;

  for (const c of candidates) {
    // Try parsing
    let parsed: unknown;
    try {
      parsed = JSON.parse(c.json);
    } catch {
      continue; // malformed — skip, will stay as raw text
    }

    if (
      typeof parsed !== "object" ||
      parsed === null ||
      !("type" in parsed) ||
      !KNOWN_TYPES.has((parsed as { type: string }).type)
    ) {
      continue; // not a known structured block
    }

    // Emit preceding text
    if (c.start > cursor) {
      const before = text.slice(cursor, c.start).trim();
      if (before) segments.push({ kind: "text", content: before });
    }

    segments.push({ kind: "block", data: parsed as StructuredBlock });
    cursor = c.end;
  }

  // Trailing text
  if (cursor < text.length) {
    const after = text.slice(cursor).trim();
    if (after) segments.push({ kind: "text", content: after });
  }

  return segments;
}

/* ── Component ─────────────────────────────────────────────────────── */

interface StructuredBlockRendererProps {
  content: string;
}

export default function StructuredBlockRenderer({ content }: StructuredBlockRendererProps) {
  const { sendMessage } = useChatStore();

  const segments = useMemo(() => parseSegments(content), [content]);

  // If there are no structured blocks, render plain text as-is
  const hasBlocks = segments.some((s) => s.kind === "block");
  if (!hasBlocks) {
    return <div className="whitespace-pre-wrap">{content}</div>;
  }

  /* Callbacks for ExpenseInputCard */
  const handleAddExpense = (_expense: RecurringExpense) => {
    // Individual expense added — no-op for now; the card manages its own list
  };

  const handleAnalyze = (expenses: RecurringExpense[]) => {
    const summary = expenses
      .map((e) => `${e.name} ($${e.amount}/${e.frequency})`)
      .join(", ");
    sendMessage(
      `Analyze my spending and find savings. Here are my expenses: ${summary}`
    );
  };

  return (
    <div className="space-y-3">
      {segments.map((seg, i) => {
        if (seg.kind === "text") {
          return (
            <div key={i} className="whitespace-pre-wrap">
              {seg.content}
            </div>
          );
        }

        const { data } = seg;

        switch (data.type) {
          case "coupon_results":
            return (
              <CouponStack
                key={i}
                storeName={data.store}
                coupons={data.coupons}
              />
            );

          case "expense_input":
            return (
              <ExpenseInputCard
                key={i}
                onAddExpense={handleAddExpense}
                onAnalyze={handleAnalyze}
              />
            );

          case "savings_report":
            return <SavingsReportCard key={i} report={data.report} />;

          case "negotiation_script":
            return (
              <NegotiationScriptCard
                key={i}
                serviceName={data.serviceName}
                currentCost={data.currentCost}
                targetCost={data.targetCost}
                steps={data.steps}
                competitorPrices={data.competitorPrices}
              />
            );

          case "spend_to_save":
            return (
              <SpendToSaveCard
                key={i}
                title={data.title}
                upfrontCost={data.upfrontCost}
                monthlySavings={data.monthlySavings}
                roiMonths={data.roiMonths}
                description={data.description}
              />
            );

          default:
            return null;
        }
      })}
    </div>
  );
}
