/* ── Mock data for testing structured chat components ─────────────────
 *  Import and inject these into the chat to verify rendering
 *  without needing real AI responses.
 * ──────────────────────────────────────────────────────────────────── */

import type { Coupon } from "@/types/coupon";
import type { SavingsReport } from "@/types/spending";
import type { PriceComparison, StoreCategoryRanking, SubscriptionValue } from "@/types/pricing";

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
};
