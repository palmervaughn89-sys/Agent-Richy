/* ── Wealth Race — Gamified Financial Progress Tracking ──────────────── */

// ==========================================
// WEALTH RACE PROFILE
// ==========================================

export interface WealthRaceProfile {
  anonymousId: string; // Never linked to real identity in client

  // Anonymized metrics for comparison
  ageGroup: "18-24" | "25-34" | "35-44" | "45-54" | "55-64" | "65+";
  region: string; // State level only
  householdType: "single" | "couple" | "family";

  // Scores (all 1-100, calculated from Financial DNA)
  overallScore: number;
  savingsScore: number;
  debtScore: number;
  investingScore: number;
  spendingScore: number;
  knowledgeScore: number;

  // Progress metrics
  savingsRate: number; // Percentage
  debtPaydownRate: number; // Monthly debt reduction
  netWorthGrowthRate: number; // Monthly net worth change

  // Streaks and achievements
  streaks: {
    currentEngagementStreak: number; // Days in a row using Richy
    longestStreak: number;
    currentSavingsStreak: number; // Months in a row hitting savings target
  };

  achievements: {
    id: string;
    name: string;
    description: string;
    earnedAt: string;
    icon: string;
    rarity: "common" | "uncommon" | "rare" | "epic" | "legendary";
  }[];
}

// ==========================================
// WEALTH RACE LEADERBOARD
// ==========================================

export interface WealthRaceLeaderboard {
  category: string; // "Overall", "Savings Rate", "Debt Paydown", etc.
  ageGroup: string;
  region?: string;

  userRank: number;
  userPercentile: number; // "Better than X% of peers"
  totalParticipants: number;

  // Anonymized top performers (no identifying info)
  topPerformers: {
    rank: number;
    anonymousLabel: string; // "Saver #4,291" — not a real name
    score: number;
    isCurrentUser: boolean;
  }[];

  // Distribution
  distribution: {
    scoreRange: string; // "90-100", "80-89", etc.
    count: number;
    percentage: number;
    userInThisRange: boolean;
  }[];

  // Motivational context
  toNextPercentile: {
    currentPercentile: number;
    nextPercentile: number;
    whatItTakes: string; // "Save $47 more per month to reach top 20%"
  };
}

// ==========================================
// ACHIEVEMENTS CATALOG
// ==========================================

export const ACHIEVEMENTS = [
  // Getting Started
  { id: "first_chat", name: "First Steps", description: "Had your first conversation with Richy", rarity: "common" as const, icon: "👋" },
  { id: "full_profile", name: "Open Book", description: "Completed the full spending intake", rarity: "uncommon" as const, icon: "📖" },
  { id: "first_save", name: "First Blood", description: "Identified your first savings opportunity", rarity: "common" as const, icon: "💰" },

  // Savings milestones
  { id: "save_100", name: "Triple Digits", description: "Saved $100 through Richy's recommendations", rarity: "common" as const, icon: "💵" },
  { id: "save_500", name: "Half Grand", description: "Saved $500 through optimizations", rarity: "uncommon" as const, icon: "🏆" },
  { id: "save_1000", name: "Four Comma Club", description: "Saved $1,000 through Richy", rarity: "rare" as const, icon: "🎯" },
  { id: "save_5000", name: "Serious Saver", description: "Saved $5,000 lifetime through Richy", rarity: "epic" as const, icon: "⭐" },
  { id: "save_10000", name: "Financial Freedom Fighter", description: "Saved $10,000 lifetime", rarity: "legendary" as const, icon: "👑" },

  // Streaks
  { id: "streak_7", name: "Week Warrior", description: "7-day engagement streak", rarity: "common" as const, icon: "🔥" },
  { id: "streak_30", name: "Monthly Master", description: "30-day engagement streak", rarity: "uncommon" as const, icon: "🔥" },
  { id: "streak_90", name: "Quarterly Queen", description: "90-day engagement streak", rarity: "rare" as const, icon: "🔥" },
  { id: "streak_365", name: "Year of Growth", description: "365-day engagement streak", rarity: "legendary" as const, icon: "🔥" },

  // Actions
  { id: "first_negotiation", name: "Negotiator", description: "Used a Richy negotiation script", rarity: "uncommon" as const, icon: "📞" },
  { id: "first_coupon", name: "Deal Hunter", description: "Used a Richy coupon", rarity: "common" as const, icon: "🏷️" },
  { id: "subscription_audit", name: "Subscription Slayer", description: "Cancelled an unused subscription", rarity: "common" as const, icon: "✂️" },
  { id: "emergency_fund", name: "Safety Net", description: "Built a 3-month emergency fund", rarity: "rare" as const, icon: "🛡️" },
  { id: "debt_free", name: "Unchained", description: "Paid off all consumer debt", rarity: "epic" as const, icon: "⛓️" },
  { id: "max_401k", name: "Maxed Out", description: "Maxing out 401k contributions", rarity: "rare" as const, icon: "📈" },

  // Knowledge
  { id: "learn_10", name: "Student", description: "Asked Richy to explain 10 financial concepts", rarity: "common" as const, icon: "📚" },
  { id: "learn_50", name: "Scholar", description: "Explored 50 financial topics", rarity: "uncommon" as const, icon: "🎓" },
  { id: "lifestyle_portfolio", name: "Market Mirror", description: "Generated your Lifestyle Portfolio", rarity: "uncommon" as const, icon: "📊" },
  { id: "financial_twin", name: "Future Sight", description: "Ran your first Financial Twin simulation", rarity: "uncommon" as const, icon: "🔮" },

  // Social
  { id: "top_10_percent", name: "Top 10%", description: "Reached the top 10% of savers in your age group", rarity: "rare" as const, icon: "🏅" },
  { id: "top_1_percent", name: "The One Percent", description: "Reached the top 1% of financial health in your age group", rarity: "legendary" as const, icon: "💎" },
];
