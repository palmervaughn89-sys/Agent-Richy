export type SourceTier = "tier1_bank" | "tier2_rating" | "tier3_specialized" | "tier4_press";

export type Sentiment = "bullish" | "moderately_bullish" | "neutral" | "moderately_bearish" | "bearish";

export type Sector =
  | "technology" | "healthcare" | "financials" | "energy"
  | "consumer_discretionary" | "consumer_staples" | "industrials"
  | "materials" | "real_estate" | "utilities" | "communication_services";

export interface AnalystInsight {
  id: string;
  source: string;              // "Goldman Sachs", "Morningstar", etc.
  sourceTier: SourceTier;
  date: string;                // ISO date of the research publication
  sector?: Sector;
  ticker?: string;             // Specific stock if applicable
  sentiment: Sentiment;
  headline: string;            // "Goldman upgrades Healthcare to Overweight"
  summary: string;             // 2-3 sentence plain English summary
  keyPoints: string[];         // Bullet points of the core thesis
  priceTarget?: number;        // If applicable
  currentPrice?: number;       // For context
  sourceUrl?: string;          // Link to original research or article covering it
  confidence: "high" | "medium" | "low";  // Based on source tier and recency
}

export interface SectorOutlook {
  sector: Sector;
  sectorName: string;          // Display name
  consensusSentiment: Sentiment;
  insights: AnalystInsight[];  // All research for this sector
  bullCount: number;
  bearCount: number;
  neutralCount: number;
  topBullCase: string;         // Best bull argument across sources
  topBearCase: string;         // Best bear argument across sources
  keyMetrics: {
    peRatio?: number;          // Sector average P/E
    ytdReturn?: number;        // Year-to-date performance
    morningstarValuation?: "undervalued" | "fairly_valued" | "overvalued";
  };
}

export interface MarketIntelligenceReport {
  generatedAt: string;
  marketSentiment: Sentiment;  // Overall market mood across sources
  topSectors: SectorOutlook[]; // Ranked by consensus bullishness
  bottomSectors: SectorOutlook[];
  keyThemes: string[];         // Cross-cutting themes: "AI spending", "rate cuts", etc.
  contrarian: string;          // One surprising or contrarian view from a reputable source
  disclaimer: string;          // Always present
}

export interface PartnerRating {
  partnerId: string;
  partnerName: string;         // "Morningstar", "Fidelity", etc.
  ticker: string;
  rating: string;              // "5 stars", "Buy", "Overweight", etc.
  ratingScale: string;         // "1-5 stars", "Buy/Hold/Sell", etc.
  fairValue?: number;
  lastUpdated: string;
  sourceUrl?: string;
}
