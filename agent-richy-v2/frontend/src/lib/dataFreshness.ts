// Every data source has a freshness classification
export type DataFreshness = "live" | "daily" | "weekly" | "monthly" | "quarterly" | "annual" | "static";

export interface DataSource {
  name: string;
  file?: string;                           // Static file path if applicable
  freshness: DataFreshness;
  lastUpdated?: string;
  maxAge: number;                          // Seconds before data is considered stale
  fallbackToStatic: boolean;              // If live fetch fails, use static data?
  searchQuery?: string;                    // Web search query to get fresh data
}

export const DATA_SOURCES: Record<string, DataSource> = {
  // MUST BE LIVE — wrong data costs money
  stockPrices: {
    name: "Stock Prices",
    freshness: "live",
    maxAge: 300,                           // 5 minutes
    fallbackToStatic: false,
    searchQuery: "[TICKER] stock price today"
  },
  analystRatings: {
    name: "Analyst Ratings & Consensus",
    freshness: "daily",
    maxAge: 86400,                         // 24 hours
    fallbackToStatic: false,
    searchQuery: "[TICKER] analyst ratings consensus [current month]"
  },
  interestRates: {
    name: "Current Interest Rates",
    freshness: "daily",
    maxAge: 86400,
    fallbackToStatic: false,
    searchQuery: "current mortgage rates savings account rates fed funds rate"
  },
  couponCodes: {
    name: "Coupon Codes",
    freshness: "daily",
    maxAge: 86400,
    fallbackToStatic: false,
    searchQuery: "[STORE] coupon codes promo codes [current month year]"
  },
  weeklyAds: {
    name: "Store Weekly Ads",
    freshness: "weekly",
    maxAge: 604800,
    fallbackToStatic: false,
    searchQuery: "[STORE] weekly ad deals [LOCATION]"
  },
  etfPricesAndYields: {
    name: "ETF Prices and Yields",
    freshness: "daily",
    maxAge: 86400,
    fallbackToStatic: true,
    file: "src/data/etf-reference.json",
    searchQuery: "[TICKER] ETF current price yield"
  },

  // CAN USE STATIC — changes slowly
  costOfLiving: {
    name: "Cost of Living by City",
    freshness: "annual",
    maxAge: 31536000,
    fallbackToStatic: true,
    file: "src/data/cost-of-living.json"
  },
  stateTaxRates: {
    name: "State Tax Rates",
    freshness: "annual",
    maxAge: 31536000,
    fallbackToStatic: true,
    file: "src/data/state-taxes.json"
  },
  lifeEventCosts: {
    name: "Life Event Reference Costs",
    freshness: "annual",
    maxAge: 31536000,
    fallbackToStatic: true,
    file: "src/data/life-event-costs.json"
  },
  subscriptionPrices: {
    name: "Subscription Service Prices",
    freshness: "quarterly",
    maxAge: 7776000,
    fallbackToStatic: true,
    file: "src/data/subscription-database.json"
  },
  billBenchmarks: {
    name: "Average Bill Costs by Category",
    freshness: "quarterly",
    maxAge: 7776000,
    fallbackToStatic: true,
    file: "src/data/bill-benchmarks.json"
  },
  storeRankings: {
    name: "Store Price Rankings",
    freshness: "quarterly",
    maxAge: 7776000,
    fallbackToStatic: true,
    file: "src/data/store-rankings.json"
  },
  financialLiteracy: {
    name: "Financial Literacy Content",
    freshness: "static",
    maxAge: Infinity,
    fallbackToStatic: true,
    file: "src/data/financial-literacy.json"
  },
  retirementRules: {
    name: "Retirement Contribution Limits & Rules",
    freshness: "annual",
    maxAge: 31536000,
    fallbackToStatic: true,
    file: "src/data/etf-reference.json"  // retirementRules section
  }
};

// System prompt instruction for data freshness
export const DATA_FRESHNESS_PROMPT = `
## Data Freshness Rules — ALWAYS FOLLOW THESE:

ALWAYS USE WEB SEARCH FOR:
- Stock prices (never quote a price without searching first)
- Analyst ratings and consensus (search for latest)
- Current interest rates (mortgage, savings, fed funds)
- Coupon codes (must be current)
- Store weekly ads and sales
- ETF prices and yields (search first, use etf-reference.json as fallback ONLY)
- Any data where being wrong could cost the user money

SAFE TO USE STATIC KNOWLEDGE BASE FOR:
- Cost of living comparisons by city (cost-of-living.json)
- State tax rates and brackets (state-taxes.json) 
- Life event cost estimates (life-event-costs.json)
- Subscription service pricing (subscription-database.json — but note prices may have changed)
- Bill benchmarks (bill-benchmarks.json)
- Store rankings by category (store-rankings.json)
- Financial literacy explanations (financial-literacy.json)
- ETF expense ratios and structure (etf-reference.json — these rarely change)
- Retirement contribution limits (etf-reference.json retirementRules section)
- Model portfolio allocations (etf-reference.json modelPortfolios section)

WHEN USING STATIC DATA:
- Always note the data date: "Based on 2026 data from [source]"
- If the user asks for something very current, search anyway
- If static data contradicts search results, trust the search results

WHEN GENERATING ALLOCATION PLANS:
1. Use etf-reference.json for ETF selection, expense ratios, and portfolio models
2. SEARCH for current prices and yields before displaying them
3. SEARCH for current interest rates before any bond/savings calculations
4. SEARCH for current retirement contribution limits (they change annually)
5. If search fails, use the static data but mark it: "Approximate as of [date]"

WHEN RUNNING FINANCIAL TWIN SIMULATIONS:
1. Use cost-of-living.json for city comparisons
2. Use state-taxes.json for tax calculations
3. Use life-event-costs.json for event cost estimates
4. SEARCH for current mortgage rates if home purchase is involved
5. SEARCH for current salary data if career change is involved
`;
