/* ── Financial DNA — The User Intelligence Model ────────────────────── */

// ==========================================
// FINANCIAL DNA — The User Intelligence Model
// ==========================================

export interface FinancialDNA {
  userId: string;
  createdAt: string;
  lastUpdated: string;
  interactionCount: number;

  // ==========================================
  // IDENTITY PROFILE
  // ==========================================
  identity: {
    age?: number;
    householdSize?: number;
    location?: { zipCode: string; city: string; state: string; costOfLivingIndex: number };
    employmentType?: "full_time" | "part_time" | "freelance" | "self_employed" | "unemployed" | "retired" | "student";
    industry?: string;
    lifeStage?: "student" | "early_career" | "mid_career" | "peak_earning" | "pre_retirement" | "retired";
    financialLiteracyLevel?: "beginner" | "intermediate" | "advanced";
  };

  // ==========================================
  // INCOME & CASH FLOW MAP
  // ==========================================
  cashFlow: {
    monthlyIncome: number;
    incomeStability: "very_stable" | "stable" | "variable" | "unpredictable";
    incomeSources: { source: string; amount: number; frequency: string; reliable: boolean }[];
    monthlyExpenses: number;
    monthlySurplus: number;
    surplusTrend: "growing" | "stable" | "shrinking";
    cashFlowScore: number; // 1-100
  };

  // ==========================================
  // SPENDING FINGERPRINT
  // ==========================================
  spendingFingerprint: {
    // What makes this user's spending unique
    topCategories: {
      category: string;
      monthlyAmount: number;
      percentOfIncome: number;
      trend: "increasing" | "stable" | "decreasing";
    }[];

    // Behavioral patterns
    impulseSpendingScore: number; // 1-100 (100 = very impulsive)
    planningScore: number; // 1-100 (100 = very planned)
    priceConsciousness: number; // 1-100 (100 = very price conscious)
    brandLoyalty: number; // 1-100 (100 = very brand loyal)

    // Known weaknesses
    spendingWeaknesses: {
      category: string;
      description: string; // "Tends to overspend on food delivery when stressed"
      estimatedMonthlyCost: number;
      suggestedIntervention: string;
    }[];

    // Known strengths
    spendingStrengths: {
      category: string;
      description: string; // "Consistently meal preps, keeping grocery costs below average"
    }[];

    // Subscription profile
    activeSubscriptions: {
      name: string;
      amount: number;
      valueScore: number;
      lastMentioned: string;
    }[];
    totalSubscriptionCost: number;

    // Shopping behavior
    primaryStores: { store: string; frequency: string; avgSpend: number }[];
    prefersBrands: boolean;
    opensToSubstitutions: boolean;
    usesCoupons: boolean;
    hasMemberships: string[]; // "Costco", "Amazon Prime", etc.
  };

  // ==========================================
  // DEBT PROFILE
  // ==========================================
  debtProfile: {
    totalDebt: number;
    debtToIncomeRatio: number;
    debts: {
      type: string;
      name: string;
      balance: number;
      interestRate: number;
      minimumPayment: number;
      actualPayment: number;
      payoffDate: string;
    }[];
    debtStrategy: "avalanche" | "snowball" | "minimum_only" | "none";
    debtScore: number; // 1-100
    monthlyDebtPayments: number;
  };

  // ==========================================
  // SAVINGS & INVESTMENT PROFILE
  // ==========================================
  wealthProfile: {
    emergencyFund: {
      balance: number;
      monthsCovered: number;
      adequate: boolean;
    };
    totalSavings: number;
    totalInvestments: number;
    netWorth: number; // Assets - debts

    savingsRate: number; // % of income
    investmentStyle?: "passive_index" | "active_stock_picking" | "mixed" | "not_investing";
    riskTolerance?: "conservative" | "moderate" | "aggressive";

    retirementAccounts: {
      type: string;
      balance: number;
      monthlyContribution: number;
      employerMatch: number;
    }[];
    retirementReadiness: number; // 1-100 (are they on track?)

    investmentInterests: string[]; // Sectors, themes they've asked about
    followedStocks: string[]; // Tickers they've asked about

    wealthScore: number; // 1-100
  };

  // ==========================================
  // GOALS & ASPIRATIONS
  // ==========================================
  goals: {
    active: {
      id: string;
      name: string;
      type: string;
      targetAmount: number;
      currentProgress: number;
      monthlyContribution: number;
      projectedCompletionDate: string;
      onTrack: boolean;
    }[];
    completed: { name: string; completedDate: string; amount: number }[];
    mentioned: string[]; // Things they've mentioned wanting but haven't formalized
  };

  // ==========================================
  // BEHAVIORAL INTELLIGENCE
  // ==========================================
  behavior: {
    // Engagement patterns
    avgMessagesPerSession: number;
    preferredTopics: string[];
    avoidedTopics: string[];
    responseStyle: "detailed" | "brief" | "mixed";

    // Financial behavior patterns
    actsOnRecommendations: boolean; // Do they actually follow through?
    followThroughRate: number; // % of suggested actions they report completing

    // Emotional patterns around money
    moneyAnxietyLevel: "low" | "moderate" | "high";
    motivatedBy: "fear" | "growth" | "security" | "freedom" | "family";

    // Learning progression
    topicsLearned: string[]; // Concepts they've asked about and understood
    topicsToRevisit: string[]; // Concepts they struggled with
  };

  // ==========================================
  // RICHY'S PREDICTIONS
  // ==========================================
  predictions: {
    // What Richy thinks will happen
    nextLikelyQuestion: string;
    upcomingFinancialEvents: {
      event: string;
      date: string;
      action: string;
    }[];
    riskAlerts: {
      risk: string;
      severity: "low" | "medium" | "high";
      recommendation: string;
    }[];
    opportunities: {
      opportunity: string;
      potentialValue: number;
      timeframe: string;
    }[];
  };

  // ==========================================
  // COMPOSITE SCORES
  // ==========================================
  scores: {
    overallFinancialHealth: number; // 1-100
    spendingEfficiency: number; // 1-100
    debtManagement: number; // 1-100
    savingsAndInvesting: number; // 1-100
    financialKnowledge: number; // 1-100
    trajectory: "improving" | "stable" | "declining";
    percentileAmongUsers: number; // Where they rank (anonymized)
  };
}

// ==========================================
// DNA UPDATE ENGINE
// ==========================================

// After every conversation, extract new information and update the DNA
export interface DNAUpdateEvent {
  timestamp: string;
  source:
    | "conversation"
    | "spending_analysis"
    | "goal_update"
    | "market_activity";
  fieldsUpdated: string[];
  previousValues: Record<string, unknown>;
  newValues: Record<string, unknown>;
  confidence: number; // How confident is Richy in this data
}

// Instructions for the AI to update DNA after each conversation
export const DNA_UPDATE_INSTRUCTIONS = `
After EVERY conversation, extract any new financial information the user revealed.
Update the Financial DNA silently. Examples:

- User mentions they got a raise → update cashFlow.monthlyIncome
- User says "I cancelled Netflix" → remove from spendingFingerprint.activeSubscriptions
- User asks about index funds for the first time → update behavior.topicsLearned
- User says "I'm stressed about my credit card" → update behavior.moneyAnxietyLevel
- User shares a grocery receipt → update spendingFingerprint.primaryStores

The DNA should grow organically through natural conversation.
NEVER ask the user to "update their profile." Just listen and learn.
`;

// ==========================================
// FACTORY — Create empty DNA for new users
// ==========================================

export function createEmptyDNA(userId: string): FinancialDNA {
  const now = new Date().toISOString();
  return {
    userId,
    createdAt: now,
    lastUpdated: now,
    interactionCount: 0,
    identity: {},
    cashFlow: {
      monthlyIncome: 0,
      incomeStability: "stable",
      incomeSources: [],
      monthlyExpenses: 0,
      monthlySurplus: 0,
      surplusTrend: "stable",
      cashFlowScore: 0,
    },
    spendingFingerprint: {
      topCategories: [],
      impulseSpendingScore: 50,
      planningScore: 50,
      priceConsciousness: 50,
      brandLoyalty: 50,
      spendingWeaknesses: [],
      spendingStrengths: [],
      activeSubscriptions: [],
      totalSubscriptionCost: 0,
      primaryStores: [],
      prefersBrands: false,
      opensToSubstitutions: true,
      usesCoupons: false,
      hasMemberships: [],
    },
    debtProfile: {
      totalDebt: 0,
      debtToIncomeRatio: 0,
      debts: [],
      debtStrategy: "none",
      debtScore: 50,
      monthlyDebtPayments: 0,
    },
    wealthProfile: {
      emergencyFund: { balance: 0, monthsCovered: 0, adequate: false },
      totalSavings: 0,
      totalInvestments: 0,
      netWorth: 0,
      savingsRate: 0,
      retirementAccounts: [],
      retirementReadiness: 0,
      investmentInterests: [],
      followedStocks: [],
      wealthScore: 0,
    },
    goals: {
      active: [],
      completed: [],
      mentioned: [],
    },
    behavior: {
      avgMessagesPerSession: 0,
      preferredTopics: [],
      avoidedTopics: [],
      responseStyle: "mixed",
      actsOnRecommendations: false,
      followThroughRate: 0,
      moneyAnxietyLevel: "moderate",
      motivatedBy: "security",
      topicsLearned: [],
      topicsToRevisit: [],
    },
    predictions: {
      nextLikelyQuestion: "",
      upcomingFinancialEvents: [],
      riskAlerts: [],
      opportunities: [],
    },
    scores: {
      overallFinancialHealth: 0,
      spendingEfficiency: 0,
      debtManagement: 0,
      savingsAndInvesting: 0,
      financialKnowledge: 0,
      trajectory: "stable",
      percentileAmongUsers: 50,
    },
  };
}
