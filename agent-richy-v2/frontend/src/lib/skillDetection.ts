/* ── Skill detection — keyword-based trigger matching ────────────────── */

export type DetectedSkill = "coupon" | "optimizer" | null;

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

/**
 * Detect which skill (if any) should be activated based on the user's message.
 * Simple keyword matching — will be replaced with a proper intent classifier later.
 */
export function detectSkill(message: string): DetectedSkill {
  const lower = message.toLowerCase();
  if (COUPON_TRIGGERS.some((t) => lower.includes(t))) return "coupon";
  if (OPTIMIZER_TRIGGERS.some((t) => lower.includes(t))) return "optimizer";
  return null;
}
