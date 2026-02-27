/* ── Skill detection — keyword-based trigger matching ────────────────── */

export type DetectedSkill = "coupon" | "optimizer" | "market_intel" | "price_intel" | "subscription_value" | null;

const COUPON_TRIGGERS = [
  "coupon",
  "promo code",
  "promo",
  "discount code",
  "deal",
  "deals",
  "save money at",
  "any codes",
  "code for",
  "discount",
  "sale",
  "coupons for",
  "deals for",
  "deals on",
  "cheaper",
];

const OPTIMIZER_TRIGGERS = [
  "cut expenses",
  "save money",
  "wasting money",
  "subscriptions",
  "cancel subscription",
  "too expensive",
  "spending too much",
  "budget help",
  "bills too high",
  "reduce spending",
  "monthly expenses",
  "spending optimizer",
  "spend helper",
  "cut costs",
  "lower my bills",
  "help me save",
  "analyze my spending",
  "where am i wasting",
];

const MARKET_INTEL_TRIGGERS = [
  "sector",
  "sectors",
  "market outlook",
  "analyst",
  "analysts",
  "what sectors",
  "bull case",
  "bear case",
  "stock outlook",
  "market sentiment",
  "what do analysts think",
  "research report",
  "sector rotation",
  "overweight",
  "underweight",
  "upgrade",
  "downgrade",
  "price target",
  "morningstar rating",
  "market intelligence",
  "where should i invest",
  "what should i invest",
  "investment opportunities",
  "market trends",
  "whats the market doing",
  "market report",
  "growth sectors",
  "best sectors",
  "sector performance",
  "wall street",
  "goldman",
  "jp morgan",
  "fidelity says",
];

const PRICE_INTEL_TRIGGERS = [
  "price comparison",
  "compare prices",
  "cheaper",
  "best price",
  "where to buy",
  "where should i buy",
  "best deal on",
  "overpaying",
  "paid too much",
  "is this a good price",
  "price check",
  "store rankings",
  "cheapest store",
  "best store for",
  "where to shop",
  "better price",
  "price match",
  "bought this at",
  "paid for this",
  "how much should",
  "grocery prices",
  "cheapest groceries",
];

const SUBSCRIPTION_VALUE_TRIGGERS = [
  "subscription value",
  "worth the money",
  "am i using",
  "cost per hour",
  "getting my money",
  "value for money",
  "worth keeping",
  "should i keep paying",
  "how much value",
  "rate my subscriptions",
  "score my subscriptions",
];

/**
 * Detect which skill (if any) should be activated based on the user's message.
 * Simple keyword matching — will be replaced with a proper intent classifier later.
 */
export function detectSkill(message: string): DetectedSkill {
  const lower = message.toLowerCase();
  if (COUPON_TRIGGERS.some((t) => lower.includes(t))) return "coupon";
  if (SUBSCRIPTION_VALUE_TRIGGERS.some((t) => lower.includes(t))) return "subscription_value";
  if (PRICE_INTEL_TRIGGERS.some((t) => lower.includes(t))) return "price_intel";
  if (OPTIMIZER_TRIGGERS.some((t) => lower.includes(t))) return "optimizer";
  if (MARKET_INTEL_TRIGGERS.some((t) => lower.includes(t))) return "market_intel";
  return null;
}
