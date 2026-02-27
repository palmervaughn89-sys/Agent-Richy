/* ── Spending Pipeline — intake state machine & analysis engine ──────── */

// ==========================================
// DATA COLLECTION REQUIREMENTS
// ==========================================

// Every field Richy needs to do a complete spending analysis.
// Fields marked REQUIRED must be collected before analysis runs.
// Fields marked OPTIONAL improve analysis quality.

export interface SpendingIntakeState {
  // PHASE 1: Income & basics
  income: {
    monthlyTakeHome: number | null;           // REQUIRED — after-tax monthly income
    payFrequency: "weekly" | "biweekly" | "semi_monthly" | "monthly" | null;  // REQUIRED
    additionalIncome: number | null;           // OPTIONAL — side gigs, freelance, etc.
    householdSize: number | null;              // REQUIRED — affects benchmarking
    zipCode: string | null;                    // OPTIONAL — affects cost of living adjustments
    collected: boolean;
  };

  // PHASE 2: Fixed expenses (bills that don't change month to month)
  fixedExpenses: {
    housing: {
      type: "rent" | "mortgage" | "living_with_family" | null;  // REQUIRED
      amount: number | null;                   // REQUIRED (0 if living with family)
      includesUtilities: boolean | null;       // REQUIRED
    };
    utilities: {
      electric: { amount: number | null; isEstimate: boolean };
      gas: { amount: number | null; isEstimate: boolean };
      water: { amount: number | null; isEstimate: boolean };
      trash: { amount: number | null; isEstimate: boolean };
      sewer: { amount: number | null; isEstimate: boolean };
    };
    insurance: {
      health: { amount: number | null; throughEmployer: boolean | null };
      car: { amount: number | null; frequency: string | null; provider: string | null };
      renters_homeowners: { amount: number | null; provider: string | null };
      life: { amount: number | null };
      other: { description: string; amount: number }[];
    };
    transportation: {
      carPayment: number | null;
      gasPerMonth: number | null;
      publicTransit: number | null;
      parking: number | null;
      rideshare: number | null;              // Uber/Lyft monthly average
      carInsuranceIncluded: boolean;         // Already counted in insurance?
    };
    telecom: {
      phone: { amount: number | null; carrier: string | null; linesCount: number | null };
      internet: { amount: number | null; provider: string | null; speed: string | null };
      cable: { amount: number | null; provider: string | null };
    };
    loans: {
      studentLoans: { amount: number | null; totalBalance: number | null; interestRate: number | null };
      personalLoans: { amount: number | null; totalBalance: number | null; interestRate: number | null };
      creditCards: {
        cards: {
          name: string;
          balance: number;
          minimumPayment: number;
          interestRate: number;
          actualPayment: number;              // What they actually pay monthly
        }[];
      };
      otherDebt: { description: string; amount: number; balance: number; rate: number }[];
    };
    collected: boolean;
  };

  // PHASE 3: Subscriptions (the gold mine for savings)
  subscriptions: {
    streaming: { name: string; amount: number; plan: string; frequency: "monthly" | "annual"; hoursPerMonth: number | null; sharedWith: number }[];
    music: { name: string; amount: number; frequency: "monthly" | "annual"; hoursPerMonth: number | null }[];
    gaming: { name: string; amount: number; frequency: "monthly" | "annual"; hoursPerMonth: number | null }[];
    news_reading: { name: string; amount: number; frequency: "monthly" | "annual" }[];
    cloud_storage: { name: string; amount: number; gbUsed: number | null; gbTotal: number | null }[];
    fitness: { name: string; amount: number; visitsPerMonth: number | null; type: "gym" | "app" | "class" }[];
    productivity: { name: string; amount: number; forWork: boolean }[];
    food_delivery: { name: string; amount: number; ordersPerMonth: number | null }[];
    membership_clubs: { name: string; amount: number; frequency: "monthly" | "annual" }[];
    other: { name: string; amount: number; category: string; frequency: "monthly" | "annual" }[];
    collected: boolean;
  };

  // PHASE 4: Variable spending (harder to track but critical)
  variableSpending: {
    groceries: { monthlyAverage: number | null; primaryStore: string | null; secondaryStores: string[] };
    diningOut: { monthlyAverage: number | null; timesPerWeek: number | null };
    coffee: { monthlyAverage: number | null; timesPerWeek: number | null; usualSpend: number | null };
    clothing: { monthlyAverage: number | null };
    entertainment: { monthlyAverage: number | null };  // Movies, events, hobbies
    personalCare: { monthlyAverage: number | null };    // Haircuts, products, etc.
    pets: { monthlyAverage: number | null; type: string | null };
    kids: { monthlyAverage: number | null; childcare: number | null; activities: number | null };
    gifts: { monthlyAverage: number | null };
    miscellaneous: { monthlyAverage: number | null };
    collected: boolean;
  };

  // PHASE 5: Savings & financial goals (for complete picture)
  savings: {
    emergencyFund: { balance: number | null; target: number | null };
    savingsAccount: { balance: number | null; monthlyContribution: number | null; apy: number | null };
    retirement: {
      has401k: boolean | null;
      monthlyContribution: number | null;
      employerMatch: number | null;         // Percentage or dollar amount
      currentBalance: number | null;
    };
    ira: { type: "traditional" | "roth" | null; balance: number | null; annualContribution: number | null };
    otherInvestments: { description: string; balance: number; monthlyContribution: number }[];
    collected: boolean;
  };

  // META
  completionPercentage: number;              // 0-100
  currentPhase: 1 | 2 | 3 | 4 | 5;
  missingCritical: string[];                 // List of REQUIRED fields still missing
  missingOptional: string[];                 // List of OPTIONAL fields still missing
  readyForAnalysis: boolean;                 // True when all REQUIRED fields collected
  startedAt: string;
  lastUpdatedAt: string;
}

// ==========================================
// ANALYSIS METRICS (what Richy calculates)
// ==========================================

export interface SpendingAnalysisMetrics {
  // Top-level financial health
  totalMonthlyIncome: number;
  totalMonthlyExpenses: number;
  monthlySurplus: number;                    // Income - expenses (can be negative)
  savingsRate: number;                       // % of income saved

  // Ratio analysis
  housingRatio: number;                      // Housing / income (target: <30%)
  debtToIncomeRatio: number;                 // Total debt payments / income (target: <36%)
  essentialExpenseRatio: number;             // Fixed + essential / income (target: <50%)
  discretionaryRatio: number;               // Variable spending / income
  savingsRatio: number;                      // Savings / income (target: >20%)

  // 50/30/20 analysis
  needs: { amount: number; percentage: number; target: 50; status: "on_track" | "over" | "under" };
  wants: { amount: number; percentage: number; target: 30; status: "on_track" | "over" | "under" };
  savingsDebt: { amount: number; percentage: number; target: 20; status: "on_track" | "over" | "under" };

  // Spending health scores (1-100)
  overallHealthScore: number;
  subscriptionEfficiency: number;            // Based on cost-per-hour and redundancy
  billOptimizationScore: number;             // How close to market rates
  debtManagementScore: number;               // Payoff strategy, interest minimization
  savingsScore: number;                      // Emergency fund coverage, retirement track

  // Debt analysis
  totalDebt: number;
  weightedAverageInterestRate: number;
  minimumMonthlyDebtPayment: number;
  debtFreeDate: string;                      // At current payment rate
  acceleratedDebtFreeDate: string;           // With avalanche method
  interestSavedByAccelerating: number;

  // Subscription analysis
  totalSubscriptionCost: number;
  subscriptionCostPerHour: number;           // Weighted average across all subs
  redundantSubscriptions: { services: string[]; combinedCost: number; suggestion: string }[];
  unusedSubscriptions: { name: string; cost: number; evidence: string }[];
  annualSavingsOpportunities: { name: string; currentMonthly: number; annualEffective: number; savings: number }[];

  // Bill optimization
  billsBelowMarket: { name: string; userPays: number; marketAvg: number }[];
  billsAboveMarket: { name: string; userPays: number; marketAvg: number; potentialSavings: number; negotiationLikelihood: "high" | "medium" | "low" }[];

  // Spending patterns
  topSpendingCategories: { category: string; amount: number; percentage: number }[];
  costOfLivingIndex: number;                 // Compared to national average (100 = average)
  lifestyleCostPerDay: number;               // Total expenses / 30

  // Projections
  annualExpenses: number;
  fiveYearExpenseProjection: number;         // With inflation
  savingsIn1Year: number;                    // At current rate
  savingsIn5Years: number;                   // With compound interest

  // Optimization roadmap
  totalPotentialMonthlySavings: number;
  totalPotentialAnnualSavings: number;
  optimizationActions: OptimizationAction[];
}

export interface OptimizationAction {
  id: string;
  priority: number;                          // 1 = highest priority
  category: "cancel" | "downgrade" | "negotiate" | "switch" | "consolidate" | "refinance" | "automate" | "spend_to_save" | "free_alternative" | "behavioral";
  title: string;
  description: string;
  currentCost: number;
  optimizedCost: number;
  monthlySavings: number;
  annualSavings: number;
  effortLevel: 1 | 2 | 3 | 4 | 5;
  timeToImplement: string;                   // "5 minutes", "1 phone call", "1 week"
  timeToRealizeSavings: string;              // "Immediate", "Next billing cycle", "30 days"
  confidence: "high" | "medium" | "low";

  // Actionable details
  steps: string[];                           // Step-by-step instructions
  script?: string;                           // Negotiation script if applicable
  alternativeService?: string;
  alternativePrice?: number;
  link?: string;                             // URL to take action

  // Impact on other metrics
  impactOnSavingsRate: number;               // How many percentage points this adds to savings rate
  cumulativeAnnualSavings: number;           // Running total if all higher-priority actions also taken
}

// ==========================================
// INTAKE FLOW ENGINE
// ==========================================

// Questions Richy asks, organized by phase
export const INTAKE_QUESTIONS: Record<number, {
  phase: string;
  intro: string;
  questions: {
    field: string;
    question: string;
    followUps: string[];
    required: boolean;
    validationRule?: string;
  }[];
}> = {
  1: {
    phase: "Income & Basics",
    intro: "Let's start with the big picture. I need to understand what's coming in before we look at what's going out.",
    questions: [
      {
        field: "income.monthlyTakeHome",
        question: "What's your monthly take-home pay? That's after taxes and deductions — the amount that actually hits your bank account.",
        followUps: ["Is that from one job or multiple?", "Do you get paid weekly, biweekly, or monthly?"],
        required: true,
      },
      {
        field: "income.householdSize",
        question: "How many people are in your household? Just you, or are you supporting others?",
        followUps: ["Any kids? Their expenses affect the analysis a lot."],
        required: true,
      },
      {
        field: "income.additionalIncome",
        question: "Any side income? Freelance, gig work, rental income, anything else coming in?",
        followUps: [],
        required: false,
      },
      {
        field: "income.zipCode",
        question: "What's your zip code? This helps me compare your costs to local averages instead of national ones.",
        followUps: [],
        required: false,
      },
    ],
  },
  2: {
    phase: "Fixed Monthly Bills",
    intro: "Now let's map out your fixed costs — the bills that hit every month whether you like it or not.",
    questions: [
      {
        field: "fixedExpenses.housing",
        question: "What's your housing situation? Renting, own with a mortgage, or living with family?",
        followUps: ["What's the monthly amount?", "Does that include any utilities?"],
        required: true,
      },
      {
        field: "fixedExpenses.utilities",
        question: "Let's go through utilities. Roughly what do you pay for electric, gas, water? Even estimates are fine — I'll note them as estimates.",
        followUps: ["Do you have separate water/sewer/trash bills?"],
        required: true,
      },
      {
        field: "fixedExpenses.telecom",
        question: "Phone and internet — who are your providers and what do you pay monthly?",
        followUps: ["How many lines on your phone plan?", "What internet speed do you get?", "Still paying for cable?"],
        required: true,
      },
      {
        field: "fixedExpenses.insurance",
        question: "Insurance — what are you covered for? Car, health, renters/homeowners? Give me the monthly or per-payment amounts.",
        followUps: ["Is health insurance through your employer or individual?", "When does your car insurance renew?"],
        required: true,
      },
      {
        field: "fixedExpenses.transportation",
        question: "Transportation costs — car payment, gas per month, parking, public transit, rideshares?",
        followUps: ["How many miles do you drive roughly?"],
        required: true,
      },
      {
        field: "fixedExpenses.loans",
        question: "Any debt payments? Student loans, credit cards, personal loans? For each one I need: the monthly payment, total balance, and interest rate.",
        followUps: ["Are you paying minimums or more?", "What's the interest rate on each card?"],
        required: true,
      },
    ],
  },
  3: {
    phase: "Subscriptions",
    intro: "Subscriptions are where most people have no idea how much they're actually spending. Let's go through every single one.",
    questions: [
      {
        field: "subscriptions.streaming",
        question: "Streaming services — Netflix, Hulu, Disney+, HBO, Peacock, Paramount+, Apple TV+, Amazon Prime? List every one, even the ones you forgot about.",
        followUps: ["Which tier/plan on each?", "How many hours per week do you actually watch each one?", "Are you sharing any of these accounts?"],
        required: true,
      },
      {
        field: "subscriptions.music",
        question: "Music — Spotify, Apple Music, YouTube Premium, Tidal? And how much do you actually listen?",
        followUps: ["Individual or family plan?"],
        required: true,
      },
      {
        field: "subscriptions.fitness",
        question: "Fitness — gym membership, Peloton, any fitness apps? How often do you actually go or use them?",
        followUps: ["When was the last time you went to the gym?", "How many visits per month?"],
        required: true,
      },
      {
        field: "subscriptions.all_other",
        question: "Any other subscriptions? Cloud storage (iCloud, Google One, Dropbox), gaming (Xbox Game Pass, PlayStation Plus), news (NYT, WSJ), food delivery memberships (DashPass, Uber One), productivity apps, VPNs, anything else?",
        followUps: ["Check your bank statement — any recurring charges you might have forgotten?"],
        required: true,
      },
    ],
  },
  4: {
    phase: "Variable Spending",
    intro: "Now the trickier part — spending that changes month to month. Estimates are fine, I just need the ballpark.",
    questions: [
      {
        field: "variableSpending.groceries",
        question: "Groceries — roughly how much per month, and where do you usually shop?",
        followUps: ["Do you meal plan or buy as you go?", "How often do you grocery shop per month?"],
        required: true,
      },
      {
        field: "variableSpending.diningOut",
        question: "Dining out and takeout — how many times per week and roughly what do you spend per outing?",
        followUps: ["Does that include food delivery orders?", "Coffee shop visits too?"],
        required: true,
      },
      {
        field: "variableSpending.other_variable",
        question: "Last few categories — roughly how much per month on: clothing, entertainment/hobbies, personal care (haircuts, products), pets, kids activities, gifts?",
        followUps: ["Any regular expensive hobbies?", "Big upcoming expenses in the next 3 months?"],
        required: false,
      },
    ],
  },
  5: {
    phase: "Savings & Goals",
    intro: "Almost done. Let's see what you're doing on the savings and investment side.",
    questions: [
      {
        field: "savings.emergencyFund",
        question: "Do you have an emergency fund? If so, how much is in it?",
        followUps: ["What's your target? General rule is 3-6 months of expenses."],
        required: true,
      },
      {
        field: "savings.retirement",
        question: "Are you contributing to a 401k or IRA? How much per month, and does your employer match?",
        followUps: ["What percentage does your employer match?", "Are you getting the full match? Because that's literally free money."],
        required: true,
      },
      {
        field: "savings.other",
        question: "Any other savings or investments? Brokerage account, savings goals you're working toward?",
        followUps: [],
        required: false,
      },
    ],
  },
};

// ==========================================
// REQUIRED FIELD REGISTRY
// ==========================================

interface RequiredFieldDef {
  path: string;
  phase: 1 | 2 | 3 | 4 | 5;
  label: string;
  required: boolean;
}

const FIELD_REGISTRY: RequiredFieldDef[] = [
  // Phase 1 — Income
  { path: "income.monthlyTakeHome", phase: 1, label: "Monthly take-home pay", required: true },
  { path: "income.payFrequency", phase: 1, label: "Pay frequency", required: true },
  { path: "income.householdSize", phase: 1, label: "Household size", required: true },
  { path: "income.additionalIncome", phase: 1, label: "Additional income", required: false },
  { path: "income.zipCode", phase: 1, label: "Zip code", required: false },
  // Phase 2 — Fixed expenses
  { path: "fixedExpenses.housing.type", phase: 2, label: "Housing type", required: true },
  { path: "fixedExpenses.housing.amount", phase: 2, label: "Housing cost", required: true },
  { path: "fixedExpenses.housing.includesUtilities", phase: 2, label: "Utilities included in housing", required: true },
  { path: "fixedExpenses.utilities.electric.amount", phase: 2, label: "Electric bill", required: true },
  { path: "fixedExpenses.telecom.phone.amount", phase: 2, label: "Phone bill", required: true },
  { path: "fixedExpenses.telecom.internet.amount", phase: 2, label: "Internet bill", required: true },
  { path: "fixedExpenses.insurance.car.amount", phase: 2, label: "Car insurance", required: true },
  { path: "fixedExpenses.transportation.carPayment", phase: 2, label: "Car payment", required: true },
  { path: "fixedExpenses.transportation.gasPerMonth", phase: 2, label: "Gas per month", required: true },
  { path: "fixedExpenses.loans.studentLoans.amount", phase: 2, label: "Student loan payment", required: true },
  // Phase 3 — Subscriptions (collected flag is the gate)
  { path: "subscriptions.collected", phase: 3, label: "Subscriptions inventory", required: true },
  // Phase 4 — Variable spending
  { path: "variableSpending.groceries.monthlyAverage", phase: 4, label: "Monthly groceries", required: true },
  { path: "variableSpending.diningOut.monthlyAverage", phase: 4, label: "Monthly dining out", required: true },
  // Phase 5 — Savings
  { path: "savings.emergencyFund.balance", phase: 5, label: "Emergency fund balance", required: true },
  { path: "savings.retirement.has401k", phase: 5, label: "401k status", required: true },
  { path: "savings.retirement.monthlyContribution", phase: 5, label: "Retirement contribution", required: true },
];

// ==========================================
// UTILITY: deep-get a value by dot path
// ==========================================

function getByPath(obj: unknown, path: string): unknown {
  const keys = path.split(".");
  let current: unknown = obj;
  for (const key of keys) {
    if (current == null || typeof current !== "object") return undefined;
    current = (current as Record<string, unknown>)[key];
  }
  return current;
}

function isFieldCollected(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === "string" && value.trim() === "") return false;
  return true;
}

// ==========================================
// CREATE EMPTY STATE
// ==========================================

export function createEmptyIntakeState(): SpendingIntakeState {
  const now = new Date().toISOString();
  return {
    income: {
      monthlyTakeHome: null,
      payFrequency: null,
      additionalIncome: null,
      householdSize: null,
      zipCode: null,
      collected: false,
    },
    fixedExpenses: {
      housing: { type: null, amount: null, includesUtilities: null },
      utilities: {
        electric: { amount: null, isEstimate: false },
        gas: { amount: null, isEstimate: false },
        water: { amount: null, isEstimate: false },
        trash: { amount: null, isEstimate: false },
        sewer: { amount: null, isEstimate: false },
      },
      insurance: {
        health: { amount: null, throughEmployer: null },
        car: { amount: null, frequency: null, provider: null },
        renters_homeowners: { amount: null, provider: null },
        life: { amount: null },
        other: [],
      },
      transportation: {
        carPayment: null,
        gasPerMonth: null,
        publicTransit: null,
        parking: null,
        rideshare: null,
        carInsuranceIncluded: false,
      },
      telecom: {
        phone: { amount: null, carrier: null, linesCount: null },
        internet: { amount: null, provider: null, speed: null },
        cable: { amount: null, provider: null },
      },
      loans: {
        studentLoans: { amount: null, totalBalance: null, interestRate: null },
        personalLoans: { amount: null, totalBalance: null, interestRate: null },
        creditCards: { cards: [] },
        otherDebt: [],
      },
      collected: false,
    },
    subscriptions: {
      streaming: [],
      music: [],
      gaming: [],
      news_reading: [],
      cloud_storage: [],
      fitness: [],
      productivity: [],
      food_delivery: [],
      membership_clubs: [],
      other: [],
      collected: false,
    },
    variableSpending: {
      groceries: { monthlyAverage: null, primaryStore: null, secondaryStores: [] },
      diningOut: { monthlyAverage: null, timesPerWeek: null },
      coffee: { monthlyAverage: null, timesPerWeek: null, usualSpend: null },
      clothing: { monthlyAverage: null },
      entertainment: { monthlyAverage: null },
      personalCare: { monthlyAverage: null },
      pets: { monthlyAverage: null, type: null },
      kids: { monthlyAverage: null, childcare: null, activities: null },
      gifts: { monthlyAverage: null },
      miscellaneous: { monthlyAverage: null },
      collected: false,
    },
    savings: {
      emergencyFund: { balance: null, target: null },
      savingsAccount: { balance: null, monthlyContribution: null, apy: null },
      retirement: {
        has401k: null,
        monthlyContribution: null,
        employerMatch: null,
        currentBalance: null,
      },
      ira: { type: null, balance: null, annualContribution: null },
      otherInvestments: [],
      collected: false,
    },
    completionPercentage: 0,
    currentPhase: 1,
    missingCritical: [],
    missingOptional: [],
    readyForAnalysis: false,
    startedAt: now,
    lastUpdatedAt: now,
  };
}

// ==========================================
// CALCULATE COMPLETION
// ==========================================

export function calculateCompletion(state: SpendingIntakeState): number {
  const requiredFields = FIELD_REGISTRY.filter((f) => f.required);
  let collected = 0;

  for (const field of requiredFields) {
    const value = getByPath(state, field.path);
    if (isFieldCollected(value)) collected++;
  }

  return requiredFields.length === 0
    ? 100
    : Math.round((collected / requiredFields.length) * 100);
}

// ==========================================
// GET NEXT QUESTION
// ==========================================

export function getNextQuestion(state: SpendingIntakeState): {
  phase: number;
  field: string;
  question: string;
  followUps: string[];
} | null {
  // Walk through phases in order, find first uncollected required field
  for (let phase = 1; phase <= 5; phase++) {
    const phaseQuestions = INTAKE_QUESTIONS[phase];
    if (!phaseQuestions) continue;

    for (const q of phaseQuestions.questions) {
      if (!q.required) continue;

      // Check if this field's data has been collected
      const value = getByPath(state, q.field);
      if (!isFieldCollected(value)) {
        // For grouped fields like "subscriptions.all_other", check the phase collected flag
        const phaseKey = q.field.split(".")[0] as keyof SpendingIntakeState;
        const phaseObj = state[phaseKey];
        if (
          typeof phaseObj === "object" &&
          phaseObj !== null &&
          "collected" in phaseObj &&
          (phaseObj as { collected: boolean }).collected
        ) {
          continue; // Phase marked as collected, skip
        }

        return {
          phase,
          field: q.field,
          question: q.question,
          followUps: q.followUps,
        };
      }
    }
  }

  return null; // All required data collected
}

// ==========================================
// CHECK IF READY FOR ANALYSIS
// ==========================================

export function isReadyForAnalysis(state: SpendingIntakeState): {
  ready: boolean;
  missingRequired: string[];
  completionPercentage: number;
} {
  const requiredFields = FIELD_REGISTRY.filter((f) => f.required);
  const missingRequired: string[] = [];

  for (const field of requiredFields) {
    const value = getByPath(state, field.path);
    if (!isFieldCollected(value)) {
      missingRequired.push(field.label);
    }
  }

  const completionPercentage = calculateCompletion(state);

  return {
    ready: missingRequired.length === 0,
    missingRequired,
    completionPercentage,
  };
}

// ==========================================
// GET MISSING FIELDS (detailed breakdown)
// ==========================================

export function getMissingFields(state: SpendingIntakeState): {
  critical: { path: string; label: string; phase: number }[];
  optional: { path: string; label: string; phase: number }[];
} {
  const critical: { path: string; label: string; phase: number }[] = [];
  const optional: { path: string; label: string; phase: number }[] = [];

  for (const field of FIELD_REGISTRY) {
    const value = getByPath(state, field.path);
    if (!isFieldCollected(value)) {
      const entry = { path: field.path, label: field.label, phase: field.phase };
      if (field.required) {
        critical.push(entry);
      } else {
        optional.push(entry);
      }
    }
  }

  return { critical, optional };
}

// ==========================================
// DETERMINE CURRENT PHASE
// ==========================================

export function determineCurrentPhase(state: SpendingIntakeState): 1 | 2 | 3 | 4 | 5 {
  if (!state.income.collected) return 1;
  if (!state.fixedExpenses.collected) return 2;
  if (!state.subscriptions.collected) return 3;
  if (!state.variableSpending.collected) return 4;
  return 5;
}

// ==========================================
// UPDATE STATE META FIELDS
// ==========================================

export function refreshStateMeta(state: SpendingIntakeState): SpendingIntakeState {
  const { critical, optional } = getMissingFields(state);
  const completionPercentage = calculateCompletion(state);
  const currentPhase = determineCurrentPhase(state);

  return {
    ...state,
    completionPercentage,
    currentPhase,
    missingCritical: critical.map((c) => c.label),
    missingOptional: optional.map((o) => o.label),
    readyForAnalysis: critical.length === 0,
    lastUpdatedAt: new Date().toISOString(),
  };
}
