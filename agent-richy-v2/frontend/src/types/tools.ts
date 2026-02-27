// ==========================================
// FINANCIAL GOAL SIMULATOR
// ==========================================

export type GoalType = 
  | "emergency_fund" | "debt_payoff" | "vacation" | "down_payment"
  | "car_purchase" | "wedding" | "retirement" | "education"
  | "investment" | "major_purchase" | "custom";

export type RiskTolerance = "conservative" | "moderate" | "aggressive";

export interface FinancialGoal {
  id: string;
  name: string;
  type: GoalType;
  targetAmount: number;
  currentSaved: number;
  deadline?: string;                    // ISO date — optional, Richy can calculate
  monthlySavingsCapacity: number;       // How much user can save per month toward this
  currentInterestRate?: number;         // If investing/savings account APY
  additionalContributions?: {           // Windfalls, bonuses, tax refunds
    amount: number;
    frequency: "one_time" | "monthly" | "quarterly" | "annual";
    description: string;
  }[];
}

export interface GoalSimulationResult {
  goalId: string;
  goalName: string;
  goalType: GoalType;
  targetAmount: number;
  currentSaved: number;
  monthlyContribution: number;
  
  // Core projections
  monthsToGoal: number;
  projectedCompletionDate: string;
  totalContributed: number;
  totalInterestEarned: number;
  
  // Scenarios
  scenarios: {
    name: string;                       // "Current pace", "With optimizer savings", "Aggressive"
    monthlyAmount: number;
    monthsToGoal: number;
    completionDate: string;
    totalInterestEarned: number;
    description: string;
  }[];
  
  // Milestones
  milestones: {
    percentage: number;                 // 25%, 50%, 75%, 100%
    amount: number;
    projectedDate: string;
    monthsFromNow: number;
  }[];
  
  // Micro-actions
  dailyEquivalent: number;             // "That's $X per day"
  weeklyEquivalent: number;
  perPaycheckAmount?: number;          // If user provided pay frequency
  
  // Boost suggestions
  boostSuggestions: {
    action: string;
    monthlySavingsIncrease: number;
    newMonthsToGoal: number;
    timeSaved: number;                  // Months saved
  }[];
  
  // Monte Carlo (for investment goals)
  monteCarlo?: {
    simulations: number;
    percentile10: number;               // 10th percentile outcome
    percentile25: number;
    percentile50: number;               // Median
    percentile75: number;
    percentile90: number;
    probabilityOfSuccess: number;       // % chance of hitting goal by deadline
  };
}

// ==========================================
// RECURRING BILL PREDICTOR
// ==========================================

export interface TrackedBill {
  id: string;
  name: string;
  category: string;
  amount: number;
  frequency: "weekly" | "biweekly" | "monthly" | "quarterly" | "semi_annual" | "annual";
  nextDueDate: string;
  autopay: boolean;
  provider?: string;
  accountNumber?: string;               // Last 4 digits only
  historicalAmounts?: {                  // Track price changes
    date: string;
    amount: number;
  }[];
  alerts?: {
    priceIncrease: boolean;             // Alert if amount increases
    dueDateReminder: number;            // Days before to remind
  };
}

export interface BillPrediction {
  period: string;                       // "March 2026", "Q2 2026"
  startDate: string;
  endDate: string;
  
  bills: {
    bill: TrackedBill;
    dueDate: string;
    amount: number;
    isEstimate: boolean;                // True if amount varies
    varianceNote?: string;              // "Your electric bill averages $137 but ranges $95-180"
  }[];
  
  totalPredicted: number;
  comparedToLastMonth: number;          // Difference from previous period
  comparedToLastMonthPercent: number;
  
  unusualItems: {
    billName: string;
    reason: string;                     // "Annual renewal", "Price increased", "New bill"
    amount: number;
  }[];
  
  calendarView: {
    date: string;
    bills: { name: string; amount: number }[];
    dailyTotal: number;
  }[];
  
  cashFlowWarnings: {
    date: string;
    warning: string;                    // "3 bills totaling $847 hit on the 15th"
    totalDue: number;
  }[];
}

// ==========================================
// LOCAL DEAL RADAR
// ==========================================

export interface LocalDeal {
  id: string;
  store: string;
  storeName: string;
  storeAddress?: string;
  distanceMiles?: number;
  
  dealType: "sale" | "clearance" | "bogo" | "coupon" | "loyalty" | "seasonal";
  productName: string;
  productCategory: string;
  
  originalPrice: number;
  salePrice: number;
  savings: number;
  savingsPercent: number;
  
  validFrom: string;
  validUntil: string;
  
  source: string;                       // "Store weekly ad", "Flipp", "store app"
  sourceUrl?: string;
  
  requiresLoyaltyCard: boolean;
  requiresMembership: boolean;
  limitPerCustomer?: number;
  
  // Contextual
  userBuysThis: boolean;               // Does this match user's shopping profile?
  usualPrice: number;                   // What user normally pays
  isHistoricLow: boolean;              // Is this the lowest price we've seen?
}

export interface LocalDealReport {
  zipCode: string;
  generatedAt: string;
  radius: number;                       // Miles searched
  
  topDeals: LocalDeal[];                // Best deals overall
  matchedDeals: LocalDeal[];            // Deals matching user's shopping profile
  
  weeklyAdHighlights: {
    store: string;
    storeName: string;
    topDeals: { item: string; salePrice: number; savings: string }[];
    adValidDates: string;
  }[];
  
  totalPotentialSavings: number;        // If user bought all matched deals at sale price vs usual price
}

// ==========================================
// RECEIPT ANALYZER
// ==========================================

export interface ReceiptItem {
  name: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  category: string;
  taxable: boolean;
}

export interface AnalyzedReceipt {
  id: string;
  store: string;
  storeAddress?: string;
  date: string;
  
  items: ReceiptItem[];
  subtotal: number;
  tax: number;
  total: number;
  paymentMethod?: string;
  
  // Analysis
  categoryBreakdown: {
    category: string;
    amount: number;
    percentage: number;
    itemCount: number;
  }[];
  
  priceAlerts: {
    item: string;
    paidPrice: number;
    betterPrice: number;
    betterStore: string;
    savings: number;
  }[];
  
  // Over time
  comparedToAverage?: {
    thisTrip: number;
    averageTrip: number;
    difference: number;
    trend: "increasing" | "stable" | "decreasing";
  };
}

export interface ReceiptHistory {
  userId: string;
  totalReceipts: number;
  totalSpent: number;
  averageTrip: number;
  
  storeBreakdown: {
    store: string;
    visits: number;
    totalSpent: number;
    averageSpent: number;
  }[];
  
  categoryTrends: {
    category: string;
    monthlyAverage: number;
    trend: "increasing" | "stable" | "decreasing";
    percentOfTotal: number;
  }[];
  
  topItems: {
    name: string;
    frequency: number;                  // Times purchased
    averagePrice: number;
    totalSpent: number;
    bestPriceFound: number;
    bestPriceStore: string;
  }[];
}
