"use client";

import React, { useMemo } from "react";
import type { Coupon } from "@/types/coupon";
import type { SavingsReport, RecurringExpense } from "@/types/spending";
import CouponStack from "./CouponStack";
import ExpenseInputCard from "./ExpenseInputCard";
import SavingsReportCard from "./SavingsReportCard";
import NegotiationScriptCard from "./NegotiationScriptCard";
import SpendToSaveCard from "./SpendToSaveCard";
import MarketReportCard from "./MarketReportCard";
import AnalystInsightCard from "./AnalystInsightCard";
import SectorOutlookCard from "./SectorOutlookCard";
import PriceComparisonCard from "./PriceComparisonCard";
import StoreRankingCard from "./StoreRankingCard";
import SubscriptionValueCard from "./SubscriptionValueCard";
import GoalSimulatorCard from "./GoalSimulatorCard";
import BillPredictorCard from "./BillPredictorCard";
import LocalDealCard from "./LocalDealCard";
import ReceiptAnalysisCard from "./ReceiptAnalysisCard";
import ConsensusLeaderboardCard from "./ConsensusLeaderboardCard";
import StockConsensusCard from "./StockConsensusCard";
import SectorConsensusCard from "./SectorConsensusCard";
import InvestmentThemeCard from "./InvestmentThemeCard";
import GroceryPlanCard from "./GroceryPlanCard";
import AllocationPlanCard from "./AllocationPlanCard";import ProactiveAlertCard from './ProactiveAlertCard';
import WeeklyDigestCard from './WeeklyDigestCard';
import FinancialHealthDashboard from './FinancialHealthDashboard';
import WealthProjectionCard from './WealthProjectionCard';
import FinancialTwinCard from './FinancialTwinCard';
import WealthRaceCard from './WealthRaceCard';
import AdvisorMatchCard from './AdvisorMatchCard';
import LifeEventSelector from './LifeEventSelector';
import MoneyMapCard from './MoneyMapCard';
import RippleTrackerCard from './RippleTrackerCard';
import RippleEffectCard from './RippleEffectCard';
import EconomicImpactCard from './EconomicImpactCard';
import DealPredictionCard from './DealPredictionCard';
import PurchaseTimingCard from './PurchaseTimingCard';
import { useChatStore } from "@/hooks/useChat";
import type { MarketIntelligenceReport, AnalystInsight, SectorOutlook } from "@/types/market";
import type { PriceComparison, StoreCategoryRanking, SubscriptionValue } from "@/types/pricing";
import type { GoalSimulationResult, BillPrediction, LocalDealReport, AnalyzedReceipt } from "@/types/tools";
import type { ConsensusLeaderboard, ConsensusRating, SectorConsensus, InvestmentTheme } from "@/types/investment";
import type { OptimizedGroceryPlan } from "@/lib/groceryPlanner";
import type { AllocationPlan } from "@/lib/allocationMapper";import type { ProactiveAlert, WeeklyDigest } from '@/lib/predictiveEngine';
import type { FinancialDNA } from '@/lib/financialDNA';
import type { WealthProjection } from '@/lib/wealthTrajectory';
import type { TwinSimulation } from '@/lib/financialTwin';
import type { WealthRaceProfile, WealthRaceLeaderboard } from '@/lib/wealthRace';
import type { AdvisorMatch } from '@/lib/advisorMarketplace';
import type { MoneyMapData, RippleTrackerData, RippleEffect } from '@/types/moneyMap';
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

interface MarketReportBlock {
  type: "market_report";
  report: MarketIntelligenceReport;
}

interface AnalystInsightBlock {
  type: "analyst_insight";
  insight: AnalystInsight;
}

interface SectorOutlookBlock {
  type: "sector_outlook";
  outlook: SectorOutlook;
}

interface PriceComparisonBlock {
  type: "price_comparison";
  comparison: PriceComparison;
}

interface StoreRankingBlock {
  type: "store_ranking";
  ranking: StoreCategoryRanking;
}

interface SubscriptionValueBlock {
  type: "subscription_value";
  subscriptions: SubscriptionValue[];
}

interface GoalSimulationBlock {
  type: "goal_simulation";
  result: GoalSimulationResult;
}

interface BillPredictionBlock {
  type: "bill_prediction";
  prediction: BillPrediction;
}

interface LocalDealsBlock {
  type: "local_deals";
  report: LocalDealReport;
}

interface ReceiptAnalysisBlock {
  type: "receipt_analysis";
  receipt: AnalyzedReceipt;
}

interface ConsensusLeaderboardBlock {
  type: "consensus_leaderboard";
  leaderboard: ConsensusLeaderboard;
}

interface StockConsensusBlock {
  type: "stock_consensus";
  stock: ConsensusRating;
}

interface SectorConsensusBlock {
  type: "sector_consensus";
  sector: SectorConsensus;
}

interface InvestmentThemeBlock {
  type: "investment_theme";
  theme: InvestmentTheme;
}

interface GroceryPlanBlock {
  type: "grocery_plan";
  plan: OptimizedGroceryPlan;
}

interface AllocationPlanBlock {
  type: "allocation_plan";
  plan: AllocationPlan;
}

interface ProactiveAlertBlock {
  type: "proactive_alert";
  alert: ProactiveAlert;
}

interface WeeklyDigestBlock {
  type: "weekly_digest";
  digest: WeeklyDigest;
}

interface FinancialHealthBlock {
  type: "financial_health";
  dna: FinancialDNA;
}

interface WealthProjectionBlock {
  type: "wealth_projection";
  projection: WealthProjection;
}

interface FinancialTwinBlock {
  type: "financial_twin";
  simulation: TwinSimulation;
}

interface WealthRaceBlock {
  type: "wealth_race";
  leaderboard: WealthRaceLeaderboard;
  profile: WealthRaceProfile;
}

interface AdvisorMatchBlock {
  type: "advisor_match";
  matches: AdvisorMatch[];
}

interface LifeEventSelectorBlock {
  type: "life_event_selector";
}

interface MoneyMapBlock {
  type: "money_map";
  data: MoneyMapData;
}

interface RippleTrackerBlock {
  type: "ripple_tracker";
  data: RippleTrackerData;
}

interface RippleEffectBlock {
  type: "ripple_effect";
  ripple: RippleEffect;
}

interface EconomicImpactBlock {
  type: "economic_impact";
  impact: import('@/types/economicIntel').PersonalEconomicImpact;
}

interface DealPredictionBlock {
  type: "deal_prediction";
  prediction: import('@/types/economicIntel').DealPrediction;
}

interface PurchaseTimingBlock {
  type: "purchase_timing";
  timing: import('@/types/economicIntel').PurchaseTimingAdvice;
}

type StructuredBlock =
  | CouponResultsBlock
  | ExpenseInputBlock
  | SavingsReportBlock
  | NegotiationScriptBlock
  | SpendToSaveBlock
  | MarketReportBlock
  | AnalystInsightBlock
  | SectorOutlookBlock
  | PriceComparisonBlock
  | StoreRankingBlock
  | SubscriptionValueBlock
  | GoalSimulationBlock
  | BillPredictionBlock
  | LocalDealsBlock
  | ReceiptAnalysisBlock
  | ConsensusLeaderboardBlock
  | StockConsensusBlock
  | SectorConsensusBlock
  | InvestmentThemeBlock
  | GroceryPlanBlock
  | AllocationPlanBlock
  | ProactiveAlertBlock
  | WeeklyDigestBlock
  | FinancialHealthBlock
  | WealthProjectionBlock
  | FinancialTwinBlock
  | WealthRaceBlock
  | AdvisorMatchBlock
  | LifeEventSelectorBlock
  | MoneyMapBlock
  | RippleTrackerBlock
  | RippleEffectBlock
  | EconomicImpactBlock
  | DealPredictionBlock
  | PurchaseTimingBlock;

const KNOWN_TYPES = new Set([
  "coupon_results",
  "expense_input",
  "savings_report",
  "negotiation_script",
  "spend_to_save",
  "market_report",
  "analyst_insight",
  "sector_outlook",
  "price_comparison",
  "store_ranking",
  "subscription_value",
  "goal_simulation",
  "bill_prediction",
  "local_deals",
  "receipt_analysis",
  "consensus_leaderboard",
  "stock_consensus",
  "sector_consensus",
  "investment_theme",
  "grocery_plan",
  "allocation_plan",
  "proactive_alert",
  "weekly_digest",
  "financial_health",
  "wealth_projection",
  "financial_twin",
  "wealth_race",
  "advisor_match",
  "life_event_selector",
  "money_map",
  "ripple_tracker",
  "ripple_effect",
  "economic_impact",
  "deal_prediction",
  "purchase_timing",
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

          case "market_report":
            return <MarketReportCard key={i} report={data.report} />;

          case "analyst_insight":
            return <AnalystInsightCard key={i} insight={data.insight} />;

          case "sector_outlook":
            return <SectorOutlookCard key={i} outlook={data.outlook} />;

          case "price_comparison":
            return <PriceComparisonCard key={i} comparison={data.comparison} />;

          case "store_ranking":
            return <StoreRankingCard key={i} ranking={data.ranking} />;

          case "subscription_value":
            return <SubscriptionValueCard key={i} subscriptions={data.subscriptions} />;

          case "goal_simulation":
            return <GoalSimulatorCard key={i} result={data.result} />;

          case "bill_prediction":
            return <BillPredictorCard key={i} prediction={data.prediction} />;

          case "local_deals":
            return <LocalDealCard key={i} report={data.report} />;

          case "receipt_analysis":
            return <ReceiptAnalysisCard key={i} receipt={data.receipt} />;

          case "consensus_leaderboard":
            return <ConsensusLeaderboardCard key={i} leaderboard={data.leaderboard} />;

          case "stock_consensus":
            return <StockConsensusCard key={i} stock={data.stock} />;

          case "sector_consensus":
            return <SectorConsensusCard key={i} sector={data.sector} />;

          case "investment_theme":
            return <InvestmentThemeCard key={i} theme={data.theme} />;

          case "grocery_plan":
            return <GroceryPlanCard key={i} plan={data.plan} />;

          case "allocation_plan":
            return <AllocationPlanCard key={i} plan={data.plan} />;

          case "proactive_alert":
            return <ProactiveAlertCard key={i} alert={data.alert} />;

          case "weekly_digest":
            return <WeeklyDigestCard key={i} digest={data.digest} />;

          case "financial_health":
            return <FinancialHealthDashboard key={i} dna={data.dna} />;

          case "wealth_projection":
            return <WealthProjectionCard key={i} projection={data.projection} />;

          case "financial_twin":
            return <FinancialTwinCard key={i} simulation={data.simulation} />;

          case "wealth_race":
            return <WealthRaceCard key={i} leaderboard={data.leaderboard} profile={data.profile} />;

          case "advisor_match":
            return (
              <div key={i} className="space-y-4">
                {data.matches.map((match, j) => (
                  <AdvisorMatchCard key={j} match={match} />
                ))}
              </div>
            );

          case "life_event_selector":
            return <LifeEventSelector key={i} onSelect={(evt) => sendMessage(`Simulate: ${evt}`)} />;

          case "money_map":
            return <MoneyMapCard key={i} data={data.data} />;

          case "ripple_tracker":
            return <RippleTrackerCard key={i} data={data.data} />;

          case "ripple_effect":
            return <RippleEffectCard key={i} ripple={data.ripple} />;

          case "economic_impact":
            return <EconomicImpactCard key={i} impact={data.impact} />;

          case "deal_prediction":
            return <DealPredictionCard key={i} prediction={data.prediction} />;

          case "purchase_timing":
            return <PurchaseTimingCard key={i} timing={data.timing} />;

          default:
            return null;
        }
      })}
    </div>
  );
}
