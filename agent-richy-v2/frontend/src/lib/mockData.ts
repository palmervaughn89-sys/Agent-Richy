/* ── Mock data for testing structured chat components ─────────────────
 *  Import and inject these into the chat to verify rendering
 *  without needing real AI responses.
 * ──────────────────────────────────────────────────────────────────── */

import type { Coupon } from "@/types/coupon";
import type { SavingsReport } from "@/types/spending";
import type { PriceComparison, StoreCategoryRanking, SubscriptionValue } from "@/types/pricing";
import type { ConsensusLeaderboard, ConsensusRating, SectorConsensus, InvestmentTheme } from "@/types/investment";
import type { OptimizedGroceryPlan } from "@/lib/groceryPlanner";
import type { AllocationPlan } from "@/lib/allocationMapper";

/* ── 1. Coupon results ────────────────────────────────────────────── */

export const mockCoupons: Coupon[] = [
  {
    id: "chip-1",
    store: "Chipotle",
    code: "GUAC4FREE",
    description: "Free guacamole with any entrée purchase over $10",
    discountType: "percentage",
    discountValue: 15,
    minimumPurchase: 10,
    expiresAt: "2026-03-31",
    restrictions: "One per customer, not valid with other offers",
    sourceUrl: "https://retailmenot.com/view/chipotle.com",
    affiliateUrl: "https://chipotle.com/order?promo=GUAC4FREE",
    confidence: "verified",
    category: "food",
  },
  {
    id: "chip-2",
    store: "Chipotle",
    code: "BURRITO5",
    description: "$5 off any order of $25 or more",
    discountType: "fixed",
    discountValue: 5,
    minimumPurchase: 25,
    expiresAt: "2026-04-15",
    sourceUrl: "https://coupons.com/chipotle",
    confidence: "verified",
    category: "food",
  },
  {
    id: "chip-3",
    store: "Chipotle",
    code: "BOGO2026",
    description: "Buy one entrée, get one free on Tuesdays",
    discountType: "bogo",
    discountValue: 1,
    expiresAt: "2026-06-30",
    restrictions: "Tuesdays only, dine-in and online orders",
    sourceUrl: "https://slickdeals.net/chipotle-bogo",
    confidence: "likely_valid",
    category: "food",
  },
  {
    id: "chip-4",
    store: "Chipotle",
    code: "CHIPSHIP",
    description: "Free delivery on orders over $15",
    discountType: "free_shipping",
    discountValue: 0,
    minimumPurchase: 15,
    sourceUrl: "https://honey.com/shop/chipotle",
    confidence: "unverified",
    category: "food",
  },
];

export const mockCouponResults = `Here are the best Chipotle deals I found this month! 🌯 The BOGO Tuesday deal is the best value if you're ordering for two.

\`\`\`json
${JSON.stringify(
  {
    type: "coupon_results",
    store: "Chipotle",
    coupons: mockCoupons,
  },
  null,
  2,
)}
\`\`\``;

/* ── 2. Savings report ────────────────────────────────────────────── */

export const mockSavingsReportData: SavingsReport = {
  userId: "demo-user",
  generatedAt: "2026-02-26T12:00:00Z",
  totalMonthlyExpenses: 1247,
  totalPotentialMonthlySavings: 347,
  totalPotentialAnnualSavings: 4164,
  actions: [
    {
      id: "action-1",
      type: "cancel",
      title: "Cancel Peacock Premium",
      description:
        "You haven't mentioned watching Peacock, and your other 3 streaming services (Netflix, Hulu, Disney+) cover most content. You could always use the free tier.",
      targetExpense: "Peacock Premium",
      estimatedMonthlySavings: 7.99,
      estimatedAnnualSavings: 95.88,
      effortLevel: 1,
      timeToRealize: "next_cycle",
    },
    {
      id: "action-2",
      type: "negotiate",
      title: "Negotiate Comcast Internet",
      description:
        "You're paying $80/mo for internet. The market average is $55-65 for comparable speeds. A 10-minute retention call could save you $25/month.",
      targetExpense: "Comcast Internet",
      estimatedMonthlySavings: 25,
      estimatedAnnualSavings: 300,
      effortLevel: 3,
      timeToRealize: "immediate",
      script: "Call 1-800-XFINITY → ask for retention → mention competitor prices",
    },
    {
      id: "action-3",
      type: "switch_annual",
      title: "Switch Spotify to Annual Plan",
      description:
        "You're paying $10.99/mo ($131.88/yr). The annual plan is $109.99 — an instant 17% savings with no change in service.",
      targetExpense: "Spotify Premium",
      estimatedMonthlySavings: 1.82,
      estimatedAnnualSavings: 21.89,
      effortLevel: 1,
      timeToRealize: "next_cycle",
    },
    {
      id: "action-4",
      type: "spend_to_save",
      title: "Smart Thermostat Installation",
      description:
        "A smart thermostat like the Ecobee costs ~$250 upfront but saves an average of $12/month on heating and cooling. Pays for itself in under 21 months.",
      estimatedMonthlySavings: 12,
      estimatedAnnualSavings: 144,
      effortLevel: 2,
      timeToRealize: "1_month",
      upfrontCost: 250,
      roiMonths: 20.8,
    },
    {
      id: "action-5",
      type: "bundle",
      title: "Bundle Disney+ & Hulu",
      description:
        "You're paying $15.99 for Disney+ and $17.99 for Hulu separately ($33.98/mo). The Disney Bundle is $19.99/mo — same content, $14/mo less.",
      targetExpense: "Disney+ & Hulu",
      estimatedMonthlySavings: 13.99,
      estimatedAnnualSavings: 167.88,
      effortLevel: 1,
      timeToRealize: "next_cycle",
    },
    {
      id: "action-6",
      type: "free_alternative",
      title: "Replace LastPass with Bitwarden",
      description:
        "You're paying $3/mo for LastPass Premium. Bitwarden's free tier has the same features — unlimited passwords, cross-device sync, and autofill.",
      targetExpense: "LastPass Premium",
      estimatedMonthlySavings: 3,
      estimatedAnnualSavings: 36,
      effortLevel: 2,
      timeToRealize: "immediate",
      alternativeService: "Bitwarden (free)",
    },
  ],
  subscriptionRedundancies: [
    {
      services: ["Netflix", "Hulu", "Disney+", "Peacock"],
      combinedCost: 51.96,
      suggestion:
        "Four streaming services is a lot! Consider rotating — keep 2 at a time and cycle the others every few months.",
    },
    {
      services: ["iCloud+ 200GB", "Google One 100GB", "Dropbox Plus"],
      combinedCost: 19.97,
      suggestion:
        "You're paying for 3 cloud storage services. Consolidate to one — iCloud if you're Apple-heavy, Google One otherwise. That alone saves ~$13/mo.",
    },
  ],
  benchmarkComparisons: [
    {
      expense: "Internet",
      userPays: 80,
      marketAverage: 58,
      potential: 22,
    },
    {
      expense: "Phone Plan",
      userPays: 85,
      marketAverage: 45,
      potential: 40,
    },
    {
      expense: "Car Insurance",
      userPays: 165,
      marketAverage: 128,
      potential: 37,
    },
  ],
};

export const mockSavingsReport = `I analyzed your spending and found some great opportunities to save! Here's the full breakdown:

\`\`\`json
${JSON.stringify(
  {
    type: "savings_report",
    report: mockSavingsReportData,
  },
  null,
  2,
)}
\`\`\`

Want to tackle any of these? I'd start with the Comcast negotiation — it's the biggest single win at $300/year.`;

/* ── 3. Negotiation script ────────────────────────────────────────── */

export const mockNegotiationScriptData = {
  serviceName: "Comcast Internet",
  currentCost: 80,
  targetCost: 55,
  steps: [
    "Call 1-800-XFINITY and say: \"I'd like to speak with the retention department, please.\"",
    "When connected: \"I've been a loyal customer for [X] years. I've noticed my bill has increased to $80/month and I've found comparable service for less. I'd like to see what you can do to keep me as a customer.\"",
    "If they offer a small discount: \"I appreciate that, but I'm seeing $50-55/month for similar speeds from competitors. Can you match that?\"",
    "If they won't budge: \"I understand. I'd like to schedule a disconnection date for two weeks from now.\" — This usually triggers their best offer.",
    "If they match or beat: \"That sounds great, I appreciate you working with me. Can you confirm that price is locked for at least 12 months?\"",
  ],
  competitorPrices: [
    { name: "T-Mobile Home Internet", price: 50 },
    { name: "AT&T Fiber 300", price: 55 },
    { name: "Verizon Fios 300/300", price: 49.99 },
  ],
};

export const mockNegotiationScript = `Here's your negotiation battle plan for Comcast. This call takes about 10 minutes and could save you $300/year. 💪

\`\`\`json
${JSON.stringify(
  {
    type: "negotiation_script",
    ...mockNegotiationScriptData,
  },
  null,
  2,
)}
\`\`\`

Pro tip: Call on a weekday morning — retention reps have more authority and aren't as rushed.`;

/* ── 4. Spend to save ─────────────────────────────────────────────── */

export const mockSpendToSaveData = {
  title: "Smart Thermostat: Ecobee Smart Thermostat Premium",
  upfrontCost: 250,
  monthlySavings: 12,
  roiMonths: 20.8,
  description:
    "A smart thermostat learns your schedule and automatically adjusts temperature when you're away or asleep. The average household saves $12/month on heating and cooling — that's $144/year. It pays for itself in about 21 months, then it's pure savings after that.",
};

export const mockSpendToSave = `This is a classic spend-to-save move — a small investment now that keeps paying you back every month:

\`\`\`json
${JSON.stringify(
  {
    type: "spend_to_save",
    ...mockSpendToSaveData,
  },
  null,
  2,
)}
\`\`\`

The Ecobee Premium also works with Alexa built-in and has an occupancy sensor, so it's genuinely useful beyond just savings.`;

/* ── 5. Expense input trigger ─────────────────────────────────────── */

export const mockExpenseInput = `Let's take a look at where your money is going! Add your recurring expenses below and I'll analyze them for savings opportunities.

\`\`\`json
${JSON.stringify({ type: "expense_input" })}
\`\`\``;

/* ── Market Intelligence mock data ───────────────────────────────── */

import type {
  MarketIntelligenceReport,
  AnalystInsight,
  SectorOutlook,
} from "@/types/market";

const healthcareInsights: AnalystInsight[] = [
  {
    id: "gs-hc-001",
    source: "Goldman Sachs",
    sourceTier: "tier1_bank",
    date: "2026-02-18",
    sector: "healthcare",
    sentiment: "bullish",
    headline: "Goldman upgrades Healthcare to Overweight",
    summary:
      "Goldman Sachs raised its Healthcare sector rating to Overweight, citing accelerating AI-driven drug discovery pipelines and favorable demographic tailwinds from an aging global population.",
    keyPoints: [
      "AI drug discovery cutting Phase I timelines by 30-40%",
      "Medicare spending projected to grow 7.2% annually through 2030",
      "Large-cap pharma trading at 15% discount to 5-year average P/E",
    ],
    confidence: "high",
    sourceUrl: "https://www.goldmansachs.com/insights/healthcare-outlook-2026",
  },
  {
    id: "ms-hc-002",
    source: "Morningstar",
    sourceTier: "tier2_rating",
    date: "2026-02-12",
    sector: "healthcare",
    sentiment: "bullish",
    headline: "Morningstar: Healthcare sector broadly undervalued",
    summary:
      "Morningstar's sector valuation model shows Healthcare trading at a 12% discount to fair value, with particular opportunity in large-cap biotech and managed care names.",
    keyPoints: [
      "Sector price-to-fair-value ratio at 0.88",
      "Biotech sub-sector at deepest discount since 2023",
      "Managed care benefiting from moderating medical cost trends",
    ],
    confidence: "high",
  },
  {
    id: "ubs-hc-003",
    source: "UBS",
    sourceTier: "tier1_bank",
    date: "2026-02-05",
    sector: "healthcare",
    sentiment: "moderately_bullish",
    headline: "UBS sees selective opportunity in Healthcare",
    summary:
      "UBS maintains a constructive view on Healthcare but warns that regulatory overhang from drug pricing reform could cap upside for some pharmaceutical names.",
    keyPoints: [
      "Favor medtech and diagnostics over branded pharma",
      "Drug pricing reform risk concentrated in top 10 pharma names",
      "GLP-1 market expected to reach $150B by 2030",
    ],
    confidence: "medium",
  },
];

const technologyInsights: AnalystInsight[] = [
  {
    id: "jpm-tech-001",
    source: "JP Morgan",
    sourceTier: "tier1_bank",
    date: "2026-02-20",
    sector: "technology",
    sentiment: "moderately_bullish",
    headline: "JP Morgan maintains Technology Overweight on AI capex cycle",
    summary:
      "JP Morgan sees continued upside in Technology driven by enterprise AI adoption, though acknowledges elevated valuations require strong earnings delivery.",
    keyPoints: [
      "Enterprise AI spending growing 45% YoY",
      "Semiconductor cycle entering new upcycle phase",
      "Valuations ~20% above historical average but justified by growth",
    ],
    confidence: "high",
    sourceUrl: "https://www.jpmorgan.com/insights/technology-2026",
  },
  {
    id: "ms-tech-002",
    source: "Morningstar",
    sourceTier: "tier2_rating",
    date: "2026-02-14",
    sector: "technology",
    sentiment: "neutral",
    headline: "Morningstar: Technology fairly valued after 2025 rally",
    summary:
      "Morningstar's valuation model shows the Technology sector trading near fair value, with limited margin of safety for new positions at current levels.",
    keyPoints: [
      "Sector price-to-fair-value ratio at 1.02",
      "Mega-cap tech fully valued; mid-cap software more attractive",
      "Cloud infrastructure cycle has further runway",
    ],
    confidence: "high",
  },
];

const industrialsInsights: AnalystInsight[] = [
  {
    id: "bofa-ind-001",
    source: "Bank of America",
    sourceTier: "tier1_bank",
    date: "2026-02-15",
    sector: "industrials",
    sentiment: "bullish",
    headline: "BofA upgrades Industrials on infrastructure spending wave",
    summary:
      "Bank of America upgraded Industrials to Overweight, citing the multi-year infrastructure spending cycle from the IIJA and CHIPS Act flowing into real project starts.",
    keyPoints: [
      "$1.2T in infrastructure project starts expected 2026-2028",
      "Reshoring trend boosting domestic manufacturing capex",
      "Defense spending at 4% GDP target driving aerospace demand",
    ],
    confidence: "high",
  },
  {
    id: "fid-ind-002",
    source: "Fidelity",
    sourceTier: "tier2_rating",
    date: "2026-02-10",
    sector: "industrials",
    sentiment: "moderately_bullish",
    headline: "Fidelity Sector Scorecard: Industrials improving",
    summary:
      "Fidelity's proprietary sector scorecard moved Industrials to 'Improving' status based on earnings revisions momentum and relative strength indicators.",
    keyPoints: [
      "Earnings revisions turning positive after 3 quarters of cuts",
      "Order books at multi-year highs for heavy equipment",
      "Wage inflation moderating, improving margin outlook",
    ],
    confidence: "medium",
  },
];

const realEstateInsights: AnalystInsight[] = [
  {
    id: "schw-re-001",
    source: "Schwab",
    sourceTier: "tier2_rating",
    date: "2026-02-17",
    sector: "real_estate",
    sentiment: "moderately_bearish",
    headline: "Schwab downgrades Real Estate to Underweight",
    summary:
      "Schwab moved Real Estate to Underweight, citing persistent rate sensitivity and the structural shift away from traditional office space dampening sector fundamentals.",
    keyPoints: [
      "REITs remain highly correlated to 10-year Treasury movements",
      "Office vacancy rates at 22% nationally with limited recovery",
      "Data center REITs are the exception — strong demand from AI",
    ],
    confidence: "high",
  },
  {
    id: "ms-re-002",
    source: "Morningstar",
    sourceTier: "tier2_rating",
    date: "2026-02-08",
    sector: "real_estate",
    sentiment: "neutral",
    headline: "Morningstar: Select REIT value emerging",
    summary:
      "Morningstar notes that while the broad REIT sector is facing headwinds, select industrial and healthcare REITs are trading below fair value and offer 5%+ dividend yields.",
    keyPoints: [
      "Sector overall near fair value",
      "Industrial REITs undervalued by 8-12%",
      "Dividend yields averaging 4.8% — attractive vs. bonds if rates fall",
    ],
    confidence: "medium",
  },
];

const utilitiesInsights: AnalystInsight[] = [
  {
    id: "ms-util-001",
    source: "Morningstar",
    sourceTier: "tier2_rating",
    date: "2026-02-11",
    sector: "utilities",
    sentiment: "moderately_bearish",
    headline: "Morningstar: Utilities overvalued after defensive rally",
    summary:
      "Morningstar rates the Utilities sector as overvalued following a 2025 defensive rally, with limited growth catalysts and premium valuations relative to historical norms.",
    keyPoints: [
      "Sector price-to-fair-value ratio at 1.08",
      "Earnings growth capped at 4-5% annually",
      "Rising capex for grid modernization pressuring free cash flow",
    ],
    confidence: "high",
  },
  {
    id: "gs-util-002",
    source: "Goldman Sachs",
    sourceTier: "tier1_bank",
    date: "2026-02-06",
    sector: "utilities",
    sentiment: "neutral",
    headline: "Goldman: Utilities neutral, AI power demand is the wildcard",
    summary:
      "Goldman Sachs maintains a Neutral stance on Utilities but flags surging data center power demand as a potential positive catalyst for select utility names with excess generation capacity.",
    keyPoints: [
      "Data center power demand growing 25% YoY",
      "Regulated utilities limited in capturing upside",
      "Independent power producers positioned better for AI power theme",
    ],
    confidence: "medium",
  },
];

const healthcareSector: SectorOutlook = {
  sector: "healthcare",
  sectorName: "Healthcare",
  consensusSentiment: "bullish",
  insights: healthcareInsights,
  bullCount: 3,
  bearCount: 0,
  neutralCount: 0,
  topBullCase:
    "AI-driven drug discovery is cutting development timelines by 30-40%, while aging demographics ensure sustained demand growth. Sector trades at a 12% discount to fair value.",
  topBearCase:
    "Drug pricing reform and regulatory scrutiny could cap upside for large pharma names. Generic competition intensifying in key therapeutic areas.",
  keyMetrics: {
    peRatio: 17.8,
    ytdReturn: 4.2,
    morningstarValuation: "undervalued",
  },
};

const technologySector: SectorOutlook = {
  sector: "technology",
  sectorName: "Technology",
  consensusSentiment: "moderately_bullish",
  insights: technologyInsights,
  bullCount: 1,
  bearCount: 0,
  neutralCount: 1,
  topBullCase:
    "Enterprise AI adoption driving 45% YoY spending growth. Semiconductor upcycle and cloud infrastructure buildout creating multi-year revenue tailwinds.",
  topBearCase:
    "Valuations 20% above historical averages leave limited margin of safety. Any slowdown in AI capex could trigger a sharp re-rating.",
  keyMetrics: {
    peRatio: 28.5,
    ytdReturn: 6.8,
    morningstarValuation: "fairly_valued",
  },
};

const industrialsSector: SectorOutlook = {
  sector: "industrials",
  sectorName: "Industrials",
  consensusSentiment: "moderately_bullish",
  insights: industrialsInsights,
  bullCount: 2,
  bearCount: 0,
  neutralCount: 0,
  topBullCase:
    "$1.2T in infrastructure project starts expected 2026-2028 from IIJA and CHIPS Act. Reshoring trend and defense spending at 4% GDP target provide additional demand.",
  topBearCase:
    "Labor shortages could bottleneck project execution. Margin pressure from supply chain normalization after post-COVID pricing power fades.",
  keyMetrics: {
    peRatio: 21.3,
    ytdReturn: 3.1,
    morningstarValuation: "fairly_valued",
  },
};

const realEstateSector: SectorOutlook = {
  sector: "real_estate",
  sectorName: "Real Estate",
  consensusSentiment: "moderately_bearish",
  insights: realEstateInsights,
  bullCount: 0,
  bearCount: 1,
  neutralCount: 1,
  topBullCase:
    "Select industrial and healthcare REITs trading below fair value with 5%+ dividend yields. Data center REITs seeing strong demand from AI infrastructure buildout.",
  topBearCase:
    "Persistent rate sensitivity and 22% national office vacancy rates create fundamental headwinds. Traditional office REIT recovery unlikely before 2028.",
  keyMetrics: {
    peRatio: 34.2,
    ytdReturn: -1.8,
    morningstarValuation: "fairly_valued",
  },
};

const utilitiesSector: SectorOutlook = {
  sector: "utilities",
  sectorName: "Utilities",
  consensusSentiment: "moderately_bearish",
  insights: utilitiesInsights,
  bullCount: 0,
  bearCount: 1,
  neutralCount: 1,
  topBullCase:
    "Surging data center power demand growing 25% YoY creates a potential catalyst for utilities with excess generation capacity.",
  topBearCase:
    "Sector overvalued after 2025 defensive rally. Earnings growth capped at 4-5% annually while rising grid modernization capex pressures free cash flow.",
  keyMetrics: {
    peRatio: 19.6,
    ytdReturn: 0.4,
    morningstarValuation: "overvalued",
  },
};

export const mockMarketReport: MarketIntelligenceReport = {
  generatedAt: "2026-02-26T00:00:00Z",
  marketSentiment: "moderately_bullish",
  topSectors: [healthcareSector, technologySector, industrialsSector],
  bottomSectors: [realEstateSector, utilitiesSector],
  keyThemes: [
    "AI infrastructure spending",
    "Healthcare innovation cycle",
    "Rate cut timeline uncertainty",
    "Election year policy risk",
  ],
  contrarian:
    "ARK Invest remains aggressively bullish on genomics and autonomous vehicles despite 18 months of underperformance, citing a cluster of upcoming FDA decisions and robotaxi regulatory approvals expected in H2 2026.",
  disclaimer:
    "Market intelligence sourced from public analyst reports and financial press. All views attributed to their respective firms. This is not financial advice.",
};

export const mockAnalystInsight: AnalystInsight = {
  id: "gs-hc-001",
  source: "Goldman Sachs",
  sourceTier: "tier1_bank",
  date: "2026-02-18",
  sector: "healthcare",
  sentiment: "bullish",
  headline: "Goldman upgrades Healthcare to Overweight",
  summary:
    "Goldman Sachs raised its Healthcare sector rating to Overweight, citing accelerating AI-driven drug discovery pipelines and favorable demographic tailwinds from an aging global population.",
  keyPoints: [
    "AI drug discovery cutting Phase I timelines by 30-40%",
    "Medicare spending projected to grow 7.2% annually through 2030",
    "Large-cap pharma trading at 15% discount to 5-year average P/E",
  ],
  priceTarget: undefined,
  currentPrice: undefined,
  sourceUrl: "https://www.goldmansachs.com/insights/healthcare-outlook-2026",
  confidence: "high",
};

/* ── All demo messages keyed for the debug panel ──────────────────── */

export const mockMarketReportMessage = `Here's a comprehensive look at what the major research firms are saying right now. Overall, markets are leaning moderately bullish, with Healthcare and Technology leading sentiment.

\`\`\`json
${JSON.stringify({ type: "market_report", report: mockMarketReport })}
\`\`\`

The biggest theme cutting across all coverage is AI infrastructure spending — it's showing up in Technology (enterprise adoption), Healthcare (drug discovery), Industrials (data center construction), and even Utilities (power demand). Rate cut timing remains the wildcard that could shift the picture.`;

export const mockAnalystInsightMessage = `Goldman Sachs just dropped a notable upgrade — here's the key takeaway:

\`\`\`json
${JSON.stringify({ type: "analyst_insight", insight: mockAnalystInsight })}
\`\`\`

This is significant because Goldman typically lags on sector upgrades — when they move, it often signals broad institutional repositioning. Worth watching the healthcare ETFs over the next few weeks.`;

/* ── 8. Price comparison ──────────────────────────────────────────── */

export const mockPriceComparison: PriceComparison = {
  id: "pc-tide-001",
  productName: "Tide Pods 42-count",
  category: "home_garden",
  userPaidPrice: 13.99,
  userPaidStore: "Walgreens",
  bestPrice: {
    store: "costco",
    storeName: "Costco",
    price: 8.49,
    unitPrice: 0.20,
    unit: "pod",
    inStock: true,
    lastVerified: "2026-02-26",
    isOnSale: false,
    membershipRequired: true,
    shippingCost: 0,
  },
  allPrices: [
    {
      store: "costco",
      storeName: "Costco",
      price: 8.49,
      unitPrice: 0.20,
      unit: "pod",
      inStock: true,
      lastVerified: "2026-02-26",
      isOnSale: false,
      membershipRequired: true,
      shippingCost: 0,
    },
    {
      store: "amazon",
      storeName: "Amazon",
      price: 10.99,
      unitPrice: 0.26,
      unit: "pod",
      url: "https://amazon.com/dp/B07TH4NRMK",
      inStock: true,
      lastVerified: "2026-02-26",
      isOnSale: false,
      primeRequired: true,
      shippingCost: 0,
    },
    {
      store: "walmart",
      storeName: "Walmart",
      price: 11.47,
      unitPrice: 0.27,
      unit: "pod",
      url: "https://walmart.com/ip/tide-pods-42ct",
      inStock: true,
      lastVerified: "2026-02-26",
      isOnSale: false,
      shippingCost: 0,
    },
    {
      store: "target",
      storeName: "Target",
      price: 12.49,
      unitPrice: 0.30,
      unit: "pod",
      url: "https://target.com/p/tide-pods-42ct",
      inStock: true,
      lastVerified: "2026-02-26",
      isOnSale: false,
      shippingCost: 0,
    },
    {
      store: "walgreens",
      storeName: "Walgreens",
      price: 13.99,
      unitPrice: 0.33,
      unit: "pod",
      inStock: true,
      lastVerified: "2026-02-26",
      isOnSale: false,
      shippingCost: 0,
    },
  ],
  savingsAmount: 5.50,
  savingsPercent: 39.3,
  recommendation:
    "Costco has this 39% cheaper. Even factoring in the $65 annual membership, if you buy this monthly you'd save $66/year minus the membership cost — so about $1/year net savings on this item alone. But combined with other Costco purchases it adds up fast.",
};

/* ── 9. Store ranking (groceries) ─────────────────────────────────── */

export const mockStoreRanking: StoreCategoryRanking = {
  category: "groceries",
  categoryName: "Groceries",
  lastUpdated: "2026-02-01",
  source: "Consumer Reports, USDA ERS Food Price Outlook, NerdWallet",
  rankings: [
    { rank: 1, store: "aldi", storeName: "Aldi", avgPriceIndex: 78, bestFor: "Everyday staples, produce, store brand quality rivals name brands", watchOut: "Limited selection, no name brands, inconsistent stock on specialty items" },
    { rank: 2, store: "costco", storeName: "Costco", avgPriceIndex: 80, bestFor: "Bulk buying for families, meat and dairy, organic options", watchOut: "Requires $65+/year membership, must buy large quantities, easy to overspend" },
    { rank: 3, store: "walmart", storeName: "Walmart", avgPriceIndex: 85, bestFor: "One-stop shopping, Great Value brand, price matching", watchOut: "Produce quality varies, crowded stores, less organic selection" },
    { rank: 4, store: "kroger", storeName: "Kroger", avgPriceIndex: 90, bestFor: "Sale cycles are excellent, fuel points, digital coupons stack well", watchOut: "Regular prices are average, need to shop sales strategically" },
    { rank: 5, store: "target", storeName: "Target", avgPriceIndex: 92, bestFor: "Good Gather brand is solid, RedCard saves 5% on everything", watchOut: "Higher on staples without RedCard, smaller grocery selection" },
    { rank: 6, store: "trader_joes", storeName: "Trader Joe's", avgPriceIndex: 88, bestFor: "Unique store brands, frozen meals, snacks, wine", watchOut: "No sales or coupons ever, limited conventional brands, small stores" },
    { rank: 7, store: "publix", storeName: "Publix", avgPriceIndex: 105, bestFor: "BOGO sales are genuinely good, bakery and deli, clean stores", watchOut: "Regular prices are 15-20% above average, Southeast US only" },
    { rank: 8, store: "whole_foods", storeName: "Whole Foods", avgPriceIndex: 118, bestFor: "Organic selection, Prime member deals on Wednesdays, quality standards", watchOut: "Premium pricing on everything, Prime deals are limited" },
  ],
};

/* ── 10. Subscription value ───────────────────────────────────────── */

export const mockSubscriptionValue: SubscriptionValue[] = [
  {
    id: "sub-netflix",
    serviceName: "Netflix",
    monthlyCost: 15.49,
    hoursUsedPerMonth: 22,
    costPerHour: 0.70,
    category: "streaming",
    valueRating: "good",
    recommendation: "Good value at $0.70/hour. You're using it regularly — keep it.",
    alternativeOptions: [
      { name: "Netflix Basic with Ads", cost: 6.99, note: "Same content, ads during shows" },
    ],
  },
  {
    id: "sub-spotify",
    serviceName: "Spotify Premium",
    monthlyCost: 11.99,
    hoursUsedPerMonth: 45,
    costPerHour: 0.27,
    category: "music",
    valueRating: "excellent",
    recommendation: "Excellent value at $0.27/hour — one of your best subscriptions.",
  },
  {
    id: "sub-hbo",
    serviceName: "HBO Max",
    monthlyCost: 16.99,
    hoursUsedPerMonth: 4,
    costPerHour: 4.25,
    category: "streaming",
    valueRating: "poor",
    recommendation: "At $4.25/hour, you're paying movie-theater prices for streaming. Consider canceling and resubscribing when a show you want drops.",
    alternativeOptions: [
      { name: "HBO Max with Ads", cost: 9.99, note: "Same content, would drop cost to $2.50/hr" },
      { name: "Cancel & rotate", cost: 0, note: "Subscribe only when a new season drops, cancel after binging" },
    ],
  },
  {
    id: "sub-adobe",
    serviceName: "Adobe Creative Cloud",
    monthlyCost: 54.99,
    hoursUsedPerMonth: 60,
    costPerHour: 0.92,
    category: "productivity",
    valueRating: "good",
    recommendation: "Good value for a work tool at $0.92/hour. If you mainly use Photoshop + Lightroom, the Photography Plan at $9.99/mo could save you $45/mo.",
    alternativeOptions: [
      { name: "Adobe Photography Plan", cost: 9.99, note: "Photoshop + Lightroom only" },
      { name: "Affinity Suite", cost: 2.50, note: "One-time $170 purchase, no subscription" },
    ],
  },
  {
    id: "sub-peacock",
    serviceName: "Peacock Premium",
    monthlyCost: 7.99,
    hoursUsedPerMonth: 0,
    costPerHour: 0,
    category: "streaming",
    valueRating: "unused",
    recommendation: "You haven't used Peacock at all this month. Cancel immediately — that's $96/year you're lighting on fire.",
  },
];

/* ── Wrapped demo messages for debug panel ───────────────────────── */

export const mockPriceComparisonMessage = `I found the Tide Pods 42-count at several stores — here's the breakdown:

\`\`\`json
${JSON.stringify({ type: "price_comparison", comparison: mockPriceComparison })}
\`\`\`

Costco wins by a wide margin, but you need a membership. Without one, Amazon with Prime is your next best bet at $10.99.`;

export const mockStoreRankingMessage = `Here are the best grocery stores ranked by overall price:

\`\`\`json
${JSON.stringify({ type: "store_ranking", ranking: mockStoreRanking })}
\`\`\`

Aldi and Costco consistently beat everyone on price. The real question is whether the limited selection at Aldi or the membership at Costco works for your shopping style.`;

export const mockSubscriptionValueMessage = `I scored all 5 of your subscriptions — here's where your money's going:

\`\`\`json
${JSON.stringify({ type: "subscription_value", subscriptions: mockSubscriptionValue })}
\`\`\`

Quick wins: Cancel Peacock immediately ($96/year saved) and consider downgrading HBO Max to the ads plan or rotating on/off.`;

// ── Goal Simulation mock data ────────────────────────────────────────────

import type { GoalSimulationResult } from "@/types/tools";
import type { BillPrediction, TrackedBill } from "@/types/tools";
import type { LocalDeal, LocalDealReport } from "@/types/tools";
import type { AnalyzedReceipt } from "@/types/tools";

export const mockGoalSimulation: GoalSimulationResult = {
  goalId: "goal_ef_001",
  goalName: "Emergency Fund",
  goalType: "emergency_fund",
  targetAmount: 10000,
  currentSaved: 2300,
  monthlyContribution: 400,
  monthsToGoal: 19.3,
  projectedCompletionDate: "2027-10-01",
  totalContributed: 7700,
  totalInterestEarned: 0,
  scenarios: [
    {
      name: "Current Pace",
      monthlyAmount: 400,
      monthsToGoal: 19.3,
      completionDate: "2027-10-01",
      totalInterestEarned: 0,
      description: "At your current $400/month, you'll hit $10K in about 19 months.",
    },
    {
      name: "With Optimizer Savings",
      monthlyAmount: 637,
      monthsToGoal: 12.1,
      completionDate: "2027-03-01",
      totalInterestEarned: 0,
      description: "Apply the $237/month we found in your spending analysis and cut 7 months off.",
    },
    {
      name: "Aggressive",
      monthlyAmount: 800,
      monthsToGoal: 9.6,
      completionDate: "2026-12-15",
      totalInterestEarned: 0,
      description: "Max out savings by cutting all discretionary spending — done before 2027.",
    },
  ],
  milestones: [
    { percentage: 25, amount: 2500, projectedDate: "2026-03-15", monthsFromNow: 0.5 },
    { percentage: 50, amount: 5000, projectedDate: "2026-10-01", monthsFromNow: 6.8 },
    { percentage: 75, amount: 7500, projectedDate: "2027-04-15", monthsFromNow: 13.3 },
    { percentage: 100, amount: 10000, projectedDate: "2027-10-01", monthsFromNow: 19.3 },
  ],
  dailyEquivalent: 13.33,
  weeklyEquivalent: 92.31,
  boostSuggestions: [
    {
      action: "Cancel Peacock → saves $7.99/mo",
      monthlySavingsIncrease: 7.99,
      newMonthsToGoal: 18.9,
      timeSaved: 0.4,
    },
    {
      action: "Negotiate internet bill → saves $25/mo",
      monthlySavingsIncrease: 25,
      newMonthsToGoal: 18.1,
      timeSaved: 1.2,
    },
    {
      action: "Downgrade HBO Max to ads plan → saves $5/mo",
      monthlySavingsIncrease: 5,
      newMonthsToGoal: 19.0,
      timeSaved: 0.3,
    },
  ],
  monteCarlo: {
    simulations: 1000,
    percentile10: 8900,
    percentile25: 9400,
    percentile50: 10000,
    percentile75: 10600,
    percentile90: 11200,
    probabilityOfSuccess: 87,
  },
};

export const mockGoalSimulationMessage = `Here's your Emergency Fund simulation — you're already 23% there! 💪

\`\`\`json
${JSON.stringify({ type: "goal_simulation", result: mockGoalSimulation })}
\`\`\`

That's just $13.33 per day. Skip one lunch out and you're on track. With the optimizer savings we found, you could be done 7 months sooner.`;

// ── Bill Prediction mock data ────────────────────────────────────────────

const billRent: TrackedBill = {
  id: "bill_001",
  name: "Rent",
  category: "Housing",
  amount: 1450,
  frequency: "monthly",
  nextDueDate: "2026-03-01",
  autopay: true,
  provider: "Greystar Properties",
};

const billCarInsurance: TrackedBill = {
  id: "bill_002",
  name: "Car Insurance",
  category: "Insurance",
  amount: 180,
  frequency: "semi_annual",
  nextDueDate: "2026-03-01",
  autopay: false,
  provider: "State Farm",
};

const billElectric: TrackedBill = {
  id: "bill_003",
  name: "Electric",
  category: "Utilities",
  amount: 137,
  frequency: "monthly",
  nextDueDate: "2026-03-12",
  autopay: false,
  provider: "Georgia Power",
  historicalAmounts: [
    { date: "2025-12-12", amount: 95 },
    { date: "2026-01-12", amount: 142 },
    { date: "2026-02-12", amount: 168 },
  ],
};

const billInternet: TrackedBill = {
  id: "bill_004",
  name: "Internet",
  category: "Telecom",
  amount: 55,
  frequency: "monthly",
  nextDueDate: "2026-03-08",
  autopay: true,
  provider: "Xfinity",
};

const billPhone: TrackedBill = {
  id: "bill_005",
  name: "Phone",
  category: "Telecom",
  amount: 45,
  frequency: "monthly",
  nextDueDate: "2026-03-15",
  autopay: true,
  provider: "T-Mobile",
};

const billNetflix: TrackedBill = {
  id: "bill_006",
  name: "Netflix",
  category: "Subscriptions",
  amount: 15.49,
  frequency: "monthly",
  nextDueDate: "2026-03-22",
  autopay: true,
  provider: "Netflix",
};

const billSpotify: TrackedBill = {
  id: "bill_007",
  name: "Spotify",
  category: "Subscriptions",
  amount: 11.99,
  frequency: "monthly",
  nextDueDate: "2026-03-18",
  autopay: true,
  provider: "Spotify",
};

const billGym: TrackedBill = {
  id: "bill_008",
  name: "Planet Fitness",
  category: "Memberships",
  amount: 29.99,
  frequency: "monthly",
  nextDueDate: "2026-03-05",
  autopay: true,
  provider: "Planet Fitness",
};

export const mockBillPrediction: BillPrediction = {
  period: "March 2026",
  startDate: "2026-03-01",
  endDate: "2026-03-31",
  bills: [
    { bill: billRent, dueDate: "2026-03-01", amount: 1450, isEstimate: false },
    { bill: billCarInsurance, dueDate: "2026-03-01", amount: 180, isEstimate: false },
    { bill: billGym, dueDate: "2026-03-05", amount: 29.99, isEstimate: false },
    { bill: billInternet, dueDate: "2026-03-08", amount: 55, isEstimate: false },
    { bill: billElectric, dueDate: "2026-03-12", amount: 137, isEstimate: true, varianceNote: "Your electric bill averages $137 but ranges $95–$180" },
    { bill: billPhone, dueDate: "2026-03-15", amount: 45, isEstimate: false },
    { bill: billSpotify, dueDate: "2026-03-18", amount: 11.99, isEstimate: false },
    { bill: billNetflix, dueDate: "2026-03-22", amount: 15.49, isEstimate: false },
  ],
  totalPredicted: 1924.47,
  comparedToLastMonth: 180,
  comparedToLastMonthPercent: 10.3,
  unusualItems: [
    {
      billName: "Car Insurance",
      reason: "Semi-annual renewal",
      amount: 180,
    },
  ],
  calendarView: [
    { date: "2026-03-01", bills: [{ name: "Rent", amount: 1450 }, { name: "Car Insurance", amount: 180 }], dailyTotal: 1630 },
    { date: "2026-03-05", bills: [{ name: "Planet Fitness", amount: 29.99 }], dailyTotal: 29.99 },
    { date: "2026-03-08", bills: [{ name: "Internet", amount: 55 }], dailyTotal: 55 },
    { date: "2026-03-12", bills: [{ name: "Electric", amount: 137 }], dailyTotal: 137 },
    { date: "2026-03-15", bills: [{ name: "Phone", amount: 45 }], dailyTotal: 45 },
    { date: "2026-03-18", bills: [{ name: "Spotify", amount: 11.99 }], dailyTotal: 11.99 },
    { date: "2026-03-22", bills: [{ name: "Netflix", amount: 15.49 }], dailyTotal: 15.49 },
  ],
  cashFlowWarnings: [
    {
      date: "2026-03-01",
      warning: "Rent + car insurance both hit on the 1st — $1,630 in one day. Make sure your account is funded.",
      totalDue: 1630,
    },
  ],
};

export const mockBillPredictionMessage = `Here's your March bill forecast — heads up, it's a bigger month:

\`\`\`json
${JSON.stringify({ type: "bill_prediction", prediction: mockBillPrediction })}
\`\`\`

Your car insurance renewal adds $180 to the usual run. Both rent and insurance hit on March 1st, so make sure you have $1,630 ready.`;

// ── Local Deals mock data ────────────────────────────────────────────────

const matchedDealChicken: LocalDeal = {
  id: "deal_m1",
  store: "kroger",
  storeName: "Kroger",
  storeAddress: "3245 Buford Dr, Buford GA 30519",
  distanceMiles: 2.1,
  dealType: "sale",
  productName: "Boneless Chicken Breast",
  productCategory: "Meat & Seafood",
  originalPrice: 4.99,
  salePrice: 2.99,
  savings: 2.00,
  savingsPercent: 40,
  validFrom: "2026-02-25",
  validUntil: "2026-03-03",
  source: "Kroger weekly ad",
  requiresLoyaltyCard: true,
  requiresMembership: false,
  userBuysThis: true,
  usualPrice: 4.99,
  isHistoricLow: true,
};

const matchedDealTide: LocalDeal = {
  id: "deal_m2",
  store: "cvs",
  storeName: "CVS Pharmacy",
  storeAddress: "4120 Hamilton Mill Rd, Buford GA 30518",
  distanceMiles: 0.8,
  dealType: "bogo",
  productName: "Tide Pods 42-count",
  productCategory: "Household",
  originalPrice: 13.99,
  salePrice: 6.99,
  savings: 7.00,
  savingsPercent: 50,
  validFrom: "2026-02-23",
  validUntil: "2026-03-01",
  source: "CVS weekly ad",
  requiresLoyaltyCard: true,
  requiresMembership: false,
  userBuysThis: true,
  usualPrice: 13.99,
  isHistoricLow: false,
};

const matchedDealGas: LocalDeal = {
  id: "deal_m3",
  store: "costco",
  storeName: "Costco Gas",
  storeAddress: "3200 Woodward Crossing Blvd, Buford GA 30519",
  distanceMiles: 3.4,
  dealType: "loyalty",
  productName: "Regular Unleaded Gas (per gallon)",
  productCategory: "Fuel",
  originalPrice: 3.19,
  salePrice: 2.89,
  savings: 0.30,
  savingsPercent: 9,
  validFrom: "2026-02-27",
  validUntil: "2026-03-06",
  source: "Costco Gas",
  requiresLoyaltyCard: false,
  requiresMembership: true,
  userBuysThis: true,
  usualPrice: 3.19,
  isHistoricLow: false,
};

const topDeal1: LocalDeal = {
  id: "deal_t1",
  store: "publix",
  storeName: "Publix",
  storeAddress: "3435 Braselton Hwy, Dacula GA 30019",
  distanceMiles: 4.2,
  dealType: "bogo",
  productName: "Publix Premium Ice Cream (all varieties)",
  productCategory: "Frozen",
  originalPrice: 7.49,
  salePrice: 3.75,
  savings: 3.74,
  savingsPercent: 50,
  validFrom: "2026-02-26",
  validUntil: "2026-03-04",
  source: "Publix weekly ad",
  requiresLoyaltyCard: false,
  requiresMembership: false,
  userBuysThis: false,
  usualPrice: 0,
  isHistoricLow: false,
};

const topDeal2: LocalDeal = {
  id: "deal_t2",
  store: "target",
  storeName: "Target",
  storeAddress: "3200 Mall of Georgia Blvd, Buford GA 30519",
  distanceMiles: 3.0,
  dealType: "sale",
  productName: "Clorox Disinfecting Wipes 3-pack",
  productCategory: "Household",
  originalPrice: 12.99,
  salePrice: 8.49,
  savings: 4.50,
  savingsPercent: 35,
  validFrom: "2026-02-23",
  validUntil: "2026-03-01",
  source: "Target Circle",
  requiresLoyaltyCard: true,
  requiresMembership: false,
  userBuysThis: false,
  usualPrice: 0,
  isHistoricLow: false,
};

const topDeal3: LocalDeal = {
  id: "deal_t3",
  store: "aldi",
  storeName: "ALDI",
  storeAddress: "2925 Buford Dr, Buford GA 30519",
  distanceMiles: 2.5,
  dealType: "sale",
  productName: "Fresh Atlantic Salmon Fillets (per lb)",
  productCategory: "Meat & Seafood",
  originalPrice: 9.99,
  salePrice: 6.99,
  savings: 3.00,
  savingsPercent: 30,
  validFrom: "2026-02-26",
  validUntil: "2026-03-04",
  source: "ALDI Finds",
  requiresLoyaltyCard: false,
  requiresMembership: false,
  userBuysThis: false,
  usualPrice: 0,
  isHistoricLow: true,
};

const topDeal4: LocalDeal = {
  id: "deal_t4",
  store: "kroger",
  storeName: "Kroger",
  storeAddress: "3245 Buford Dr, Buford GA 30519",
  distanceMiles: 2.1,
  dealType: "sale",
  productName: "Coca-Cola 12-Pack Cans",
  productCategory: "Beverages",
  originalPrice: 7.99,
  salePrice: 3.99,
  savings: 4.00,
  savingsPercent: 50,
  validFrom: "2026-02-25",
  validUntil: "2026-03-03",
  source: "Kroger weekly ad",
  requiresLoyaltyCard: true,
  requiresMembership: false,
  limitPerCustomer: 4,
  userBuysThis: false,
  usualPrice: 0,
  isHistoricLow: false,
};

export const mockLocalDeals: LocalDealReport = {
  zipCode: "30518",
  generatedAt: "2026-02-27T10:00:00Z",
  radius: 5,
  topDeals: [topDeal1, topDeal2, topDeal3, topDeal4],
  matchedDeals: [matchedDealChicken, matchedDealTide, matchedDealGas],
  weeklyAdHighlights: [
    {
      store: "kroger",
      storeName: "Kroger",
      topDeals: [
        { item: "Boneless Chicken Breast", salePrice: 2.99, savings: "Save $2.00/lb" },
        { item: "Coca-Cola 12-Pack", salePrice: 3.99, savings: "Save $4.00" },
        { item: "Kroger Brand Milk (gallon)", salePrice: 2.49, savings: "Save $1.30" },
        { item: "Strawberries 1lb", salePrice: 2.50, savings: "Save $2.49" },
      ],
      adValidDates: "Feb 25 – Mar 3, 2026",
    },
    {
      store: "publix",
      storeName: "Publix",
      topDeals: [
        { item: "Premium Ice Cream (BOGO)", salePrice: 3.75, savings: "Save $3.74" },
        { item: "Boar's Head Deli Meats", salePrice: 8.99, savings: "Save $3.00/lb" },
        { item: "Publix Ground Beef 80/20", salePrice: 3.99, savings: "Save $2.00/lb" },
      ],
      adValidDates: "Feb 26 – Mar 4, 2026",
    },
  ],
  totalPotentialSavings: 34.50,
};

export const mockLocalDealsMessage = `Found 7 deals within 5 miles of 30518 — here's what's hot this week:

\`\`\`json
${JSON.stringify({ type: "local_deals", report: mockLocalDeals })}
\`\`\`

The chicken deal at Kroger is a historic low — if you usually buy at Publix, this alone saves you $2/lb. The Tide BOGO at CVS is solid too. Just remember your Kroger Plus card!`;

// ── Receipt Analysis mock data ───────────────────────────────────────────

export const mockReceiptAnalysis: AnalyzedReceipt = {
  id: "receipt_001",
  store: "Publix",
  storeAddress: "3435 Braselton Hwy, Dacula GA 30019",
  date: "2026-02-26",
  items: [
    { name: "Boneless Chicken Breast", quantity: 2, unitPrice: 4.99, totalPrice: 9.98, category: "Meat", taxable: false },
    { name: "Ground Turkey 93/7", quantity: 1, unitPrice: 5.49, totalPrice: 5.49, category: "Meat", taxable: false },
    { name: "Atlantic Salmon Fillet", quantity: 1, unitPrice: 11.49, totalPrice: 11.49, category: "Meat", taxable: false },
    { name: "Organic Baby Spinach", quantity: 1, unitPrice: 4.29, totalPrice: 4.29, category: "Produce", taxable: false },
    { name: "Avocados (bag of 4)", quantity: 1, unitPrice: 3.99, totalPrice: 3.99, category: "Produce", taxable: false },
    { name: "Bananas", quantity: 1, unitPrice: 1.69, totalPrice: 1.69, category: "Produce", taxable: false },
    { name: "Roma Tomatoes", quantity: 1, unitPrice: 2.49, totalPrice: 2.49, category: "Produce", taxable: false },
    { name: "Bell Peppers (3-pack)", quantity: 1, unitPrice: 3.99, totalPrice: 3.99, category: "Produce", taxable: false },
    { name: "Whole Milk (gallon)", quantity: 1, unitPrice: 4.59, totalPrice: 4.59, category: "Dairy", taxable: false },
    { name: "Shredded Cheddar Cheese", quantity: 1, unitPrice: 3.49, totalPrice: 3.49, category: "Dairy", taxable: false },
    { name: "Greek Yogurt (4-pack)", quantity: 1, unitPrice: 5.49, totalPrice: 5.49, category: "Dairy", taxable: false },
    { name: "Olive Oil Extra Virgin", quantity: 1, unitPrice: 8.99, totalPrice: 8.99, category: "Pantry", taxable: false },
    { name: "Paper Towels 6-Roll", quantity: 1, unitPrice: 9.49, totalPrice: 9.49, category: "Household", taxable: true },
    { name: "Whole Wheat Pasta", quantity: 2, unitPrice: 1.79, totalPrice: 3.58, category: "Pantry", taxable: false },
  ],
  subtotal: 79.49,
  tax: 7.94,
  total: 87.43,
  paymentMethod: "Debit Card",
  categoryBreakdown: [
    { category: "Meat", amount: 26.96, percentage: 31, itemCount: 3 },
    { category: "Produce", amount: 16.45, percentage: 19, itemCount: 5 },
    { category: "Dairy", amount: 13.57, percentage: 16, itemCount: 3 },
    { category: "Pantry", amount: 12.57, percentage: 14, itemCount: 2 },
    { category: "Household", amount: 9.49, percentage: 11, itemCount: 1 },
  ],
  priceAlerts: [
    {
      item: "Boneless Chicken Breast",
      paidPrice: 4.99,
      betterPrice: 2.99,
      betterStore: "Kroger",
      savings: 2.00,
    },
    {
      item: "Paper Towels 6-Roll",
      paidPrice: 9.49,
      betterPrice: 6.99,
      betterStore: "Costco",
      savings: 2.50,
    },
    {
      item: "Olive Oil Extra Virgin",
      paidPrice: 8.99,
      betterPrice: 5.99,
      betterStore: "ALDI",
      savings: 3.00,
    },
  ],
  comparedToAverage: {
    thisTrip: 87.43,
    averageTrip: 72.00,
    difference: 15.43,
    trend: "increasing",
  },
};

export const mockReceiptAnalysisMessage = `Here's your Publix receipt breakdown — I found a few places you could save:

\`\`\`json
${JSON.stringify({ type: "receipt_analysis", receipt: mockReceiptAnalysis })}
\`\`\`

You could save $7.50 next time by grabbing chicken at Kroger (it's on sale this week!), paper towels at Costco, and olive oil at ALDI. Your grocery spending has been trending up — might be worth checking the deal radar for this week's sales.`;

/* ── 15. Consensus Leaderboard ────────────────────────────────────── */

export const mockConsensusLeaderboard: ConsensusLeaderboard = {
  generatedAt: "2026-02-26T00:00:00Z",
  category: "Overall",
  categoryDescription: "Top rated stocks across all sectors by analyst consensus",
  timeframe: "February 2026 Analyst Consensus",
  topRated: [
    {
      ticker: "NVDA",
      companyName: "NVIDIA Corporation",
      sector: "Technology",
      consensusScore: 91,
      consensusLabel: "Strong Buy",
      buyCount: 42,
      holdCount: 5,
      sellCount: 0,
      totalRatings: 47,
      currentPrice: 875.00,
      avgPriceTarget: 1050.00,
      highPriceTarget: 1400.00,
      lowPriceTarget: 700.00,
      medianPriceTarget: 1025.00,
      impliedUpside: 20.0,
      ratings: [],
      morningstarStars: 4,
      morningstarFairValue: 950.00,
      morningstarMoat: "wide",
      peRatio: 62.5,
      forwardPE: 38.2,
      dividendYield: 0.02,
      beta: 1.65,
      marketCap: "2.2T",
      revenueGrowthYoY: 122.0,
      bullCase: "AI capex super-cycle. Data center GPU monopoly.",
      bearCase: "Valuation stretched. China export risk.",
      lastUpdated: "2026-02-26",
      disclaimer: "All ratings sourced from public analyst reports. Not investment advice.",
    },
    {
      ticker: "META",
      companyName: "Meta Platforms Inc.",
      sector: "Technology",
      consensusScore: 86,
      consensusLabel: "Strong Buy",
      buyCount: 38,
      holdCount: 8,
      sellCount: 1,
      totalRatings: 47,
      currentPrice: 505.00,
      avgPriceTarget: 585.00,
      highPriceTarget: 680.00,
      lowPriceTarget: 400.00,
      medianPriceTarget: 570.00,
      impliedUpside: 15.8,
      ratings: [],
      morningstarStars: 4,
      morningstarFairValue: 560.00,
      morningstarMoat: "wide",
      peRatio: 25.1,
      forwardPE: 21.3,
      dividendYield: 0.40,
      beta: 1.22,
      marketCap: "1.3T",
      revenueGrowthYoY: 25.0,
      bullCase: "Reels monetization. AI ad targeting gains.",
      bearCase: "Reality Labs losses. Regulatory risk.",
      lastUpdated: "2026-02-26",
      disclaimer: "All ratings sourced from public analyst reports. Not investment advice.",
    },
    {
      ticker: "LLY",
      companyName: "Eli Lilly and Company",
      sector: "Healthcare",
      consensusScore: 88,
      consensusLabel: "Strong Buy",
      buyCount: 25,
      holdCount: 3,
      sellCount: 0,
      totalRatings: 28,
      currentPrice: 780.00,
      avgPriceTarget: 920.00,
      highPriceTarget: 1100.00,
      lowPriceTarget: 650.00,
      medianPriceTarget: 900.00,
      impliedUpside: 17.9,
      ratings: [],
      morningstarStars: 3,
      morningstarFairValue: 680.00,
      morningstarMoat: "wide",
      peRatio: 118.0,
      forwardPE: 52.0,
      dividendYield: 0.65,
      beta: 0.42,
      marketCap: "740B",
      revenueGrowthYoY: 36.0,
      bullCase: "GLP-1 drug dominance (Mounjaro/Zepbound). Pipeline depth.",
      bearCase: "Premium valuation. Patent cliff in 2030s.",
      lastUpdated: "2026-02-26",
      disclaimer: "All ratings sourced from public analyst reports. Not investment advice.",
    },
    {
      ticker: "AMZN",
      companyName: "Amazon.com Inc.",
      sector: "Consumer Discretionary",
      consensusScore: 84,
      consensusLabel: "Buy",
      buyCount: 45,
      holdCount: 10,
      sellCount: 0,
      totalRatings: 55,
      currentPrice: 187.00,
      avgPriceTarget: 225.00,
      highPriceTarget: 270.00,
      lowPriceTarget: 170.00,
      medianPriceTarget: 220.00,
      impliedUpside: 20.3,
      ratings: [],
      morningstarStars: 4,
      morningstarFairValue: 210.00,
      morningstarMoat: "wide",
      peRatio: 58.5,
      forwardPE: 35.0,
      dividendYield: 0.0,
      beta: 1.15,
      marketCap: "1.9T",
      revenueGrowthYoY: 12.0,
      bullCase: "AWS re-acceleration. Advertising growth.",
      bearCase: "Retail margin pressure. Antitrust scrutiny.",
      lastUpdated: "2026-02-26",
      disclaimer: "All ratings sourced from public analyst reports. Not investment advice.",
    },
    {
      ticker: "JPM",
      companyName: "JPMorgan Chase & Co.",
      sector: "Financials",
      consensusScore: 79,
      consensusLabel: "Buy",
      buyCount: 18,
      holdCount: 7,
      sellCount: 1,
      totalRatings: 26,
      currentPrice: 198.00,
      avgPriceTarget: 220.00,
      highPriceTarget: 250.00,
      lowPriceTarget: 180.00,
      medianPriceTarget: 215.00,
      impliedUpside: 11.1,
      ratings: [],
      morningstarStars: 3,
      morningstarFairValue: 190.00,
      morningstarMoat: "wide",
      peRatio: 11.8,
      forwardPE: 11.2,
      dividendYield: 2.15,
      beta: 1.08,
      marketCap: "570B",
      revenueGrowthYoY: 8.0,
      bullCase: "Best-in-class management. Net interest income strength.",
      bearCase: "CRE exposure. Regulatory capital requirements.",
      lastUpdated: "2026-02-26",
      disclaimer: "All ratings sourced from public analyst reports. Not investment advice.",
    },
  ],
  sectorBreakdown: [
    { sector: "Technology", stockCount: 2, avgConsensusScore: 88.5, topPick: "NVDA" },
    { sector: "Healthcare", stockCount: 1, avgConsensusScore: 88.0, topPick: "LLY" },
    { sector: "Consumer Discretionary", stockCount: 1, avgConsensusScore: 84.0, topPick: "AMZN" },
    { sector: "Financials", stockCount: 1, avgConsensusScore: 79.0, topPick: "JPM" },
  ],
  methodology: "Consensus scores aggregate Buy/Hold/Sell ratings from 15+ major sell-side and buy-side firms, weighted by recency and historic accuracy. Morningstar data supplements with fair value estimates and economic moat analysis.",
  sources: ["Goldman Sachs", "JP Morgan", "Morgan Stanley", "Morningstar", "Fidelity", "Schwab", "Bank of America", "UBS"],
  disclaimer: "All ratings are aggregated from publicly available research and belong to their respective firms. This is educational content, not investment advice. Past performance does not guarantee future results.",
};

export const mockConsensusLeaderboardMessage = `Here are the top analyst-rated stocks across major sectors — these are the names getting the most bullish consensus from Wall Street right now:

\`\`\`json
${JSON.stringify({ type: "consensus_leaderboard", leaderboard: mockConsensusLeaderboard })}
\`\`\`

NVIDIA leads the pack with a 91 consensus score, driven by the AI infrastructure super-cycle. Eli Lilly is the standout in healthcare with GLP-1 drug dominance. Want me to dive deeper into any of these stocks?`;

/* ── 16. Stock Consensus ──────────────────────────────────────────── */

export const mockStockConsensus: ConsensusRating = {
  ticker: "NVDA",
  companyName: "NVIDIA Corporation",
  sector: "Technology",
  consensusScore: 91,
  consensusLabel: "Strong Buy",
  buyCount: 42,
  holdCount: 5,
  sellCount: 0,
  totalRatings: 47,
  currentPrice: 875.00,
  avgPriceTarget: 1050.00,
  highPriceTarget: 1400.00,
  lowPriceTarget: 700.00,
  medianPriceTarget: 1025.00,
  impliedUpside: 20.0,
  ratings: [
    { source: "goldman_sachs", sourceName: "Goldman Sachs", rating: "strong_buy", ratingDisplay: "Strong Buy", priceTarget: 1100, confidence: "high", dateIssued: "2025-01-15" },
    { source: "jp_morgan", sourceName: "JP Morgan", rating: "buy", ratingDisplay: "Buy", priceTarget: 1050, confidence: "high", dateIssued: "2025-01-12" },
    { source: "morgan_stanley", sourceName: "Morgan Stanley", rating: "strong_buy", ratingDisplay: "Strong Buy", priceTarget: 1200, confidence: "high", dateIssued: "2025-01-18" },
    { source: "morningstar", sourceName: "Morningstar", rating: "hold", ratingDisplay: "Hold", priceTarget: 950, confidence: "high", dateIssued: "2025-01-10" },
    { source: "bank_of_america", sourceName: "Bank of America", rating: "buy", ratingDisplay: "Buy", priceTarget: 1000, confidence: "high", dateIssued: "2025-01-14" },
  ],
  morningstarStars: 4,
  morningstarFairValue: 950.00,
  morningstarMoat: "wide",
  peRatio: 62.5,
  forwardPE: 38.2,
  dividendYield: 0.02,
  beta: 1.65,
  marketCap: "2.2T",
  revenueGrowthYoY: 122.0,
  bullCase: "AI capex super-cycle: hyperscalers spending $150B+ annually on AI infrastructure. CUDA ecosystem lock-in creates switching costs that AMD/Intel can't easily overcome. Inference demand now matching training — doubles total addressable market. Software/services revenue growing 50%+ YoY, improving margin mix.",
  bearCase: "Trading at 62x earnings — prices in perfection with zero margin for error. China export restrictions already cut ~$5B in annual revenue; could worsen. Hyperscalers building custom chips (Google TPU, Amazon Trainium) reduce dependency. Semiconductor industry is inherently cyclical — this boom will moderate.",
  lastUpdated: "2026-02-26",
  disclaimer: "All ratings sourced from public analyst reports. Not investment advice.",
};

export const mockStockConsensusMessage = `Here's the full analyst consensus breakdown for NVIDIA — it's one of the most covered stocks on Wall Street right now:

\`\`\`json
${JSON.stringify({ type: "stock_consensus", stock: mockStockConsensus })}
\`\`\`

The consensus is overwhelmingly bullish (91 score) with 42 Buy ratings and zero Sells. The key debate is on valuation — Goldman and Morgan Stanley are aggressive with $1,100-$1,200 targets, while Morningstar thinks the stock is trading above fair value at $950. Notable disagreement worth watching. Want me to look at any of NVIDIA's competitors or the broader semiconductor sector?`;

/* ── 17. Sector Consensus ─────────────────────────────────────────── */

export const mockSectorConsensus: SectorConsensus = {
  sector: "technology",
  sectorName: "Technology",
  firmViews: [
    { source: "Goldman Sachs", sourceName: "Goldman Sachs", sectorRating: "overweight", keyReason: "AI infrastructure spending creates multi-year tailwind for semiconductors and cloud infrastructure. Capex cycle just beginning.", dateIssued: "2025-01-20" },
    { source: "JP Morgan", sourceName: "JP Morgan", sectorRating: "overweight", keyReason: "Enterprise software transitioning to AI-native products. Pricing power increasing across the stack.", dateIssued: "2025-01-18" },
    { source: "Morgan Stanley", sourceName: "Morgan Stanley", sectorRating: "overweight", keyReason: "Inference demand inflection doubles semiconductor TAM. Cloud re-acceleration visible in Q4 data.", dateIssued: "2025-01-22" },
    { source: "Morningstar", sourceName: "Morningstar", sectorRating: "equal_weight", keyReason: "Secular tailwinds are real but valuations have already priced in significant growth. Few bargains remain in quality names.", dateIssued: "2025-01-15" },
    { source: "Fidelity", sourceName: "Fidelity", sectorRating: "overweight", keyReason: "Productivity gains from AI adoption will disproportionately benefit tech companies with data advantages.", dateIssued: "2025-01-17" },
    { source: "UBS", sourceName: "UBS", sectorRating: "overweight", keyReason: "Cybersecurity spending acceleration and cloud migration tailwinds remain intact for 2025-2026.", dateIssued: "2025-01-19" },
  ],
  overweightCount: 5,
  equalWeightCount: 1,
  underweightCount: 0,
  consensusView: "overweight",
  topPicks: [
    mockConsensusLeaderboard.topRated[0], // NVDA
    mockConsensusLeaderboard.topRated[1], // META
  ],
  sectorMetrics: { peRatio: 32.5, ytdReturn: 8.2, dividendYield: 0.85, earningsGrowth: 18.5 },
  catalysts: [
    "Q1 mega-cap earnings season (April) — key test for AI revenue growth narratives",
    "NVIDIA GTC conference — next-gen Blackwell Ultra architecture details expected",
    "Fed rate cut timeline — lower rates benefit growth stock valuations",
    "Enterprise AI adoption inflection — several Fortune 500 companies increasing AI budgets 3-5x",
  ],
  risks: [
    "Antitrust regulation in US and EU targeting major tech platforms",
    "Rising interest rates compress growth multiples if Fed delays cuts",
    "China tech restrictions could escalate, impacting semiconductor supply chains",
    "AI spending ROI questions — if enterprises don't see returns, capex could pull back sharply",
  ],
};

export const mockSectorConsensusMessage = `Here's the analyst consensus view on the Technology sector — the overwhelming majority of major firms are overweight:

\`\`\`json
${JSON.stringify({ type: "sector_consensus", sector: mockSectorConsensus })}
\`\`\`

5 out of 6 major firms rate Technology as overweight, with AI infrastructure spending as the primary driver. Morningstar is the notable holdout — they agree the tailwinds are real but think valuations have gotten ahead of fundamentals. Key catalysts to watch: Q1 earnings season and NVIDIA's GTC conference. Want me to drill into a specific stock or compare this to another sector?`;

/* ── 18. Investment Theme ─────────────────────────────────────────── */

export const mockInvestmentTheme: InvestmentTheme = {
  id: "ai-infrastructure",
  themeName: "AI Infrastructure Buildout",
  description: "The rapid adoption of generative AI is driving unprecedented demand for GPUs, data center capacity, networking equipment, and power infrastructure. This theme captures companies building the physical and digital backbone of the AI revolution — from chip designers to cloud providers to energy suppliers cooling massive data centers.",
  supportingFirms: [
    { source: "Goldman Sachs", sourceName: "Goldman Sachs", thesis: "AI capex cycle to reach $200B+ annually by 2027. Infrastructure is the safest way to play the AI trade — picks and shovels always win in a gold rush.", datePublished: "2025-01-10" },
    { source: "Morgan Stanley", sourceName: "Morgan Stanley", thesis: "Inference demand inflection means the data center buildout is only at 30% of its eventual scale. Power constraints are the next bottleneck — creating opportunities in energy infrastructure.", datePublished: "2025-01-12" },
    { source: "ARK Invest", sourceName: "ARK Invest", thesis: "AI training costs falling 75% annually while capabilities double. This creates a virtuous cycle of adoption that requires exponentially more infrastructure.", datePublished: "2025-01-08" },
    { source: "JP Morgan", sourceName: "JP Morgan", thesis: "Enterprise AI adoption is moving from experimentation to production deployment. The infrastructure needed for production workloads is 10-100x what experimentation required.", datePublished: "2025-01-14" },
  ],
  relatedStocks: [
    { ticker: "NVDA", companyName: "NVIDIA Corporation", consensusScore: 91, connection: "Dominant GPU supplier for AI training and inference. CUDA ecosystem creates deep switching costs." },
    { ticker: "AVGO", companyName: "Broadcom Inc.", consensusScore: 82, connection: "Custom AI accelerator chips (XPUs) for hyperscalers + networking silicon for AI clusters." },
    { ticker: "ANET", companyName: "Arista Networks", consensusScore: 78, connection: "High-speed networking equipment connecting GPU clusters in AI data centers." },
    { ticker: "VRT", companyName: "Vertiv Holdings", consensusScore: 75, connection: "Thermal management and power distribution for AI data centers — cooling is the key bottleneck." },
    { ticker: "EQIX", companyName: "Equinix Inc.", consensusScore: 73, connection: "Largest global data center REIT — AI workloads driving capacity expansion worldwide." },
  ],
  timeHorizon: "long_term",
  riskLevel: "moderate",
};

export const mockInvestmentThemeMessage = `Here's a deep dive on one of the biggest investment themes right now — the AI Infrastructure buildout:

\`\`\`json
${JSON.stringify({ type: "investment_theme", theme: mockInvestmentTheme })}
\`\`\`

This is a "picks and shovels" play — instead of trying to guess which AI application wins, you invest in the infrastructure everyone needs. Goldman, Morgan Stanley, ARK, and JP Morgan all have high-conviction theses here. The risk level is moderate because while demand is undeniable, valuations on some of these names are stretched. Want me to explore another theme like clean energy or GLP-1 healthcare?`;

/* ── 20. Grocery Plan ─────────────────────────────────────────────── */

export const mockGroceryPlan: OptimizedGroceryPlan = {
  totalItems: 15,
  estimatedTotalAtUsualStore: 127.43,
  optimizedTotal: 89.67,
  totalSavings: 37.76,
  savingsPercentage: 29.6,
  storeTrips: [
    {
      store: "kroger",
      storeName: "Kroger",
      items: [
        { item: { name: "Chicken Breast", quantity: 3, unit: "lb", category: "meat_seafood", brandFlexible: true, estimatedPrice: 11.97, usualStore: "Publix" }, priceAtThisStore: 7.47, priceAtUsualStore: 11.97, savings: 4.50, onSale: true, couponAvailable: true, couponCode: "CHICKEN3", couponSavings: 1.50, substituteAvailable: false },
        { item: { name: "Whole Milk", quantity: 1, unit: "gallon", category: "dairy_eggs", brand: "Horizon Organic", brandFlexible: true, estimatedPrice: 6.49, usualStore: "Publix" }, priceAtThisStore: 4.99, priceAtUsualStore: 6.49, savings: 1.50, onSale: false, couponAvailable: false, substituteAvailable: true, substituteName: "Kroger Organic Milk", substitutePrice: 3.99, substituteSavings: 2.50 },
        { item: { name: "Cheddar Cheese", quantity: 1, unit: "lb", category: "dairy_eggs", brandFlexible: true, estimatedPrice: 6.99, usualStore: "Publix" }, priceAtThisStore: 4.99, priceAtUsualStore: 6.99, savings: 2.00, onSale: true, couponAvailable: false, substituteAvailable: false },
        { item: { name: "Bread (Whole Wheat)", quantity: 1, unit: "count", category: "bakery", brandFlexible: true, estimatedPrice: 4.29, usualStore: "Publix" }, priceAtThisStore: 2.99, priceAtUsualStore: 4.29, savings: 1.30, onSale: false, couponAvailable: false, substituteAvailable: true, substituteName: "Kroger Whole Wheat Bread", substitutePrice: 1.99, substituteSavings: 2.30 },
        { item: { name: "Pasta (Penne)", quantity: 2, unit: "count", category: "pantry_staples", brand: "Barilla", brandFlexible: true, estimatedPrice: 3.78, usualStore: "Publix" }, priceAtThisStore: 2.50, priceAtUsualStore: 3.78, savings: 1.28, onSale: false, couponAvailable: true, couponCode: "PASTA1OFF", couponSavings: 1.00, substituteAvailable: false },
        { item: { name: "Pasta Sauce", quantity: 2, unit: "count", category: "pantry_staples", brand: "Rao's", brandFlexible: false, estimatedPrice: 9.98, usualStore: "Publix" }, priceAtThisStore: 8.98, priceAtUsualStore: 9.98, savings: 1.00, onSale: false, couponAvailable: false, substituteAvailable: false },
        { item: { name: "Greek Yogurt", quantity: 4, unit: "count", category: "dairy_eggs", brand: "Chobani", brandFlexible: true, estimatedPrice: 5.96, usualStore: "Publix" }, priceAtThisStore: 4.76, priceAtUsualStore: 5.96, savings: 1.20, onSale: false, couponAvailable: false, substituteAvailable: true, substituteName: "Kroger Greek Yogurt", substitutePrice: 3.16, substituteSavings: 2.80 },
        { item: { name: "Olive Oil", quantity: 1, unit: "count", category: "pantry_staples", brandFlexible: true, estimatedPrice: 8.99, usualStore: "Publix" }, priceAtThisStore: 6.99, priceAtUsualStore: 8.99, savings: 2.00, onSale: false, couponAvailable: false, substituteAvailable: false },
      ],
      subtotal: 43.67,
      couponsApplied: 2,
      couponSavings: 2.50,
    },
    {
      store: "aldi",
      storeName: "Aldi",
      items: [
        { item: { name: "Bananas", quantity: 1, unit: "bunch", category: "produce", brandFlexible: true, estimatedPrice: 1.29, usualStore: "Publix" }, priceAtThisStore: 0.59, priceAtUsualStore: 1.29, savings: 0.70, onSale: false, couponAvailable: false, substituteAvailable: false },
        { item: { name: "Broccoli", quantity: 2, unit: "count", category: "produce", brandFlexible: true, estimatedPrice: 4.58, usualStore: "Publix" }, priceAtThisStore: 2.98, priceAtUsualStore: 4.58, savings: 1.60, onSale: false, couponAvailable: false, substituteAvailable: false },
        { item: { name: "Rice (Long Grain)", quantity: 1, unit: "lb", category: "pantry_staples", brandFlexible: true, estimatedPrice: 3.49, usualStore: "Publix" }, priceAtThisStore: 1.89, priceAtUsualStore: 3.49, savings: 1.60, onSale: false, couponAvailable: false, substituteAvailable: false },
        { item: { name: "Eggs (Large)", quantity: 1, unit: "dozen", category: "dairy_eggs", brandFlexible: true, estimatedPrice: 4.99, usualStore: "Publix" }, priceAtThisStore: 2.89, priceAtUsualStore: 4.99, savings: 2.10, onSale: false, couponAvailable: true, couponCode: "EGGS2OFF", couponSavings: 2.00, substituteAvailable: false },
        { item: { name: "Frozen Mixed Vegetables", quantity: 2, unit: "count", category: "frozen", brandFlexible: true, estimatedPrice: 5.98, usualStore: "Publix" }, priceAtThisStore: 3.38, priceAtUsualStore: 5.98, savings: 2.60, onSale: true, couponAvailable: false, substituteAvailable: false },
        { item: { name: "Butter (Unsalted)", quantity: 1, unit: "count", category: "dairy_eggs", brandFlexible: true, estimatedPrice: 5.49, usualStore: "Publix" }, priceAtThisStore: 3.49, priceAtUsualStore: 5.49, savings: 2.00, onSale: false, couponAvailable: false, substituteAvailable: false },
        { item: { name: "Orange Juice", quantity: 1, unit: "count", category: "beverages", brand: "Tropicana", brandFlexible: true, estimatedPrice: 4.99, usualStore: "Publix" }, priceAtThisStore: 2.99, priceAtUsualStore: 4.99, savings: 2.00, onSale: false, couponAvailable: false, substituteAvailable: true, substituteName: "Aldi Nature's Nectar OJ", substitutePrice: 1.99, substituteSavings: 3.00 },
      ],
      subtotal: 18.21,
      couponsApplied: 1,
      couponSavings: 2.00,
    },
  ],
  singleStoreBest: {
    store: "Kroger",
    total: 98.12,
    vsOptimized: 8.45,
    convenienceTax: 8.45,
  },
  couponsFound: [
    { item: "Chicken Breast", store: "Kroger", code: "CHICKEN3", savings: 1.50, expiresAt: "2026-03-15" },
    { item: "Pasta (Penne)", store: "Kroger", code: "PASTA1OFF", savings: 1.00, expiresAt: "2026-03-20" },
    { item: "Eggs (Large)", store: "Aldi", code: "EGGS2OFF", savings: 2.00, expiresAt: "2026-03-10" },
  ],
  substitutions: [
    { original: "Horizon Organic Milk", originalPrice: 4.99, substitute: "Kroger Organic Milk", substitutePrice: 3.99, savings: 1.00, note: "Same USDA Organic certification. Kroger brand is sourced from the same regional dairies." },
    { original: "Whole Wheat Bread", originalPrice: 2.99, substitute: "Kroger Whole Wheat Bread", substitutePrice: 1.99, savings: 1.00, note: "Store brand with identical ingredients list. Baked fresh daily in-store." },
    { original: "Chobani Greek Yogurt (4-pack)", originalPrice: 4.76, substitute: "Kroger Greek Yogurt (4-pack)", substitutePrice: 3.16, savings: 1.60, note: "Same protein content (15g). Blind taste tests show most people can't tell the difference." },
    { original: "Tropicana Orange Juice", originalPrice: 2.99, substitute: "Aldi Nature's Nectar OJ", substitutePrice: 1.99, savings: 1.00, note: "Not from concentrate, same 100% juice. $1 cheaper per carton." },
  ],
  tips: [
    "Kroger and Aldi are 2.3 miles apart on Peachtree Rd — hit both in one trip to save the full $37.76 without wasting gas.",
    "Chicken is on sale at Kroger this week. Buy 5 lbs instead of 3, portion and freeze the extra — you'll save $3/lb vs next week's regular price.",
    "Stack the CHICKEN3 manufacturer coupon with Kroger's digital coupon in the app for an extra $0.50 off (total coupon savings: $2.00 on chicken alone).",
  ],
};

export const mockGroceryPlanMessage = `I optimized your 15-item grocery list across Kroger and Aldi. Here's your plan:

\`\`\`json
${JSON.stringify({ type: "grocery_plan", plan: mockGroceryPlan })}
\`\`\`

You're currently spending $127.43 at Publix for these items. By splitting between Kroger (8 items) and Aldi (7 items), you'll pay $89.67 — that's **$37.76 saved (29.6%)**. I also found 3 coupons and 4 store brand swaps. The single-store option at Kroger is $98.12 if you'd rather skip the second stop. Want me to add anything to the list?`;

/* ── 21. Allocation Plan ──────────────────────────────────────────── */

export const mockAllocationPlan: AllocationPlan = {
  generatedAt: "2026-02-27T14:00:00Z",
  basedOn: "Your preferences: age 30, moderate risk tolerance, long-term horizon, $500/month budget",
  disclaimer: "This is an organizational tool to help structure your investment thinking. It is not financial advice. Discuss any changes with a licensed financial advisor before making investment decisions.",
  assetAllocation: {
    stocks: { percentage: 80, reason: "At age 30, a common approach is (110 - age) = 80% stocks. Your moderate risk tolerance and long timeline support this." },
    bonds: { percentage: 15, reason: "15% bonds provides stability without significantly dragging long-term growth. Cushions against stock volatility." },
    cash: { percentage: 5, reason: "5% cash reserve for rebalancing opportunities and peace of mind. Keep 3-6 months expenses separately in a HYSA." },
  },
  sectorAllocation: [
    {
      sector: "US Total Market",
      percentage: 50,
      reason: "Broad US market exposure captures large, mid, and small cap growth. The backbone of most portfolios.",
      exampleETFs: [
        { ticker: "VTI", name: "Vanguard Total Stock Market ETF", expenseRatio: 0.03 },
        { ticker: "ITOT", name: "iShares Core S&P Total US Stock Market ETF", expenseRatio: 0.03 },
      ],
      analystConsensus: "Goldman Sachs and Fidelity both recommend maintaining full US equity allocation for long-term investors.",
    },
    {
      sector: "International Developed",
      percentage: 20,
      reason: "Diversification across developed markets (Europe, Japan, Australia) reduces single-country risk.",
      exampleETFs: [
        { ticker: "VXUS", name: "Vanguard Total International Stock ETF", expenseRatio: 0.07 },
        { ticker: "IXUS", name: "iShares Core MSCI Total International Stock ETF", expenseRatio: 0.07 },
      ],
      analystConsensus: "Morningstar rates international developed equities as undervalued relative to US — potential for mean reversion.",
    },
    {
      sector: "Technology",
      percentage: 10,
      reason: "Modest tilt toward tech based on your expressed interest. Adds growth potential without over-concentrating.",
      exampleETFs: [
        { ticker: "VGT", name: "Vanguard Information Technology ETF", expenseRatio: 0.10 },
        { ticker: "QQQ", name: "Invesco QQQ Trust", expenseRatio: 0.20 },
      ],
      analystConsensus: "JP Morgan and Goldman Sachs rate technology overweight heading into 2026, driven by AI infrastructure spending.",
    },
  ],
  bondAllocation: [
    {
      type: "US Aggregate Bond",
      percentage: 70,
      reason: "Core bond holding — diversified mix of treasuries, corporates, and mortgage-backed securities.",
      exampleETFs: [
        { ticker: "BND", name: "Vanguard Total Bond Market ETF", expenseRatio: 0.03, yield: 4.2 },
        { ticker: "AGG", name: "iShares Core US Aggregate Bond ETF", expenseRatio: 0.03, yield: 4.1 },
      ],
    },
    {
      type: "Treasury Inflation-Protected",
      percentage: 30,
      reason: "TIPS protect purchasing power if inflation runs hotter than expected. Insurance policy for your bond allocation.",
      exampleETFs: [
        { ticker: "SCHP", name: "Schwab US TIPS ETF", expenseRatio: 0.04, yield: 2.3 },
      ],
    },
  ],
  monthlyPlan: [
    {
      account: "Roth IRA",
      monthlyAmount: 583,
      allocation: [
        { ticker: "VTI", name: "Vanguard Total Stock Market ETF", percentage: 60, dollarAmount: 349.80 },
        { ticker: "VXUS", name: "Vanguard Total International Stock ETF", percentage: 25, dollarAmount: 145.75 },
        { ticker: "BND", name: "Vanguard Total Bond Market ETF", percentage: 15, dollarAmount: 87.45 },
      ],
      taxBenefit: "Tax-free growth and tax-free withdrawals in retirement. Contributions made with after-tax dollars. Max $7,000/year ($583/month) in 2026.",
    },
  ],
  rebalancingFrequency: "semi_annual",
  rebalancingMethod: "Check allocations every 6 months. If any asset class drifts more than 5% from target, rebalance by directing new contributions to the underweight asset. Avoid selling to rebalance in taxable accounts (tax drag).",
  educationalNotes: [
    {
      topic: "Why Compound Interest Matters at 30",
      explanation: "At age 30, you have roughly 35 years until traditional retirement. $500/month invested at a 7% historical average return grows to approximately $853,000 by age 65. Starting just 5 years later would reduce that to about $580,000 — a $273,000 difference from 5 years of delay. Time is your single greatest asset.",
      source: "Historical S&P 500 average annual return (1926-2025), adjusted for inflation",
    },
    {
      topic: "Expense Ratios: The Silent Wealth Killer",
      explanation: "A 0.03% expense ratio (VTI) vs a 0.75% expense ratio (typical actively managed fund) doesn't sound like much. But on $500/month over 35 years, the difference is approximately $180,000 in fees eaten by the expensive fund. Always check the expense ratio — it's the one investment cost you can control.",
      source: "Morningstar fee impact calculator",
    },
    {
      topic: "Why Roth IRA First",
      explanation: "At your income level and age, a Roth IRA is typically the highest-impact account. You pay taxes now (at likely your lowest lifetime rate) and never pay taxes on the growth. If your $500/month grows to $853,000, you withdraw every penny tax-free. In a traditional IRA, you'd owe taxes on all of it at withdrawal.",
    },
  ],
  exportFormats: ["clipboard", "notes"],
};

export const mockAllocationPlanMessage = `Based on your profile (age 30, moderate risk, $500/month), here's a structured investment allocation framework:

\`\`\`json
${JSON.stringify({ type: "allocation_plan", plan: mockAllocationPlan })}
\`\`\`

This puts 80% in stocks, 15% in bonds, and 5% cash — a common starting point for someone your age with a long timeline. Your entire $500/month goes into a Roth IRA split across VTI (60%), VXUS (25%), and BND (15%) — all with expense ratios under 0.10%. Rebalance every 6 months by adjusting new contributions. Want me to adjust the allocation or add a 401k to the plan?`;


export const DEMO_MESSAGES: Record<string, { label: string; content: string }> = {
  coupons: { label: "🏷️ Coupons", content: mockCouponResults },
  savings: { label: "📊 Savings Report", content: mockSavingsReport },
  negotiate: { label: "📞 Negotiation Script", content: mockNegotiationScript },
  spend: { label: "💡 Spend to Save", content: mockSpendToSave },
  expense: { label: "📝 Expense Input", content: mockExpenseInput },
  market: { label: "📈 Market Report", content: mockMarketReportMessage },
  analyst: { label: "🏦 Analyst Insight", content: mockAnalystInsightMessage },
  prices: { label: "💲 Price Compare", content: mockPriceComparisonMessage },
  stores: { label: "🏪 Store Rankings", content: mockStoreRankingMessage },
  subs: { label: "📺 Sub Value", content: mockSubscriptionValueMessage },
  goal: { label: "🎯 Goal Simulator", content: mockGoalSimulationMessage },
  bills: { label: "📅 Bill Predictor", content: mockBillPredictionMessage },
  deals: { label: "📍 Local Deals", content: mockLocalDealsMessage },
  receipt: { label: "🧾 Receipt Analysis", content: mockReceiptAnalysisMessage },
  leaderboard: { label: "🏆 Consensus Board", content: mockConsensusLeaderboardMessage },
  stockview: { label: "📊 Stock Consensus", content: mockStockConsensusMessage },
  sectorview: { label: "🏭 Sector View", content: mockSectorConsensusMessage },
  theme: { label: "🎯 Invest Theme", content: mockInvestmentThemeMessage },
  grocery: { label: "🛒 Grocery Plan", content: mockGroceryPlanMessage },
  allocation: { label: "📐 Allocation Plan", content: mockAllocationPlanMessage },
};
