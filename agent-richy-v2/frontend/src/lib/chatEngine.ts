/* ── Chat engine — agent routing, offline fallback, emotion detection ── */

import fs from 'fs';
import path from 'path';
import type { StructuredResponse } from '@/lib/types';

// ── Agent definitions ───────────────────────────────────────────────────

interface AgentDef {
  name: string;
  icon: string;
  specialty: string;
  systemPrompt: string;
  keywords: string[];
  defaultEmotion: string;
}

const AGENT_DEFS: Record<string, AgentDef> = {
  coach_richy: {
    name: 'Coach Richy',
    icon: '💰',
    specialty: 'General Financial Coaching',
    keywords: ['help', 'start', 'advice', 'money', 'finance', 'plan'],
    defaultEmotion: 'friendly',
    systemPrompt: `You are Coach Richy — a warm, encouraging AI financial coach. You help people of ALL ages build better money habits. You explain things simply, use emojis for energy, and always motivate. Keep answers under 300 words. Use markdown for structure. If someone shares financial details, acknowledge them and give actionable advice. Always end with a question or next step.`,
  },
  budget_bot: {
    name: 'Budget Bot',
    icon: '📊',
    specialty: 'Budgeting & Expense Tracking',
    keywords: ['budget', 'spend', 'expense', 'track', 'save money', '50/30/20', 'paycheck'],
    defaultEmotion: 'thinking',
    systemPrompt: `You are Budget Bot — a sharp, detail-oriented budgeting specialist. You love the 50/30/20 rule, zero-based budgets, and helping people find hidden money. Always ask about income and expenses if not provided. Give specific dollar amounts. Use markdown tables when comparing options. Keep under 300 words.`,
  },
  invest_intel: {
    name: 'Invest Intel',
    icon: '📈',
    specialty: 'Investing & Wealth Building',
    keywords: ['invest', 'stock', 'etf', 'index', 'portfolio', 'compound', 'retire', 'roth', '401k'],
    defaultEmotion: 'presenting',
    systemPrompt: `You are Invest Intel — a patient investing mentor who makes complex topics simple. You advocate for index funds, dollar-cost averaging, and long-term thinking. Explain risk vs return. Use examples with real numbers. Always include a disclaimer that this isn't financial advice. Keep under 300 words.`,
  },
  debt_destroyer: {
    name: 'Debt Destroyer',
    icon: '💪',
    specialty: 'Debt Elimination Strategies',
    keywords: ['debt', 'owe', 'loan', 'credit card', 'payoff', 'interest', 'snowball', 'avalanche'],
    defaultEmotion: 'empathetic',
    systemPrompt: `You are Debt Destroyer — a tough-love but compassionate debt elimination coach. You know snowball and avalanche methods inside out. You celebrate small wins and never shame. Give specific strategies with numbers. Keep under 300 words.`,
  },
  savings_sage: {
    name: 'Savings Sage',
    icon: '🏦',
    specialty: 'Savings & Emergency Funds',
    keywords: ['save', 'emergency', 'fund', 'goal', 'rainy day', 'savings account'],
    defaultEmotion: 'teaching',
    systemPrompt: `You are Savings Sage — a wise and encouraging savings specialist. You help people build emergency funds, set savings goals, and find creative ways to save more. You love automation and high-yield savings accounts. Keep under 300 words.`,
  },
  kid_coach: {
    name: 'Kid Coach',
    icon: '🎮',
    specialty: 'Kids & Teen Financial Education',
    keywords: ['kid', 'child', 'teen', 'allowance', 'young', 'teach', 'learn', 'game'],
    defaultEmotion: 'excited',
    systemPrompt: `You are Kid Coach — a fun, energetic financial educator for kids and teens! You use simple language, fun analogies, and lots of emojis. You teach about earning, saving, spending wisely, and basic investing concepts through stories and examples kids can relate to. Keep under 250 words.`,
  },
};

// ── Cached offline responses ────────────────────────────────────────────

interface CachedResponse {
  keywords: string[];
  agentKey: string;
  message: string;
  emotion: string;
}

const CACHED_RESPONSES: CachedResponse[] = [
  {
    keywords: ['compound interest', 'compound'],
    agentKey: 'invest_intel',
    emotion: 'excited',
    message: `## 📈 The Magic of Compound Interest!\n\nCompound interest is when your money earns interest on **both** your original amount AND the interest you've already earned. It's like a snowball rolling downhill!\n\n**Example:** If you invest $1,000 at 8% annual return:\n- Year 1: $1,080\n- Year 10: $2,159\n- Year 30: **$10,063** 🤯\n\nThat's 10x your money without adding a single dollar! Now imagine adding $200/month...\n\n💡 **Try the Compound Interest Calculator** in the Calculators tab to see your own numbers!\n\nWant me to help you figure out how much to invest monthly to reach a specific goal? 🎯`,
  },
  {
    keywords: ['50/30/20', 'budget rule', 'how to budget'],
    agentKey: 'budget_bot',
    emotion: 'teaching',
    message: `## 💰 The 50/30/20 Budget Rule\n\nThis is my favorite framework for beginners! Here's how it works:\n\n| Category | % of Income | Examples |\n|----------|------------|----------|\n| **Needs** | 50% | Rent, groceries, insurance, utilities |\n| **Wants** | 30% | Dining out, streaming, shopping |\n| **Savings** | 20% | Emergency fund, investments, debt payoff |\n\n**Example on $5,000/month:**\n- Needs: $2,500\n- Wants: $1,500\n- Savings: $1,000\n\nThe key is to pay yourself first — move that 20% to savings the moment your paycheck hits! 🏦\n\n💡 **Try the Budget Calculator** to see your personalized breakdown!\n\nWant to tell me your monthly income so I can create a custom plan? 📊`,
  },
  {
    keywords: ['emergency fund', 'rainy day', 'emergenc'],
    agentKey: 'savings_sage',
    emotion: 'teaching',
    message: `## 🛟 Emergency Fund Guide\n\nAn emergency fund is your financial safety net — money set aside for unexpected expenses like car repairs, medical bills, or job loss.\n\n**How much do you need?**\n- 🟡 Minimum: **3 months** of expenses\n- 🟢 Ideal: **6 months** of expenses\n- 🔵 Great: **9-12 months** (if self-employed)\n\n**Where to keep it:**\n- High-yield savings account (4-5% APY right now!)\n- NOT invested in stocks (too volatile)\n- Separate from your checking (reduces temptation)\n\n**How to build it:**\n1. Start with a $1,000 mini goal\n2. Automate transfers ($50-200/paycheck)\n3. Use windfalls (tax refunds, bonuses)\n\n💡 **Try the Emergency Fund Calculator** to see where you stand!\n\nWhat are your monthly expenses? I can calculate your target! 🎯`,
  },
  {
    keywords: ['debt', 'payoff', 'snowball', 'avalanche'],
    agentKey: 'debt_destroyer',
    emotion: 'empathetic',
    message: `## 💪 Debt Payoff Strategies\n\nTwo proven methods to crush debt:\n\n### 🏔️ Avalanche Method (saves the most money)\nPay minimums on all debts, then throw extra at the **highest interest rate** first.\n- ✅ Mathematically optimal\n- ❌ Can feel slow if the biggest rate is also the biggest balance\n\n### ⛄ Snowball Method (builds momentum)\nPay minimums on all debts, then throw extra at the **smallest balance** first.\n- ✅ Quick wins keep you motivated\n- ❌ May pay slightly more interest overall\n\n**My recommendation:** If you need motivation, start with snowball. If you're disciplined, avalanche saves more.\n\n💡 **Try the Debt Payoff Calculator** to see your timeline!\n\nWant to tell me about your debts? I'll build a custom payoff plan! 📋`,
  },
  {
    keywords: ['invest', 'stock', 'begin', 'start investing', 'how to invest'],
    agentKey: 'invest_intel',
    emotion: 'presenting',
    message: `## 📈 Getting Started with Investing\n\nInvesting doesn't have to be complicated! Here's a beginner-friendly roadmap:\n\n**Step 1: Foundation** ✅\n- Emergency fund of 3-6 months ✓\n- High-interest debt paid off ✓\n\n**Step 2: Start Simple**\n- Open a Roth IRA (tax-free growth!)\n- Buy a total market index fund (like VTI or VTSAP)\n- Set up automatic monthly contributions\n\n**Step 3: The Numbers**\n- S&P 500 average return: ~10%/year\n- $200/month for 30 years at 10% = **$452,098** 🤯\n- Start early — time is your superpower!\n\n**What NOT to do:**\n- ❌ Pick individual stocks as a beginner\n- ❌ Try to time the market\n- ❌ Invest money you need within 5 years\n\n*Note: This is educational info, not financial advice.*\n\nWhat's your current savings situation? Let's find the right starting point! 🎯`,
  },
  {
    keywords: ['credit score', 'credit', 'fico'],
    agentKey: 'coach_richy',
    emotion: 'teaching',
    message: `## 📊 Understanding Your Credit Score\n\nYour credit score (300-850) affects loan rates, apartments, and even job applications!\n\n**Score Ranges:**\n- 🔴 300-579: Poor\n- 🟠 580-669: Fair\n- 🟡 670-739: Good\n- 🟢 740-799: Very Good\n- 🔵 800-850: Excellent\n\n**The 5 Factors:**\n1. **Payment History** (35%) — Pay on time, every time\n2. **Credit Utilization** (30%) — Keep under 30% of limits\n3. **Length of History** (15%) — Don't close old cards\n4. **Credit Mix** (10%) — Mix of card + loans helps\n5. **New Inquiries** (10%) — Don't apply for too many at once\n\n**Quick Wins:**\n- Set up autopay for minimums\n- Request credit limit increases\n- Become an authorized user on a parent's card\n\nWant me to help you build a credit improvement plan? 🎯`,
  },
  {
    keywords: ['hello', 'hi', 'hey', 'sup', 'start'],
    agentKey: 'coach_richy',
    emotion: 'friendly',
    message: `## 👋 Hey there! I'm Richy!\n\nWelcome — I'm your all-in-one AI financial coach! 🎉\n\nHere's what I can help you with:\n\n- 🏷️ **Find Coupons & Deals** — Real-time codes for any store\n- 📊 **Budget & Cash Flow** — Build a plan that fits your life\n- 🔄 **Subscription Audit** — Kill zombie charges\n- 📞 **Bill Negotiation** — Scripts to lower your bills\n- 📈 **Investing & Wealth** — Grow your money smarter\n- 💪 **Debt Payoff Plans** — Snowball, avalanche, or custom\n- 🧾 **Tax Strategy** — Deductions, brackets, and planning\n- ⭐ **Kids Zone** — Fun financial education for young earners\n\nJust tell me what's on your mind — no forms, no menus. I'll take it from there. 🎯`,
  },
];

// ── Emotion detection ───────────────────────────────────────────────────

const EMOTION_KEYWORDS: Record<string, string[]> = {
  celebrating: ['congrat', 'amazing', 'awesome', 'great job', 'well done', 'paid off'],
  serious: ['tax', 'irs', 'legal', 'bankrupt', 'foreclos'],
  empathetic: ['struggle', 'can\'t afford', 'behind on', 'overwhelm', 'stress', 'worried'],
  excited: ['compound', 'growth', 'retire', 'million', 'invest', 'save'],
  presenting: ['here\'s', 'let me show', 'breakdown', 'compare', 'analysis'],
  teaching: ['explain', 'what is', 'how does', 'learn', 'understand', 'guide'],
};

export function determineEmotion(text: string, agentKey: string): string {
  const lower = text.toLowerCase();
  for (const [emotion, keywords] of Object.entries(EMOTION_KEYWORDS)) {
    if (keywords.some((kw) => lower.includes(kw))) return emotion;
  }
  return AGENT_DEFS[agentKey]?.defaultEmotion ?? 'friendly';
}

// ── Agent routing ───────────────────────────────────────────────────────

export function routeToAgent(message: string, currentAgent?: string): string {
  const lower = message.toLowerCase();
  let bestAgent = currentAgent || 'coach_richy';
  let bestScore = 0;

  for (const [key, def] of Object.entries(AGENT_DEFS)) {
    let score = 0;
    for (const kw of def.keywords) {
      if (lower.includes(kw)) score += 1;
    }
    if (score > bestScore) {
      bestScore = score;
      bestAgent = key;
    }
  }

  return bestAgent;
}

// ── Offline response ────────────────────────────────────────────────────

export function findCachedResponse(message: string): CachedResponse | null {
  const lower = message.toLowerCase();
  for (const cached of CACHED_RESPONSES) {
    if (cached.keywords.some((kw) => lower.includes(kw))) {
      return cached;
    }
  }
  return null;
}

export function buildFallbackResponse(message: string, agentKey: string): string {
  const agent = AGENT_DEFS[agentKey];
  return `## ${agent?.icon ?? '💰'} ${agent?.name ?? 'Coach Richy'}\n\nThanks for your question! While I'm running in offline mode right now, here are some things I can help with:\n\n- 📊 **Budget Planning** — Try asking about the 50/30/20 rule\n- 📈 **Investing Basics** — Ask about compound interest or how to start investing\n- 💪 **Debt Strategy** — Ask about snowball vs avalanche methods\n- 🛟 **Emergency Fund** — Ask how much you need\n- 🧮 **Calculators** — Check out the Calculators tab for exact numbers!\n\nTry asking me about one of these topics, or head to your **Profile** to set up your financial details so I can give personalized advice! 🎯`;
}

// ── Build StructuredResponse ────────────────────────────────────────────

export function buildStructuredResponse(
  message: string,
  agentKey: string,
  emotion?: string,
): StructuredResponse {
  return {
    message,
    agent: agentKey,
    charts: [],
    examples: [],
    evidence: [],
    avatar_emotion: emotion || determineEmotion(message, agentKey),
    suggested_agent: undefined,
    calculator_result: undefined,
  };
}

// ── Get system prompt for an agent ──────────────────────────────────────

/** Cache loaded prompt files so we only read from disk once per cold start. */
const promptCache = new Map<string, string>();

function loadPromptFile(filename: string): string | null {
  if (promptCache.has(filename)) return promptCache.get(filename)!;
  try {
    const filePath = path.join(process.cwd(), 'src', 'prompts', filename);
    const content = fs.readFileSync(filePath, 'utf-8');
    promptCache.set(filename, content);
    return content;
  } catch {
    return null;
  }
}

const SKILL_PROMPT_FILES: Record<string, string> = {
  coupon: 'coupon-finder.md',
  optimizer: 'spending-optimizer.md',
  market_intel: 'market-intelligence.md',
  price_intel: 'price-intelligence.md',
  subscription_value: 'price-intelligence.md',
  goal_sim: 'goal-simulator.md',
  bill_predict: 'bill-predictor.md',
  local_deals: 'local-deals.md',
  receipt_analyze: 'receipt-analyzer.md',
  investment_intel: 'investment-intelligence.md',
  grocery_plan: 'grocery-planner.md',
  allocation_map: 'allocation-mapper.md',
  proactive: 'proactive-alerts.md',
  trajectory: 'wealth-trajectory.md',
  financial_twin: 'financial-twin.md',
  wealth_race: 'wealth-race.md',
  advisor_match: 'advisor-match.md',
};

/**
 * Build the full system prompt.
 * Base = richy-unified.md (falls back to inline AGENT_DEFS prompt).
 * If a skill is active, append the skill-specific prompt.
 */
export function getAgentSystemPrompt(
  agentKey: string,
  skill?: 'coupon' | 'optimizer' | 'market_intel' | 'price_intel' | 'subscription_value' | 'goal_sim' | 'bill_predict' | 'local_deals' | 'receipt_analyze' | 'investment_intel' | 'grocery_plan' | 'allocation_map' | 'proactive' | 'trajectory' | 'financial_twin' | 'wealth_race' | 'advisor_match' | null,
): string {
  // Load unified base prompt
  const unified = loadPromptFile('richy-unified.md');
  const base = unified ?? AGENT_DEFS[agentKey]?.systemPrompt ?? AGENT_DEFS.coach_richy.systemPrompt;

  if (!skill) return base;

  const skillFile = SKILL_PROMPT_FILES[skill];
  if (!skillFile) return base;

  const skillPrompt = loadPromptFile(skillFile);
  if (!skillPrompt) return base;

  return `${base}\n\n---\n\n${skillPrompt}`;
}

export function getAgentName(agentKey: string): string {
  return AGENT_DEFS[agentKey]?.name ?? 'Coach Richy';
}
