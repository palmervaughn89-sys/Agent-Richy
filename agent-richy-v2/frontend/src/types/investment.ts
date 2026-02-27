export type AnalystRating = "strong_buy" | "buy" | "overweight" | "hold" | "underweight" | "sell" | "strong_sell";

export type RatingSource =
  | "goldman_sachs" | "jp_morgan" | "morgan_stanley" | "bank_of_america"
  | "morningstar" | "fidelity" | "schwab" | "ark_invest"
  | "citi" | "barclays" | "ubs" | "deutsche_bank"
  | "wells_fargo" | "raymond_james" | "jefferies";

export interface FirmRating {
  source: RatingSource;
  sourceName: string;            // Display name: "Goldman Sachs"
  rating: AnalystRating;
  ratingDisplay: string;         // "Overweight", "Buy", "4 Stars"
  priceTarget?: number;
  currentPrice?: number;
  upside?: number;               // Percentage upside to price target
  dateIssued: string;
  analystName?: string;
  reportTitle?: string;
  sourceUrl?: string;
  confidence: "high" | "medium" | "low";  // Based on recency and source tier
}

export interface ConsensusRating {
  ticker: string;
  companyName: string;
  sector: string;
  currentPrice: number;

  // Consensus calculations
  consensusScore: number;        // 1-100 scale (100 = strongest buy consensus)
  consensusLabel: "Strong Buy" | "Buy" | "Moderate Buy" | "Hold" | "Moderate Sell" | "Sell" | "Strong Sell";

  // Individual firm ratings
  ratings: FirmRating[];
  totalRatings: number;
  buyCount: number;              // Firms with buy/strong_buy/overweight
  holdCount: number;
  sellCount: number;             // Firms with sell/strong_sell/underweight

  // Price target consensus
  avgPriceTarget: number;
  highPriceTarget: number;
  lowPriceTarget: number;
  medianPriceTarget: number;
  impliedUpside: number;         // % from current price to avg target

  // Additional context
  morningstarStars?: number;     // 1-5
  morningstarFairValue?: number;
  morningstarMoat?: "wide" | "narrow" | "none";

  // Key metrics
  peRatio?: number;
  forwardPE?: number;
  dividendYield?: number;
  marketCap?: string;
  beta?: number;
  revenueGrowthYoY?: number;

  // Bull/Bear summary
  bullCase: string;
  bearCase: string;

  lastUpdated: string;
  disclaimer: string;
}

export interface ConsensusLeaderboard {
  generatedAt: string;
  category: string;              // "Overall", "Technology", "Healthcare", etc.
  categoryDescription: string;
  timeframe: string;             // "February 2026 Analyst Consensus"

  topRated: ConsensusRating[];   // Top 10 by consensus score

  sectorBreakdown: {
    sector: string;
    stockCount: number;
    avgConsensusScore: number;
    topPick: string;             // Ticker of highest-rated in sector
  }[];

  methodology: string;           // How scores are calculated — full transparency
  sources: string[];             // All firms included

  disclaimer: string;
}

export interface SectorConsensus {
  sector: string;
  sectorName: string;

  // Aggregate sector ratings across firms
  firmViews: {
    source: string;
    sourceName: string;
    sectorRating: "overweight" | "equal_weight" | "underweight";
    keyReason: string;
    dateIssued: string;
  }[];

  overweightCount: number;
  equalWeightCount: number;
  underweightCount: number;
  consensusView: "overweight" | "equal_weight" | "underweight";

  topPicks: ConsensusRating[];   // Highest consensus stocks in this sector

  sectorMetrics: {
    peRatio: number;
    ytdReturn: number;
    dividendYield: number;
    earningsGrowth: number;
  };

  catalysts: string[];           // Upcoming events that could move the sector
  risks: string[];
}

export interface InvestmentTheme {
  id: string;
  themeName: string;             // "AI Infrastructure", "GLP-1 Revolution", "Rate Cut Beneficiaries"
  description: string;

  supportingFirms: {
    source: string;
    sourceName: string;
    thesis: string;
    datePublished: string;
  }[];

  relatedStocks: {
    ticker: string;
    companyName: string;
    consensusScore: number;
    connection: string;          // Why this stock relates to the theme
  }[];

  timeHorizon: "near_term" | "medium_term" | "long_term";
  riskLevel: "low" | "moderate" | "high" | "speculative";
}
