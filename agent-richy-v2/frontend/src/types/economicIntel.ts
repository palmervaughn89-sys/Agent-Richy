// ==========================================
// ECONOMIC INTELLIGENCE — Macro meets personal
// ==========================================

// Categories that map to personal spending
export type SpendingCategory =
  | "food_at_home" | "food_away" | "energy" | "gasoline"
  | "housing" | "apparel" | "transportation" | "medical"
  | "education" | "electronics" | "recreation" | "furniture"
  | "personal_care" | "alcohol" | "tobacco" | "overall";

export interface CategoryInflation {
  category: SpendingCategory;
  displayName: string;
  currentRate: number;                     // Year-over-year % change
  lastMonth: number;                       // Previous month's rate
  trend: "accelerating" | "stable" | "decelerating";
  threeMonthAvg: number;
  sixMonthAvg: number;

  // Personal impact
  avgMonthlySpend: number;                 // Average American monthly spend in this category
  monthlyImpactDollars: number;            // How much more/less per month vs last year
  annualImpactDollars: number;

  // Prediction
  forecast: "rising" | "stable" | "falling";
  forecastConfidence: "high" | "medium" | "low";
  forecastReason: string;                  // "Egg supply recovering from avian flu"

  // User action
  userAction: string;                      // "Stock up now" or "Wait — prices dropping" or "No change needed"
  actionUrgency: "now" | "soon" | "watch" | "none";
}

export interface EconomicSnapshot {
  generatedAt: string;
  dataDate: string;                        // When this data was last fetched

  // Big picture
  overallInflation: number;                // CPI year-over-year
  coreInflation: number;                   // Excluding food and energy
  fedFundsRate: number;
  unemployment: number;
  consumerConfidence: number;              // Conference Board index
  consumerSpendingGrowth: number;          // Month-over-month % change
  gdpGrowth: number;                       // Latest quarterly

  // Category breakdown
  categoryInflation: CategoryInflation[];

  // Key rates that affect users directly
  rates: {
    mortgage30yr: number;
    mortgage15yr: number;
    autoLoanNew: number;
    autoLoanUsed: number;
    creditCardAvg: number;
    personalLoan: number;
    savingsAccountAvg: number;
    savingsAccountBest: number;            // Best widely available HYSA rate
    cdRate1yr: number;
    cdRate5yr: number;
    primeRate: number;
    tenYearTreasury: number;
  };

  // Gas prices (huge impact on daily life)
  gasPrices: {
    nationalAvg: number;
    weekAgo: number;
    monthAgo: number;
    yearAgo: number;
    trend: "rising" | "stable" | "falling";
    forecast: string;                      // "Expected to fall 5-10 cents in next 2 weeks"
    cheapestDay: string;                   // "Monday and Tuesday tend to be cheapest"
  };

  // Housing market
  housing: {
    medianHomePrice: number;
    yearOverYearChange: number;
    inventoryMonths: number;               // Months of supply (below 4 = seller's market)
    marketType: "sellers" | "balanced" | "buyers";
    mortgagePayment: number;               // Monthly on median home with 20% down
    rentVsBuyAdvantage: string;            // "Renting is cheaper in most metros right now"
    forecast: string;
  };

  // Employment
  employment: {
    unemploymentRate: number;
    jobsAddedLastMonth: number;
    wageGrowthYoY: number;
    quitRate: number;                      // Higher = workers feel confident
    sectorStrength: { sector: string; outlook: "growing" | "stable" | "contracting" }[];
  };
}

// ==========================================
// PREDICTIVE DEAL INTELLIGENCE
// ==========================================

export interface DealPrediction {
  id: string;
  category: string;
  prediction: string;                      // "Electronics prices likely to drop 10-15% in next 3-4 weeks"

  confidence: "high" | "medium" | "low";
  timeframe: string;                       // "Next 2-4 weeks"

  // The reasoning chain (transparent to user)
  reasoning: {
    dataPoint: string;
    source: string;
    implication: string;
  }[];
  // Example:
  // { dataPoint: "Consumer electronics spending down 8% YoY", source: "BLS CPI Report", implication: "Retailers sitting on excess inventory" }
  // { dataPoint: "Best Buy reported 12% decline in same-store sales", source: "Earnings report", implication: "Pressure to discount to move product" }
  // { dataPoint: "Black Friday/Holiday inventory still clearing", source: "Retail industry reports", implication: "Extended clearance sales likely" }

  // What the user should do
  action: "wait" | "buy_now" | "stock_up" | "watch" | "lock_in";
  actionDescription: string;
  potentialSavings: string;                // "Save 10-15% by waiting 3 weeks"

  // Risk of waiting
  riskOfAction: string;                    // "Small risk of sell-out on popular models"

  // Affected products
  affectedProducts: string[];              // "TVs", "Laptops", "Headphones"

  generatedAt: string;
  expiresAt: string;                       // Prediction is no longer relevant after this date
}

export interface PurchaseTimingAdvice {
  item: string;                            // What the user wants to buy
  currentPrice: number;

  timing: "buy_now" | "wait" | "urgent";
  reason: string;

  // Price prediction
  priceForecast: {
    weeks2: { price: number; confidence: number };
    weeks4: { price: number; confidence: number };
    months3: { price: number; confidence: number };
  };

  // Seasonal patterns
  bestMonthToBuy: string;                  // "TVs are cheapest in January (Super Bowl sales) and November (Black Friday)"
  worstMonthToBuy: string;                 // "Worst time: September-October (new models launch, old stock holds value)"

  // Current market conditions
  demandLevel: "high" | "normal" | "low";
  supplyLevel: "tight" | "normal" | "excess";

  // Comparable alternatives
  alternatives: {
    name: string;
    price: number;
    savings: number;
    tradeoff: string;
  }[];
}

// ==========================================
// SEASONAL PATTERNS DATABASE
// ==========================================

export interface SeasonalPattern {
  category: string;
  monthlyPattern: {
    month: number;                         // 1-12
    monthName: string;
    typicalPricing: "peak" | "above_avg" | "average" | "below_avg" | "lowest";
    reason: string;
    buyRating: 1 | 2 | 3 | 4 | 5;        // 5 = best time to buy
  }[];
  bestTimeToBuy: string;
  worstTimeToBuy: string;
  annualPriceVariation: number;            // % difference between peak and lowest
}

// ==========================================
// PERSONAL ECONOMIC IMPACT
// ==========================================

export interface PersonalEconomicImpact {
  userId: string;
  generatedAt: string;

  // How the current economy affects THIS user specifically
  monthlyInflationCost: number;            // Extra $ this user pays vs last year due to inflation
  annualInflationCost: number;

  // Category-by-category impact based on their actual spending
  categoryImpacts: {
    category: string;
    userMonthlySpend: number;
    inflationRate: number;
    monthlyExtraCost: number;              // How much more they're paying vs last year
    annualExtraCost: number;
    trend: "getting_worse" | "stable" | "improving";
    richyAction: string;                   // What Richy suggests to offset this
  }[];

  // Rate impacts
  rateImpacts: {
    // If they have a mortgage
    mortgageImpact?: {
      currentRate: number;
      currentMarketRate: number;
      refinanceSavings: number;            // Monthly savings if they refinance
      shouldRefinance: boolean;
      reason: string;
    };
    // If they have credit card debt
    creditCardImpact?: {
      currentRate: number;
      avgMarketRate: number;
      balanceTransferSavings: number;
      shouldTransfer: boolean;
    };
    // Savings account
    savingsImpact?: {
      currentAPY: number;
      bestAvailableAPY: number;
      balanceInSavings: number;
      annualEarningsDifference: number;    // Switching to best HYSA
    };
  };

  // Active deal predictions relevant to this user's shopping patterns
  relevantPredictions: DealPrediction[];

  // The headline
  headline: string;
  // "Inflation is costing you $127/month extra. But electronics prices are dropping —
  //  wait 3 weeks on that laptop and save $150-200."

  // Net position
  netMonthlyImpact: number;               // Total: inflation cost - savings from timing
}
