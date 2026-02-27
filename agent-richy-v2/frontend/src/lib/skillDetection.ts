/* ── Skill detection — keyword-based trigger matching ────────────────── */

export type DetectedSkill = "coupon" | "optimizer" | "market_intel" | "price_intel" | "subscription_value" | "goal_sim" | "bill_predict" | "local_deals" | "receipt_analyze" | "investment_intel" | "grocery_plan" | "allocation_map" | "proactive" | "trajectory" | "financial_twin" | "wealth_race" | "advisor_match" | "money_map" | "ripple_tracker" | "economic_intel" | "purchase_timing" | null;

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

const GOAL_SIM_TRIGGERS = [
  "goal",
  "savings goal",
  "save for",
  "saving for",
  "how long to save",
  "emergency fund",
  "down payment",
  "vacation fund",
  "retire",
  "retirement",
  "pay off debt",
  "debt payoff",
  "financial goal",
  "how long until",
  "when can i afford",
  "simulate",
  "projection",
  "forecast my savings",
  "savings calculator",
  "reach my goal",
  "monte carlo",
  "probability of",
];

const BILL_PREDICT_TRIGGERS = [
  "upcoming bills",
  "bills this month",
  "bills next month",
  "predict my bills",
  "bill forecast",
  "bill calendar",
  "when are my bills due",
  "bill tracker",
  "monthly bills",
  "how much do i owe",
  "bills coming up",
  "cash flow",
  "bill schedule",
  "recurring bills",
  "autopay",
  "due dates",
];

const LOCAL_DEAL_TRIGGERS = [
  "local deals",
  "deals near me",
  "sales near me",
  "weekly ads",
  "grocery sales",
  "store sales",
  "whats on sale",
  "deals this week",
  "sales this week",
  "nearby deals",
  "local sales",
  "flyer",
  "circular",
  "weekly specials",
  "clearance near",
];

const RECEIPT_TRIGGERS = [
  "receipt",
  "analyze my receipt",
  "what i bought",
  "grocery trip",
  "shopping trip",
  "i just bought",
  "i just spent",
  "here is my receipt",
  "break down my purchase",
  "purchase analysis",
  "did i overpay",
  "shopping analysis",
];

const GROCERY_TRIGGERS = [
  'grocery list', 'groceries', 'shopping list', 'meal plan',
  'grocery shopping', 'what to buy', 'food shopping', 'weekly shop',
  'cheapest groceries', 'grocery deals', 'shopping plan',
  'help me shop', 'optimize my groceries', 'grocery run',
  'store for groceries', 'where to buy food',
];

const ALLOCATION_TRIGGERS = [
  'allocation', 'portfolio allocation', 'how to invest',
  'investment plan', 'allocate my money', 'investment allocation',
  'build a portfolio', 'etf recommendation', 'etf allocation',
  'retirement allocation', '401k allocation', 'ira allocation',
  'asset allocation', 'stock bond split', 'investment breakdown',
  'where to put my money', 'organize my investments',
  'investment worksheet', 'monthly investment plan',
];

const PROACTIVE_TRIGGERS = [
  'any alerts', 'what should i know', 'anything coming up',
  'financial checkup', 'weekly report', 'how am i doing',
  'my financial health', 'health score', 'money checkup',
  'whats my score', 'financial score', 'digest',
];

const TRAJECTORY_TRIGGERS = [
  'financial future', 'retirement', 'when can i retire',
  'long term', 'wealth projection', 'net worth projection',
  'where am i headed', 'financial trajectory', 'project my savings',
  'compound growth', 'future net worth', '10 years from now',
  'financial independence', 'fire', 'early retirement',
];

const TWIN_TRIGGERS = [
  'what if', 'what would happen if', 'simulate', 'financial twin',
  'life simulation', 'if i moved', 'if i quit', 'if i had a baby',
  'if i bought a house', 'if i changed jobs', 'if i started a business',
  'if i got a raise', 'if i retired', 'run a simulation',
  'model this scenario', 'show me the impact',
];

const RACE_TRIGGERS = [
  'how do i compare', 'my rank', 'my ranking', 'wealth race',
  'percentile', 'how am i doing vs', 'compare me', 'leaderboard',
  'achievements', 'my achievements', 'badges', 'my streak',
  'am i doing well', 'am i behind', 'am i ahead',
];

const ADVISOR_TRIGGERS = [
  'financial advisor', 'find an advisor', 'need an advisor',
  'professional advice', 'talk to someone', 'licensed advisor',
  'cfp', 'wealth manager', 'financial planner', 'need help from a pro',
  'too complex', 'connect me with', 'advisor marketplace',
  'human advisor', 'real advisor',
];

const MONEY_MAP_TRIGGERS = [
  'money map', 'where does my money go', 'show me my flows',
  'financial overview', 'spending overview', 'cash flow map',
  'visualize my money', 'money flow', 'income vs expenses',
  'where is my money going', 'spending map', 'flow diagram',
  'show me everything', 'financial picture', 'the big picture',
];

const RIPPLE_TRIGGERS = [
  'ripple', 'ripple effect', 'invisible raise', 'my raise',
  'how much have i saved', 'total savings', 'what have i saved',
  'compound impact', 'lifetime impact', 'show me the impact',
  'i cancelled', 'i switched', 'i negotiated', 'i saved',
  'what difference does', 'does it matter', 'is it worth it',
  'small savings', 'every dollar',
];

const ECONOMIC_TRIGGERS = [
  'economy', 'inflation', 'recession', 'interest rates',
  'economic', 'cpi', 'consumer spending', 'unemployment',
  'gas prices', 'housing market', 'fed rate', 'mortgage rate',
  'economic outlook', 'market conditions', 'cost of living increase',
  'prices going up', 'everything is expensive', 'economic impact',
  'how is the economy', 'financial news',
];

const PURCHASE_TIMING_TRIGGERS = [
  'should i buy', 'when to buy', 'is now a good time to buy',
  'best time to buy', 'should i wait', 'will prices drop',
  'will it go on sale', 'when is the best deal', 'buy now or wait',
  'is this a good price', 'price going up', 'price going down',
  'hold off on buying', 'when should i buy', 'purchase timing',
];

const INVESTMENT_INTEL_TRIGGERS = [
  "top rated stocks",
  "best rated stocks",
  "analyst ratings",
  "consensus rating",
  "what do analysts rate",
  "highest rated",
  "stock consensus",
  "analyst consensus",
  "wall street ratings",
  "top picks",
  "analyst top picks",
  "investment themes",
  "what are analysts buying",
  "highest conviction",
  "leaderboard",
  "stock rankings",
  "best stocks",
  "firm ratings",
  "goldman rates",
  "morningstar rates",
  "price targets",
  "bull case bear case",
  "sector consensus",
  "overweight underweight",
  "research says",
  "analysts say about",
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
  if (RECEIPT_TRIGGERS.some((t) => lower.includes(t))) return "receipt_analyze";
  if (PURCHASE_TIMING_TRIGGERS.some((t) => lower.includes(t))) return "purchase_timing";
  if (MONEY_MAP_TRIGGERS.some((t) => lower.includes(t))) return "money_map";
  if (RIPPLE_TRIGGERS.some((t) => lower.includes(t))) return "ripple_tracker";
  if (ECONOMIC_TRIGGERS.some((t) => lower.includes(t))) return "economic_intel";
  if (PROACTIVE_TRIGGERS.some((t) => lower.includes(t))) return "proactive";
  if (TRAJECTORY_TRIGGERS.some((t) => lower.includes(t))) return "trajectory";
  if (TWIN_TRIGGERS.some((t) => lower.includes(t))) return "financial_twin";
  if (RACE_TRIGGERS.some((t) => lower.includes(t))) return "wealth_race";
  if (ADVISOR_TRIGGERS.some((t) => lower.includes(t))) return "advisor_match";
  if (INVESTMENT_INTEL_TRIGGERS.some((t) => lower.includes(t))) return "investment_intel";
  if (BILL_PREDICT_TRIGGERS.some((t) => lower.includes(t))) return "bill_predict";
  if (LOCAL_DEAL_TRIGGERS.some((t) => lower.includes(t))) return "local_deals";
  if (GOAL_SIM_TRIGGERS.some((t) => lower.includes(t))) return "goal_sim";
  if (GROCERY_TRIGGERS.some((t) => lower.includes(t))) return "grocery_plan";
  if (ALLOCATION_TRIGGERS.some((t) => lower.includes(t))) return "allocation_map";
  if (OPTIMIZER_TRIGGERS.some((t) => lower.includes(t))) return "optimizer";
  if (MARKET_INTEL_TRIGGERS.some((t) => lower.includes(t))) return "market_intel";
  return null;
}
