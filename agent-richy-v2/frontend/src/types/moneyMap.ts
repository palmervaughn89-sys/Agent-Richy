// ==========================================
// THE MONEY MAP — Your financial ecosystem visualized
// ==========================================

export type FlowCategory =
  | "income_salary" | "income_freelance" | "income_side" | "income_investment" | "income_other"
  | "housing" | "utilities" | "transportation" | "food_groceries" | "food_dining"
  | "insurance" | "healthcare" | "debt_payments" | "subscriptions" | "personal_care"
  | "clothing" | "entertainment" | "kids" | "pets" | "gifts"
  | "savings_emergency" | "savings_goals" | "investing_retirement" | "investing_brokerage"
  | "taxes" | "fees" | "miscellaneous";

export type FlowDirection = "inflow" | "outflow" | "transfer";

export interface MoneyFlow {
  id: string;
  name: string;
  category: FlowCategory;
  direction: FlowDirection;
  monthlyAmount: number;
  percentOfIncome: number;

  // Visual properties
  streamWidth: number;                     // Proportional to amount — thicker = more money
  color: string;                           // Color-coded by health
  healthStatus: "healthy" | "caution" | "warning" | "critical";

  // Context
  benchmark: number;                       // What similar people spend (from Financial DNA peers)
  vsAverage: number;                       // Percentage above/below average (+15% = 15% more than peers)
  trend: "increasing" | "stable" | "decreasing";

  // Sub-flows (drill down)
  subFlows?: {
    name: string;
    amount: number;
    percentage: number;                    // Of parent flow
  }[];

  // Optimization potential
  optimizationAvailable: boolean;
  potentialSavings: number;
  optimizationNote?: string;               // "Your internet is $30 above market rate"
}

export interface MoneyMapData {
  userId: string;
  generatedAt: string;
  period: string;                          // "February 2026"

  // The big numbers
  totalInflow: number;
  totalOutflow: number;
  netFlow: number;                         // Positive = surplus, negative = deficit

  // All flows
  inflows: MoneyFlow[];
  outflows: MoneyFlow[];
  transfers: MoneyFlow[];                  // Money moving between accounts (savings, investing)

  // Flow health analysis
  healthScore: number;                     // 1-100

  // The "drain" — where money disappears without value
  leaks: {
    name: string;
    amount: number;
    annualImpact: number;
    description: string;                   // "Unused gym membership — $0 value for $45/month"
    fixDifficulty: "easy" | "medium" | "hard";
  }[];
  totalLeakage: number;

  // The "dam" — money that should be flowing somewhere but isn't
  blockedFlows: {
    name: string;
    shouldBe: number;                      // What they should be putting toward this
    currentlyIs: number;
    gap: number;
    description: string;                   // "You're not capturing $3,200/year in employer 401k match"
  }[];
  totalBlockedValue: number;

  // Historical comparison
  vsLastMonth: {
    inflowChange: number;
    outflowChange: number;
    netFlowChange: number;
    categoriesIncreased: { category: string; amount: number }[];
    categoriesDecreased: { category: string; amount: number }[];
  };

  // Sankey diagram data (for the visualization)
  sankeyNodes: {
    id: string;
    name: string;
    value: number;
    color: string;
    column: number;                        // 0=income, 1=categories, 2=subcategories, 3=destinations
  }[];
  sankeyLinks: {
    source: string;
    target: string;
    value: number;
    color: string;
  }[];
}

// ==========================================
// THE RIPPLE TRACKER — Every decision echoes
// ==========================================

export interface RippleEffect {
  id: string;
  trigger: string;                         // "Cancelled Peacock subscription"
  triggerDate: string;
  monthlySavings: number;

  // The ripple chain — how this small decision echoes across time
  ripples: {
    timeframe: string;                     // "This month", "This year", "5 years", "10 years", "At retirement"
    amount: number;                        // Raw savings at this timeframe
    investedAmount: number;                // If invested at 7% annual return
    description: string;                   // "In 10 years, this $7.99/month becomes $1,383 invested"
    milestone?: string;                    // "That's a round-trip flight to Miami"
  }[];

  // Connection to goals
  goalImpact: {
    goalName: string;
    timeSaved: string;                     // "Reach your emergency fund 2 weeks sooner"
    percentageBoost: number;               // How much faster this gets you to the goal
  }[];

  // Connection to other metrics
  metricsImpact: {
    savingsRateChange: number;             // +0.3% savings rate
    debtFreeAcceleration: number;          // Days sooner to debt free
    retirementAcceleration: number;        // Days sooner to retirement
    dailyEquivalent: number;               // "That's $0.27/day working for your future"
  };
}

export interface InvisibleRaise {
  userId: string;
  generatedAt: string;

  // The headline number
  totalAnnualSavings: number;              // Sum of all optimizations found
  equivalentPreTaxRaise: number;           // Adjusted for tax bracket (~30% more)
  effectiveHourlyRaise: number;            // Total / 2080 work hours

  // How it breaks down
  optimizations: {
    id: string;
    description: string;
    dateFound: string;
    status: "implemented" | "pending" | "dismissed";
    monthlySavings: number;
    annualSavings: number;
    category: string;
    rippleId: string;                      // Links to the RippleEffect
  }[];

  // Implemented vs potential
  implementedSavings: number;              // Confirmed actions taken
  pendingSavings: number;                  // Suggested but not yet acted on
  dismissedSavings: number;               // User said no

  // The compound story
  compoundProjection: {
    year1: number;                         // First year savings
    year5: number;                         // 5 years of savings invested
    year10: number;
    year20: number;
    year30: number;                        // 30 years invested at 7%
    retirementImpact: number;              // Total addition to retirement
  };

  // The emotional hook
  equivalentTo: {
    description: string;
    icon: string;
  }[];
  // Examples:
  // "$4,230/year = a vacation to Cancun every year"
  // "$4,230/year = a new iPhone every 3 months"
  // "$4,230/year invested for 30 years = $401,000 at retirement"
  // "$4,230/year = $11.59/day working for you"

  // Progress over time
  monthlyHistory: {
    month: string;
    cumulativeSavings: number;
    newOptimizations: number;
    raiseAmount: number;                   // Running total of annual savings
  }[];

  // Milestone celebrations
  milestones: {
    name: string;
    threshold: number;
    reached: boolean;
    reachedDate?: string;
    icon: string;
  }[];
  // "$100 raise" → "$500 raise" → "$1,000 raise" → "$2,500 raise" → "$5,000 raise" → "$10,000 raise"
}

// Combined view for the Ripple Tracker feature
export interface RippleTrackerData {
  invisibleRaise: InvisibleRaise;
  recentRipples: RippleEffect[];

  // The power statement
  powerStatement: string;
  // "Since joining Richy 47 days ago, you've given yourself a $4,230 raise.
  //  That's $11.59/day. Invested over 30 years, that becomes $401,000.
  //  All from decisions that took less than 5 minutes."
}
