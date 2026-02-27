/* ── Predictive Engine — Richy's Proactive Intelligence ──────────────── */

import type { FinancialDNA } from "./financialDNA";

// ==========================================
// PROACTIVE ALERT
// ==========================================

export interface ProactiveAlert {
  id: string;
  type:
    | "savings_opportunity"
    | "bill_warning"
    | "price_drop"
    | "goal_milestone"
    | "subscription_check"
    | "investment_insight"
    | "behavioral_nudge"
    | "seasonal_tip"
    | "rate_change"
    | "renewal_reminder";

  priority: "urgent" | "high" | "medium" | "low";

  title: string;
  message: string;

  // Why Richy is bringing this up
  reasoning: string; // "Your car insurance renews in 30 days and you haven't shopped rates in 14 months"

  // What to do about it
  suggestedAction: string;
  estimatedValue: number; // Dollar value of acting on this

  // Timing
  relevantDate?: string;
  expiresAt?: string; // Alert becomes irrelevant after this date

  // Engagement
  actionButton?: { label: string; action: string }; // "Generate negotiation script", "Show me alternatives"
  dismissable: boolean;
}

// ==========================================
// ALERT RULE TEMPLATE
// ==========================================

interface AlertRuleTemplate {
  type: ProactiveAlert["type"];
  priority: ProactiveAlert["priority"];
  title: string;
  message: string;
  suggestedAction: string;
  estimatedValue: string | number;
}

export interface AlertRule {
  id: string;
  trigger: string;
  check: (dna: FinancialDNA) => boolean;
  template: Partial<AlertRuleTemplate>;
}

// ==========================================
// ALERT GENERATION RULES
// ==========================================

export const PROACTIVE_ALERT_RULES: AlertRule[] = [
  {
    id: "insurance_renewal",
    trigger: "Car or home insurance renewal within 45 days",
    check: (dna: FinancialDNA) => {
      // Check if insurance renewal is approaching
      // Check if user has shopped rates in last 12 months
      const events = dna.predictions.upcomingFinancialEvents;
      return events.some(
        (e) =>
          e.event.toLowerCase().includes("insurance") &&
          daysBetween(new Date(), new Date(e.date)) <= 45,
      );
    },
    template: {
      type: "renewal_reminder",
      priority: "high",
      title: "Insurance renewal approaching",
      message:
        "Your {type} insurance renews on {date}. You haven't compared rates in {months} months. Shopping around typically saves 15-25%.",
      suggestedAction:
        "Want me to prepare your current coverage details in a format you can send to competitors for quotes?",
      estimatedValue: "15-25% of annual premium",
    },
  },
  {
    id: "subscription_unused",
    trigger: "User hasn't mentioned using a subscription in 60+ days",
    check: (dna: FinancialDNA) => {
      // Check lastMentioned date on each subscription
      const subs = dna.spendingFingerprint.activeSubscriptions;
      return subs.some(
        (s) => s.lastMentioned && daysBetween(new Date(s.lastMentioned), new Date()) > 60,
      );
    },
    template: {
      type: "subscription_check",
      priority: "medium",
      title: "Still using {service}?",
      message:
        "You haven't mentioned {service} (${amount}/mo) in over 2 months. That's ${wasted} potentially unused. Want to keep it or cut it?",
      suggestedAction: "Cancel and save ${annual}/year",
      estimatedValue: "annualCost",
    },
  },
  {
    id: "bill_spike",
    trigger: "A known bill increased by more than 10%",
    check: (_dna: FinancialDNA) => {
      // Compare current bill amounts to historical
      // Requires bill history tracking — stub returns false until wired
      return false;
    },
    template: {
      type: "bill_warning",
      priority: "high",
      title: "{bill} went up",
      message:
        "Your {bill} increased from ${old} to ${new} — that's a {percent}% jump. This happens when promotional rates expire.",
      suggestedAction:
        "Want me to generate a negotiation script to get the price back down?",
      estimatedValue: "difference × 12",
    },
  },
  {
    id: "goal_milestone",
    trigger: "User crosses 25%, 50%, or 75% of a savings goal",
    check: (dna: FinancialDNA) => {
      // Check goal progress
      return dna.goals.active.some((g) => {
        const pct = g.targetAmount > 0 ? (g.currentProgress / g.targetAmount) * 100 : 0;
        return [25, 50, 75].some((m) => pct >= m && pct < m + 5);
      });
    },
    template: {
      type: "goal_milestone",
      priority: "medium",
      title: "Milestone: {goal} is {percent}% funded!",
      message:
        "You've saved ${current} of your ${target} {goal} goal. At your current pace, you'll hit it by {date}. Keep going!",
      suggestedAction: "Want to see ways to get there faster?",
      estimatedValue: 0,
    },
  },
  {
    id: "seasonal_savings",
    trigger: "Calendar-based seasonal opportunity",
    check: (_dna: FinancialDNA) => {
      // Check current month for seasonal tips
      const month = new Date().getMonth(); // 0-indexed
      // January(0): tax prep, March(2): spring clean, May(4): insurance,
      // November(10): Black Friday, December(11): tax-loss harvesting
      return [0, 2, 4, 10, 11].includes(month);
    },
    template: {
      type: "seasonal_tip",
      priority: "low",
      title: "Seasonal money move",
      // January: tax prep booking, gym membership negotiation
      // March: spring cleaning = cancel unused services
      // May: insurance shopping season
      // November: annual subscription deals (Black Friday)
      // December: tax-loss harvesting, charitable giving deadline
    },
  },
  {
    id: "emergency_fund_low",
    trigger: "Emergency fund covers less than 1 month of expenses",
    check: (dna: FinancialDNA) => {
      return dna.wealthProfile.emergencyFund.monthsCovered < 1;
    },
    template: {
      type: "savings_opportunity",
      priority: "urgent",
      title: "Your emergency fund needs attention",
      message:
        "Your emergency fund covers {months} months of expenses. Financial experts recommend 3-6 months. Even adding ${daily}/day gets you to 1 month coverage by {date}.",
      suggestedAction:
        "Want me to find ${monthly} in your budget to redirect to your emergency fund?",
      estimatedValue: 0,
    },
  },
  {
    id: "debt_optimization",
    trigger:
      "User is paying minimum on high-interest debt while holding low-yield savings above emergency fund level",
    check: (dna: FinancialDNA) => {
      // High interest debt + excess savings
      const hasHighInterestDebt = dna.debtProfile.debts.some(
        (d) => d.interestRate > 10 && d.actualPayment <= d.minimumPayment,
      );
      const hasExcessSavings =
        dna.wealthProfile.totalSavings >
        dna.cashFlow.monthlyExpenses * 6;
      return hasHighInterestDebt && hasExcessSavings;
    },
    template: {
      type: "savings_opportunity",
      priority: "high",
      title: "Your savings are costing you money",
      message:
        "You have ${excess} in savings earning {savingsRate}% while carrying ${debt} in credit card debt at {debtRate}%. Paying down the debt first would save you ${interestSaved}/year in interest.",
      suggestedAction:
        "Want me to run the numbers on an optimal debt payoff plan?",
      estimatedValue: "interestSaved",
    },
  },
  {
    id: "investment_opportunity",
    trigger: "User has surplus cash and no active investment plan",
    check: (dna: FinancialDNA) => {
      // monthlySurplus > 200 AND no investment activity
      return (
        dna.cashFlow.monthlySurplus > 200 &&
        (dna.wealthProfile.investmentStyle === "not_investing" ||
          !dna.wealthProfile.investmentStyle)
      );
    },
    template: {
      type: "investment_insight",
      priority: "medium",
      title: "Your surplus could be working harder",
      message:
        "You have ~${surplus}/month left over after expenses. In a savings account at {rate}%, that grows to ${savings5yr} in 5 years. Historically, a diversified index fund has averaged ~10%, which would grow to ${invested5yr}. That's a ${difference} difference.",
      suggestedAction: "Want me to build an allocation plan for your surplus?",
      estimatedValue: "difference",
    },
  },
  {
    id: "employer_match",
    trigger: "User has 401k but isn't getting full employer match",
    check: (dna: FinancialDNA) => {
      // 401k contribution < employer match threshold
      return dna.wealthProfile.retirementAccounts.some(
        (a) =>
          a.type.toLowerCase().includes("401k") &&
          a.employerMatch > 0 &&
          a.monthlyContribution < a.employerMatch,
      );
    },
    template: {
      type: "savings_opportunity",
      priority: "urgent",
      title: "You're leaving free money on the table",
      message:
        "Your employer matches {matchPercent}% up to {matchCap}. You're currently contributing ${current}/month. Increasing to ${needed}/month would capture ${freeMoneyPerYear}/year in free employer contributions. That's literally free money.",
      suggestedAction:
        "Want me to show you where to find the extra ${difference}/month in your budget?",
      estimatedValue: "freeMoneyPerYear",
    },
  },
];

// ==========================================
// WEEKLY DIGEST
// ==========================================

export interface WeeklyDigest {
  userId: string;
  weekOf: string;

  // Scores update
  healthScoreChange: number; // +/- from last week

  // Key events
  savingsThisWeek: number;
  spendingThisWeek: number;
  goalsProgress: { name: string; progress: number; change: number }[];

  // Alerts
  activeAlerts: ProactiveAlert[];

  // Wins
  winsThisWeek: string[]; // "Cancelled Peacock — saving $72/year", "Negotiated internet down $25/mo"

  // Next week preview
  upcomingBills: { name: string; amount: number; date: string }[];
  upcomingOpportunities: string[];

  // Motivation
  totalSavedSinceJoining: number;
  totalSavedThisMonth: number;
  streakDays: number; // Days in a row the user engaged
}

// ==========================================
// HELPERS
// ==========================================

/** Calendar days between two dates (absolute). */
function daysBetween(a: Date, b: Date): number {
  const ms = Math.abs(b.getTime() - a.getTime());
  return Math.floor(ms / (1000 * 60 * 60 * 24));
}

/** Run every rule against a user's DNA and collect triggered alerts. */
export function generateAlerts(dna: FinancialDNA): ProactiveAlert[] {
  const alerts: ProactiveAlert[] = [];

  for (const rule of PROACTIVE_ALERT_RULES) {
    try {
      if (rule.check(dna)) {
        alerts.push({
          id: `${rule.id}_${Date.now()}`,
          type: (rule.template.type ?? "behavioral_nudge") as ProactiveAlert["type"],
          priority: (rule.template.priority ?? "medium") as ProactiveAlert["priority"],
          title: rule.template.title ?? rule.trigger,
          message: rule.template.message ?? "",
          reasoning: rule.trigger,
          suggestedAction: rule.template.suggestedAction ?? "",
          estimatedValue:
            typeof rule.template.estimatedValue === "number"
              ? rule.template.estimatedValue
              : 0,
          dismissable: true,
        });
      }
    } catch {
      // Rule evaluation failed — skip silently
    }
  }

  // Sort: urgent → high → medium → low
  const priorityOrder: Record<string, number> = {
    urgent: 0,
    high: 1,
    medium: 2,
    low: 3,
  };
  alerts.sort(
    (a, b) => (priorityOrder[a.priority] ?? 3) - (priorityOrder[b.priority] ?? 3),
  );

  return alerts;
}

/** Build an empty weekly digest scaffold for a user. */
export function createEmptyDigest(userId: string): WeeklyDigest {
  return {
    userId,
    weekOf: new Date().toISOString().slice(0, 10),
    healthScoreChange: 0,
    savingsThisWeek: 0,
    spendingThisWeek: 0,
    goalsProgress: [],
    activeAlerts: [],
    winsThisWeek: [],
    upcomingBills: [],
    upcomingOpportunities: [],
    totalSavedSinceJoining: 0,
    totalSavedThisMonth: 0,
    streakDays: 0,
  };
}
