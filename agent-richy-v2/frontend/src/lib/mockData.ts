/* ── Mock data for testing structured chat components ─────────────────
 *  Import and inject these into the chat to verify rendering
 *  without needing real AI responses.
 * ──────────────────────────────────────────────────────────────────── */

import type { Coupon } from "@/types/coupon";
import type { SavingsReport } from "@/types/spending";

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

/* ── All demo messages keyed for the debug panel ──────────────────── */

export const DEMO_MESSAGES: Record<string, { label: string; content: string }> = {
  coupons: { label: "🏷️ Coupons", content: mockCouponResults },
  savings: { label: "📊 Savings Report", content: mockSavingsReport },
  negotiate: { label: "📞 Negotiation Script", content: mockNegotiationScript },
  spend: { label: "💡 Spend to Save", content: mockSpendToSave },
  expense: { label: "📝 Expense Input", content: mockExpenseInput },
};
