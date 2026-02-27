/* ── Price Intelligence — Crowdsourced Pricing Moat ──────────────────── */

// ==========================================
// PRICE DATA POINT
// ==========================================

export interface PriceDataPoint {
  id: string;
  productName: string;
  normalizedName: string; // "tide pods 42ct" regardless of how user typed it
  category: string;
  brand: string;

  store: string;
  storeLocation?: string; // ZIP or city

  price: number;
  unitPrice?: number;
  unit?: string;

  reportedBy: string; // Anonymized user ID
  reportedAt: string;

  context: "receipt" | "manual" | "shopping_trip" | "price_check";

  // Validation
  outlier: boolean; // Flagged if wildly different from other reports
  confirmedBy: number; // How many other users reported similar price
}

// ==========================================
// PRODUCT PRICE PROFILE
// ==========================================

export interface ProductPriceProfile {
  productName: string;
  normalizedName: string;
  category: string;

  // Aggregated from all user reports
  dataPoints: number; // Total reports
  uniqueReporters: number;

  // Price analysis
  averagePrice: number;
  medianPrice: number;
  lowestReported: { price: number; store: string; date: string };
  highestReported: { price: number; store: string; date: string };

  // By store
  storeComparison: {
    store: string;
    avgPrice: number;
    dataPoints: number;
    lastReported: string;
    trend: "increasing" | "stable" | "decreasing";
  }[];

  // Price trends
  priceHistory: { month: string; avgPrice: number }[];
  trend: "increasing" | "stable" | "decreasing";
  inflationRate: number; // This product's specific inflation rate

  // Smart insights
  bestTimeToBuy: string; // "Prices drop 15% in November typically"
  bestStore: string;
  worstStore: string;

  lastUpdated: string;
}

// ==========================================
// NETWORK EFFECT METRICS
// ==========================================

export interface PlatformIntelligence {
  // These metrics grow with every user and make the platform more valuable

  totalPriceDataPoints: number;
  totalUniqueProducts: number;
  totalUniqueStores: number;
  totalActiveUsers: number;

  // Coverage
  citiesCovered: number;
  categoriesCovered: number;
  avgDataPointsPerProduct: number;

  // Freshness
  avgDataAge: number; // Hours since last report
  productsUpdatedToday: number;

  // Accuracy
  priceAccuracyScore: number; // How often our crowdsourced data matches actual store prices

  // Value created
  totalUserSavings: number; // Aggregate savings across all users
  avgSavingsPerUser: number;
  topSavingsCategories: { category: string; totalSaved: number }[];

  // Growth
  dataPointsThisWeek: number;
  newUsersThisWeek: number;
  weekOverWeekGrowth: number;
}

// ==========================================
// ANONYMIZED INSIGHTS (sellable data product)
// ==========================================

export interface MarketInsight {
  // Anonymized, aggregated data that is valuable to retailers, CPG companies,
  // and market researchers. This is a potential B2B revenue stream.

  category: string;
  timeframe: string;

  // Consumer behavior
  avgMonthlySpend: number;
  spendTrend: "increasing" | "stable" | "decreasing";
  topBrands: { brand: string; marketShare: number }[];
  priceElasticity: number; // How much does demand change with price

  // Store competition
  storePreferences: { store: string; percentage: number }[];
  switchingBehavior: number; // % of users who changed primary store

  // Demographics (anonymized)
  byAgeGroup: { group: string; avgSpend: number; topBrand: string }[];
  byHouseholdSize: { size: number; avgSpend: number }[];
  byRegion: {
    region: string;
    avgSpend: number;
    preferredStore: string;
  }[];
}

// ==========================================
// PRICE NORMALIZATION
// ==========================================

/** Normalizes user-typed product names into a canonical form for matching. */
export function normalizeProductName(raw: string): string {
  return raw
    .toLowerCase()
    .replace(/['']/g, "'")
    .replace(/[^a-z0-9.' ]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/** Detect if a price seems like an outlier given existing data. */
export function isOutlier(
  price: number,
  existing: { averagePrice: number; dataPoints: number },
): boolean {
  if (existing.dataPoints < 3) return false; // Not enough data to judge
  const deviation = Math.abs(price - existing.averagePrice) / existing.averagePrice;
  return deviation > 0.5; // More than 50% off average
}

/** Calculate median from a list of prices. */
export function medianPrice(prices: number[]): number {
  if (prices.length === 0) return 0;
  const sorted = [...prices].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0
    ? sorted[mid]
    : (sorted[mid - 1] + sorted[mid]) / 2;
}

/** Compute simple trend direction from a series of monthly averages. */
export function computeTrend(
  history: { month: string; avgPrice: number }[],
): "increasing" | "stable" | "decreasing" {
  if (history.length < 3) return "stable";
  const recent = history.slice(-3);
  const first = recent[0].avgPrice;
  const last = recent[recent.length - 1].avgPrice;
  const change = (last - first) / first;
  if (change > 0.05) return "increasing";
  if (change < -0.05) return "decreasing";
  return "stable";
}

/** Product-specific inflation rate (annualized % change). */
export function productInflation(
  history: { month: string; avgPrice: number }[],
): number {
  if (history.length < 2) return 0;
  const oldest = history[0];
  const newest = history[history.length - 1];
  const monthsSpan =
    (new Date(newest.month).getTime() - new Date(oldest.month).getTime()) /
    (1000 * 60 * 60 * 24 * 30.44);
  if (monthsSpan === 0) return 0;
  const totalChange = (newest.avgPrice - oldest.avgPrice) / oldest.avgPrice;
  return (totalChange / monthsSpan) * 12 * 100; // Annualized %
}

// ==========================================
// PLATFORM METRICS
// ==========================================

/** Create an empty PlatformIntelligence snapshot. */
export function createEmptyPlatformIntelligence(): PlatformIntelligence {
  return {
    totalPriceDataPoints: 0,
    totalUniqueProducts: 0,
    totalUniqueStores: 0,
    totalActiveUsers: 0,
    citiesCovered: 0,
    categoriesCovered: 0,
    avgDataPointsPerProduct: 0,
    avgDataAge: 0,
    productsUpdatedToday: 0,
    priceAccuracyScore: 0,
    totalUserSavings: 0,
    avgSavingsPerUser: 0,
    topSavingsCategories: [],
    dataPointsThisWeek: 0,
    newUsersThisWeek: 0,
    weekOverWeekGrowth: 0,
  };
}
