/* ── Advisor Marketplace — Two-Sided Financial Advisor Matching ───────── */

// ==========================================
// ADVISOR PROFILES
// ==========================================

export interface AdvisorProfile {
  id: string;

  // Identity
  name: string;
  title: string; // "CFP", "CFA", "Financial Advisor"
  firm: string;
  photo?: string;

  // Credentials
  certifications: (
    | "CFP"
    | "CFA"
    | "CPA"
    | "ChFC"
    | "CLU"
    | "RICP"
    | "Series_65"
    | "Series_66"
  )[];
  yearsExperience: number;
  registeredWith: ("SEC" | "FINRA" | "State")[];
  adv2Link?: string; // Link to their ADV Part 2 (public disclosure)
  brokecheckLink?: string; // FINRA BrokerCheck link

  // Specializations
  specialties: AdvisorSpecialty[];
  clientTypes: (
    | "young_professional"
    | "family"
    | "pre_retirement"
    | "retiree"
    | "high_net_worth"
    | "business_owner"
    | "debt_focused"
    | "first_generation_wealth"
  )[];
  minimumAssets?: number; // Minimum AUM to work with them (0 = no minimum)

  // Service model
  feeStructure:
    | "fee_only"
    | "fee_based"
    | "commission"
    | "flat_fee"
    | "hourly";
  feeDetails: string; // "1% of AUM" or "$200/hour" or "$1,500 flat fee for financial plan"
  meetingFormat: ("in_person" | "video" | "phone")[];
  location?: { city: string; state: string };
  servicesNationwide: boolean;

  // Profile
  bio: string;
  philosophy: string; // Their investment/planning philosophy
  typicalClient: string; // "I typically work with young families building their first..."

  // Ratings (from Richy users)
  rating: number; // 1-5 stars
  reviewCount: number;
  responseTime: string; // "Usually responds within 24 hours"

  // Matching
  matchScore?: number; // Calculated based on user's Financial DNA
  matchReasons?: string[]; // Why this advisor is a good fit

  // Status
  acceptingNewClients: boolean;
  verified: boolean; // Richy team verified credentials
  premiumListing: boolean; // Paid for enhanced visibility
}

export type AdvisorSpecialty =
  | "retirement_planning"
  | "investment_management"
  | "tax_planning"
  | "estate_planning"
  | "debt_management"
  | "budgeting"
  | "college_planning"
  | "insurance"
  | "small_business"
  | "divorce_financial_planning"
  | "sudden_wealth"
  | "socially_responsible_investing"
  | "crypto_digital_assets"
  | "real_estate"
  | "stock_options_equity_comp";

// ==========================================
// MATCHING ENGINE
// ==========================================

export interface AdvisorMatch {
  advisor: AdvisorProfile;
  matchScore: number; // 1-100
  matchReasons: string[];

  // What Richy prepared for the advisor
  clientBrief: {
    // Anonymized summary of user's financial situation
    // Advisor sees this BEFORE the first meeting
    ageRange: string;
    financialGoals: string[];
    primaryConcerns: string[];
    estimatedNetWorth: string; // Range, not exact: "$50K-100K"
    estimatedIncome: string; // Range
    debtSituation: string; // "Moderate student loan debt"
    investmentExperience: string;
    whatTheyNeedHelpWith: string[];
    richyRecommendation: string; // "This client would benefit from a comprehensive financial plan with focus on debt payoff strategy and retirement catch-up"
  };

  // What the user sees
  whyThisAdvisor: string; // "Specializes in young professionals with student debt. Fee-only, no conflicts of interest. 4.8 stars from 23 Richy users."
  estimatedCost: string; // "~$200/hour or $1,500 for a full financial plan"
  nextStep: string; // "Schedule a free 15-minute intro call"
}

// ==========================================
// MARKETPLACE METRICS
// ==========================================

export interface MarketplaceMetrics {
  totalAdvisors: number;
  activeAdvisors: number; // Responded to a match in last 30 days
  totalMatches: number;
  totalMeetingsScheduled: number;
  avgMatchScore: number;
  avgAdvisorRating: number;

  // Revenue
  advisorSubscriptionRevenue: number; // Monthly from advisor listings
  referralFeeRevenue: number; // Per-match or per-meeting fees
  premiumListingRevenue: number;

  // By specialty
  demandBySpecialty: {
    specialty: string;
    searchCount: number;
    advisorCount: number;
    gap: number;
  }[];

  // Geography
  topMarkets: {
    city: string;
    advisorCount: number;
    userDemand: number;
  }[];
}

// ==========================================
// ADVISOR REVENUE MODEL
// ==========================================

export const ADVISOR_PRICING = {
  // No monthly subscription. No barriers to entry.
  // Maximum ecosystem growth. Every advisor can join for free.
  // They only pay when they get a qualified lead.

  // Core model: $50 per qualified lead
  referralFee: 50,

  // What the $50 gets them:
  // 1. Pre-built client brief from Financial DNA (income, debts, goals, concerns)
  // 2. Client has explicitly requested advisor matching
  // 3. Client's contact info for scheduling
  // 4. Richy's analysis of what the client needs help with
  // 5. The client's spending profile, risk tolerance, and financial literacy level
  //
  // This is 5-10x cheaper than SmartAsset ($200-300/lead),
  // WiserAdvisor ($150-250/lead), or Zoe Financial ($100+/lead).
  // AND the leads are higher quality because Financial DNA pre-qualifies them.

  // Free for all advisors:
  freeFeatures: [
    "Create and maintain a full profile",
    "Be visible in the marketplace and search results",
    "Receive match notifications",
    "View anonymized client brief previews (age range, goals, needs)",
    "Basic analytics on profile views",
  ],

  // What triggers a $50 charge:
  // Advisor clicks "Accept Match" → sees full client brief + contact info → $50 charged
  // If the client doesn't respond within 14 days, advisor gets a credit back

  // Optional premium visibility (for advisors who want more leads)
  premiumBadge: {
    name: "Featured Advisor",
    monthlyPrice: 49,
    features: [
      "Featured placement at top of match results",
      "Richy proactively mentions you by name in relevant conversations",
      "Enhanced profile with video intro and case studies",
      "Priority matching when multiple advisors fit",
      "Monthly market insights report for your client demographic",
    ],
  },

  // Revenue projections:
  // 100 matches/month × $50 = $5,000/month
  // 500 matches/month × $50 = $25,000/month
  // 1,000 matches/month × $50 = $50,000/month
  // Plus premium badge revenue: 10% of advisors × $49/month
  // This scales independently from user subscriptions
};
