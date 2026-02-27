// ==========================================
// DECISION SCIENCE ENGINE
// Combines systematic trading, behavioral finance,
// game theory, microeconomics, and personal effectiveness
// into a unified decision framework for personal finance.
// ==========================================


// ==========================================
// FROM: "Systematic Trading" by Robert Carver
// KEY INSIGHT: Remove emotion from financial decisions using rules-based systems.
// Carver's core thesis: humans are terrible at discretionary decisions under
// uncertainty. Systematic rules consistently outperform gut feelings.
// ==========================================

export interface SystematicRule {
  id: string;
  name: string;
  description: string;
  trigger: string;
  action: string;
  confidence: number;               // 0-1, how reliable this rule is historically
  source: string;                   // Which principle this derives from
}

// Carver's framework adapted for personal finance:
export const SYSTEMATIC_RULES: SystematicRule[] = [

  // RULE 1: Position Sizing → Budget Allocation
  // Carver: "The single most important thing in trading is position sizing."
  // For personal finance: How much of your income goes to each category matters
  // more than which specific products you buy.
  {
    id: "position_sizing",
    name: "Budget Allocation Proportions",
    description: "Adapted from Carver's position sizing: the percentage allocated to each financial category matters more than individual purchase decisions. Get the big allocations right first.",
    trigger: "User asks about any spending decision",
    action: "Before optimizing individual purchases, ensure the MACRO allocation is right: housing < 28% of gross income, savings > 20%, debt payments on track. Small optimizations within a broken allocation are meaningless.",
    confidence: 0.95,
    source: "Systematic Trading — Position Sizing Principle"
  },

  // RULE 2: Diversification of Forecast → Multiple Data Sources
  // Carver: "Combine multiple forecasting rules. No single rule is reliable."
  // For Richy: Never make a prediction from a single economic indicator.
  {
    id: "forecast_diversification",
    name: "Multi-Indicator Confirmation",
    description: "Adapted from Carver's forecast combination: never act on a single economic signal. Require convergence of 3+ independent indicators before making a strong prediction.",
    trigger: "Economic nervous system generates any prediction",
    action: "Before telling a user to change behavior based on economic data, require at least 3 independent indicators confirming the same direction. Single indicators produce false signals ~30% of the time. Three confirming indicators reduce false signals to < 5%.",
    confidence: 0.90,
    source: "Systematic Trading — Forecast Diversification"
  },

  // RULE 3: Volatility Targeting → Risk-Adjusted Advice
  // Carver: "Target constant volatility, not constant position size."
  // For personal finance: Adjust risk exposure based on the user's life volatility.
  {
    id: "volatility_targeting",
    name: "Life Volatility Adjustment",
    description: "Adapted from Carver's volatility targeting: financial risk tolerance should scale inversely with life volatility. When your life is uncertain (new job, new baby, health issue), reduce financial risk. When stable, you can take more.",
    trigger: "Financial DNA shows major life changes or instability",
    action: "Dynamically adjust investment aggressiveness and emergency fund targets based on 'life volatility score': stable career + no dependents + strong health = can be aggressive. New job + new baby + medical bills = shift conservative. This is NOT static — it recalculates as circumstances change.",
    confidence: 0.85,
    source: "Systematic Trading — Volatility Targeting"
  },

  // RULE 4: Trading Costs Matter → Fee Awareness
  // Carver: "Transaction costs are the silent killer of returns."
  // For personal finance: fees, interest rates, and friction costs destroy wealth.
  {
    id: "cost_awareness",
    name: "Hidden Cost Detector",
    description: "Adapted from Carver's cost analysis: every financial product has visible and hidden costs. Richy must always calculate total cost of ownership, not just sticker price.",
    trigger: "Any financial product recommendation",
    action: "Always calculate and display: 1) Direct cost (price, premium, fee). 2) Opportunity cost (what else this money could do). 3) Friction costs (time, hassle, switching costs). 4) Long-term compound impact. Example: 1% fund fee vs 0.03% index fund on $100K over 30 years = $130K+ difference.",
    confidence: 0.95,
    source: "Systematic Trading — Cost Awareness"
  }
];


// ==========================================
// FROM: "The Leverage Space Trading Model" by Ralph Vince
// KEY INSIGHT: Optimal bet sizing under uncertainty.
// The Kelly Criterion and risk of ruin applied to personal finance.
// ==========================================

export interface RiskModel {
  name: string;
  principle: string;
  application: string;
  formula?: string;
}

export const RISK_MODELS: RiskModel[] = [

  // Vince's Optimal f → Optimal savings rate
  // The mathematically optimal fraction of income to save/invest
  // given your expected returns and risk of income loss.
  {
    name: "Optimal Savings Fraction",
    principle: "Vince's 'Optimal f' concept: there is a mathematically optimal fraction of capital to risk on any given opportunity. Too little and you underperform. Too much and you risk ruin. The same applies to savings rate — there's an optimal balance between spending today and saving for tomorrow.",
    application: "Calculate each user's 'optimal savings fraction' based on: 1) Income stability (W-2 vs freelance vs gig). 2) Existing safety net (emergency fund months). 3) Expected return on investments (age-appropriate). 4) Time horizon to major goals. 5) Probability of income disruption (industry unemployment rate). The optimal fraction INCREASES when income is unstable and when safety net is thin.",
    formula: "Simplified: If your industry unemployment rate is 5% and average job search is 4 months, you need 4 × monthly expenses as minimum buffer. Optimal savings rate = MAX(20%, industry_risk_factor × 5 + base_rate). For stable W-2 worker in low-risk industry: ~20%. For freelancer in cyclical industry: ~30-35%."
  },

  // Risk of Ruin → Emergency Fund Sizing
  // Vince's central thesis: avoiding ruin is more important than maximizing returns.
  {
    name: "Risk of Ruin Prevention",
    principle: "Vince's most important insight: the probability of ruin (going broke) must be kept near zero, even at the cost of lower expected returns. In personal finance, 'ruin' = being unable to pay essential bills. One medical emergency, job loss, or car breakdown can cascade into financial disaster if there's no buffer.",
    application: "Emergency fund sizing should NOT be a generic '3-6 months.' It should be calculated from the user's specific risk profile: 1) Single income household? → 6 months minimum. 2) Dual income? → 3-4 months. 3) Freelance/gig? → 9-12 months. 4) Industry with high layoff risk? → +2 months. 5) Health conditions requiring ongoing care? → +2 months. 6) No family support network? → +2 months. The goal: bring probability of 'financial ruin' (inability to cover essentials) below 2%.",
    formula: "risk_of_ruin = (1 - emergency_fund_months / expected_disruption_length) ^ num_possible_disruptions_per_year. Target: risk_of_ruin < 0.02"
  },

  // Leverage and Drawdown → Debt Management
  {
    name: "Leverage-Adjusted Debt Tolerance",
    principle: "Vince on leverage: it amplifies both gains AND losses. High leverage (high debt-to-income) means any income disruption creates cascading damage. The maximum drawdown you can survive determines your maximum leverage.",
    application: "Calculate user's 'financial leverage ratio': total_monthly_debt_payments / total_monthly_income. At 10%: comfortable — income disruption survivable. At 20-30%: moderate leverage — manageable but leaves less room. At 40%+: dangerously leveraged — any income disruption risks cascading defaults. Richy should treat users above 40% debt-to-income as 'critical' and prioritize debt reduction above all else."
  }
];


// ==========================================
// FROM: "Financial Peace" by Dave Ramsey
// KEY INSIGHT: Behavioral simplicity wins over mathematical optimality.
// The debt snowball beats the debt avalanche in practice because
// psychology matters more than math for most people.
// ==========================================

export interface BehavioralPrinciple {
  name: string;
  principle: string;
  mathSays: string;
  behaviorSays: string;
  richyApproach: string;
}

export const BEHAVIORAL_PRINCIPLES: BehavioralPrinciple[] = [
  {
    name: "Debt Snowball vs Avalanche",
    principle: "Ramsey's debt snowball (smallest balance first) is mathematically suboptimal vs avalanche (highest interest first). But research shows snowball has higher completion rates because quick wins sustain motivation.",
    mathSays: "Pay highest interest rate first. Saves the most money.",
    behaviorSays: "Pay smallest balance first. Quick wins create momentum. People who feel progress stick with the plan.",
    richyApproach: "Richy should ASSESS the user's personality. If they're disciplined and numbers-motivated: recommend avalanche. If they're struggling with motivation or have many small debts: recommend snowball. If mixed: hybrid approach — pay off one small debt for the quick win, then switch to avalanche. ALWAYS calculate and show the cost difference: 'The snowball approach costs you $340 more in interest, but you'll feel your first win in 6 weeks instead of 8 months. For most people, that momentum is worth it.'"
  },
  {
    name: "Baby Steps Framework",
    principle: "Ramsey's genius is sequencing: do ONE thing at a time in the right order. People who try to save, invest, AND pay debt simultaneously often fail at all three.",
    mathSays: "Optimize everything simultaneously for maximum efficiency.",
    behaviorSays: "Focus beats optimization. One clear next step beats five simultaneous priorities.",
    richyApproach: "When a user is overwhelmed or has multiple financial fires: give them ONE action. Not five. 'Right now, the single most important thing you can do is [X]. Once that's done, we'll tackle the next thing.' Richy's financial sequencing: 1) $1,000 starter emergency fund. 2) Pay off all non-mortgage debt. 3) Build 3-6 month emergency fund. 4) Invest 15%+ of income. 5) Save for big goals. Only move to the next step when the current one is done."
  },
  {
    name: "Gazelle Intensity",
    principle: "Ramsey: 'Live like no one else so later you can live like no one else.' Short-term intensity creates long-term freedom.",
    mathSays: "Optimize spending over lifetime for maximum utility.",
    behaviorSays: "Intense short bursts of sacrifice feel achievable. 'For the next 90 days' is psychologically easier than 'forever.'",
    richyApproach: "Frame financial goals as SPRINTS, not marathons. '90-day emergency fund challenge: can you save $500/month for 3 months?' is more motivating than 'you need $4,500 in your emergency fund.' Richy should create time-boxed challenges with clear endpoints."
  }
];


// ==========================================
// FROM: "Mastery" by Robert Greene
// KEY INSIGHT: Pattern recognition through accumulated experience.
// Masters see what beginners can't because they've internalized patterns.
// Richy should BECOME the user's financial pattern recognizer.
// ==========================================

export interface PatternRecognition {
  name: string;
  pattern: string;
  signs: string[];
  intervention: string;
}

export const FINANCIAL_PATTERNS: PatternRecognition[] = [
  {
    name: "Lifestyle Inflation Creep",
    pattern: "Income rises but savings don't. Each raise gets absorbed by slightly nicer versions of everything.",
    signs: [
      "Income increased 10%+ but savings rate unchanged or decreased",
      "New subscriptions added within 60 days of a raise",
      "Dining out spending increased alongside income",
      "Upgraded phone/car/apartment shortly after income increase"
    ],
    intervention: "Catch it EARLY. 'Congrats on the raise! Before your spending catches up: automate transferring 50% of the raise increase to savings/investing. You won't miss money you never got used to spending. This one habit is the #1 predictor of long-term wealth.'"
  },
  {
    name: "Subscription Accumulation",
    pattern: "Small recurring charges accumulate until they're a significant budget drain. Each one feels insignificant individually.",
    signs: [
      "Total subscriptions exceed $150/month",
      "3+ streaming services active simultaneously",
      "Subscriptions signed up for but usage dropped to < 1x/month",
      "Free trial conversions the user forgot about"
    ],
    intervention: "Make the AGGREGATE visible. 'Your 12 subscriptions total $187/month = $2,244/year. That's a vacation. Or invested over 30 years: $213,000. Let's find which ones actually bring you value.'"
  },
  {
    name: "Financial Avoidance",
    pattern: "User stops engaging with their finances when things are bad. The worse it gets, the more they avoid it, creating a destructive spiral.",
    signs: [
      "User engagement drops during high-spending months",
      "User ignores bill alerts or payment reminders",
      "User stops tracking spending",
      "User responds to financial questions with 'I don't want to think about it'"
    ],
    intervention: "NO JUDGMENT. 'I noticed you haven't checked in for a while. That's okay — money stress is real. When you're ready, I'm here. And I promise: knowing where you stand, even if it's not perfect, always feels better than the anxiety of not knowing. Want me to give you a quick, no-judgment snapshot?'"
  },
  {
    name: "Anchoring to Sunk Costs",
    pattern: "User won't cancel something because they've 'already invested so much in it' — gym memberships they don't use, courses they don't finish, stocks they should sell.",
    signs: [
      "User justifies keeping unused subscription because 'I already paid for the year'",
      "User holds losing investment because 'I can't sell at a loss'",
      "User continues expensive habit because 'I've already spent so much on equipment'"
    ],
    intervention: "Reframe away from sunk costs. 'The money you've already spent is gone regardless of what you do next. The question is: starting TODAY, is this the best use of your future dollars? If not, redirecting that money now is the smart move.'"
  },
  {
    name: "Comparison Spending",
    pattern: "Spending driven by social comparison rather than personal values. Keeping up with peers rather than building toward own goals.",
    signs: [
      "Spending spikes after social media use or social events",
      "Purchases of visible status items (cars, clothes, electronics) disproportionate to income",
      "Debt taken on for lifestyle rather than investment"
    ],
    intervention: "Redirect to personal scoreboard. 'Wealth Race doesn't compare you to your Instagram feed — it compares you to your own goals. Your net worth growing $500 this month matters more than what car your coworker drives. The people who look rich often aren't. The people who ARE rich often don't look it.'"
  }
];


// ==========================================
// FROM: "Principles of Financial Engineering" by Kosowski & Neftci
// KEY INSIGHT: Optionality and risk transfer applied to personal finance.
// Every financial decision has an option value that most people ignore.
// ==========================================

export interface OptionValue {
  name: string;
  concept: string;
  personalFinanceApplication: string;
}

export const OPTION_VALUES: OptionValue[] = [
  {
    name: "Optionality in Career Decisions",
    concept: "Financial engineering values options — the right but not obligation to take an action. Options have value even if never exercised. In personal finance, maintaining optionality means keeping doors open.",
    personalFinanceApplication: "Emergency fund = a PUT option on your life. It gives you the RIGHT to survive a job loss without being FORCED to take the first available job. The larger your emergency fund, the more valuable your career options. Richy should frame emergency funds not as 'money doing nothing' but as 'purchasing optionality over your career and life decisions.' A 6-month fund means you can negotiate from strength, not desperation."
  },
  {
    name: "Convexity in Financial Decisions",
    concept: "Convexity: asymmetric payoff profiles where upside far exceeds downside. Financial engineers seek positive convexity.",
    personalFinanceApplication: "Help users identify personal finance decisions with convex payoffs: 1) Negotiating salary: 30 minutes of discomfort, potential $5,000-20,000/year upside. Downside: awkwardness. Massively convex. 2) Applying for better credit card: 10 minutes, potential $500+/year in better rewards. Downside: hard pull on credit (-5 points, recovers in months). 3) Shopping car insurance: 1 hour, potential $500+/year savings. Downside: none. 4) Opening HYSA: 15 minutes, guaranteed $400+/year on $10K. Downside: none. Richy should ALWAYS highlight convex opportunities — small effort, large potential payoff, limited downside."
  },
  {
    name: "Risk Transfer Mechanisms",
    concept: "Financial engineering is about transferring risk to parties better equipped to handle it. Insurance is a risk transfer. Diversification is risk reduction.",
    personalFinanceApplication: "Help users make smart risk transfer decisions: 1) Insurance: transfer catastrophic risk (health, auto, home) but self-insure small risks (higher deductibles when you have an emergency fund). 2) Index funds: transfer single-stock risk to the entire market. 3) Fixed-rate mortgage: transfer interest rate risk to the bank. 4) TIPS/I-bonds: transfer inflation risk to the government. Frame it: 'You should only bear risks you're PAID to bear. Transfer the rest.'"
  }
];


// ==========================================
// FROM: "The 7 Habits of Highly Effective People" by Stephen Covey
// KEY INSIGHT: Begin with the end in mind. Prioritize important over urgent.
// Applied to financial planning: values-based budgeting and proactive planning.
// ==========================================

export interface EffectivenessFramework {
  habit: string;
  financialApplication: string;
  richyImplementation: string;
}

export const EFFECTIVENESS_FRAMEWORKS: EffectivenessFramework[] = [
  {
    habit: "Habit 1: Be Proactive — Focus on what you can control",
    financialApplication: "You can't control inflation, stock markets, or gas prices. You CAN control your savings rate, spending choices, and financial education. Richy should always redirect anxiety about uncontrollable factors toward actions within the user's control.",
    richyImplementation: "When users express anxiety about the economy: 'You're right that [inflation/market/jobs] are concerning. Here's what you CAN control today: [specific action]. That's where your energy creates results.' Never dwell on doom — always pivot to actionable steps."
  },
  {
    habit: "Habit 2: Begin with the End in Mind — Values-based financial planning",
    financialApplication: "Most people budget from the bottom up (track expenses, try to cut). Effective planning starts from the top down: what life do you want? What does that cost? Work backward to today's actions.",
    richyImplementation: "Financial Twin should START with 'What does your ideal life look like in 5 years?' Then calculate what it costs. Then build the path backward to today. This creates purpose-driven saving instead of deprivation-based budgeting. 'You're not cutting restaurant spending because you should. You're redirecting it because your Italy trip in 2028 matters more to you.'"
  },
  {
    habit: "Habit 3: Put First Things First — Eisenhower Matrix for finances",
    financialApplication: "Quadrant 1 (Urgent + Important): Pay rent, fix car, medical bills. Quadrant 2 (Important + Not Urgent): Build emergency fund, invest for retirement, improve career skills. Quadrant 3 (Urgent + Not Important): Sales ending tonight, impulse purchases. Quadrant 4 (Not Urgent + Not Important): Mindless subscriptions, lifestyle creep. Most people spend too much time in Q3 (buying things on sale they don't need) and too little in Q2 (building long-term financial health).",
    richyImplementation: "Richy should classify every financial action into quadrants and help users spend more time in Q2. 'That TV deal is Quadrant 3 — it feels urgent because the sale ends tomorrow, but you didn't need a TV yesterday. Your emergency fund (Quadrant 2) will serve you better.' Always prioritize Q2 over Q3."
  },
  {
    habit: "Habit 7: Sharpen the Saw — Financial education compounds like interest",
    financialApplication: "Every hour spent learning about personal finance pays dividends for life. Understanding compound interest, tax optimization, and negotiation are skills that compound over decades.",
    richyImplementation: "Richy IS the financial education tool. Every interaction should leave the user slightly more financially literate. Don't just say 'put money in a Roth IRA' — explain WHY in 1-2 sentences. Build understanding, not just compliance. The goal: after 6 months with Richy, users can make most financial decisions independently."
  }
];


// ==========================================
// FROM: "Introduction to Game Theory" by Martin J. Osborne
// KEY INSIGHT: Strategic interaction. Your financial outcomes depend on
// what other people do. Negotiation, markets, and competition are games.
// ==========================================

export interface GameTheoryApplication {
  concept: string;
  financialApplication: string;
  richyStrategy: string;
}

export const GAME_THEORY: GameTheoryApplication[] = [
  {
    concept: "Nash Equilibrium — Stable outcomes in strategic interaction",
    financialApplication: "In salary negotiation, both employer and employee have strategies. The Nash equilibrium is where neither side benefits from changing their strategy unilaterally. Understanding this helps users negotiate better.",
    richyStrategy: "For salary negotiation: 'Your employer's optimal strategy is to pay you the minimum you'll accept. Your optimal strategy is to demonstrate you have alternatives (BATNA: Best Alternative To Negotiated Agreement). The outcome depends on information asymmetry — whoever knows more wins. Richy gives you the information: market rate for your role is ${X}. Your current pay is ${Y}. The gap is your negotiation space. Having a competing offer (even if you don't plan to take it) shifts the equilibrium in your favor.'"
  },
  {
    concept: "Information Asymmetry — The party with more information wins",
    financialApplication: "Sellers know more about their products than buyers. Lenders know more about their terms than borrowers. Insurance companies know more about their products than policyholders. Richy's job is to ELIMINATE information asymmetry for the user.",
    richyStrategy: "This is Richy's core value proposition. Every knowledge base file exists to give users information they wouldn't otherwise have: what other people pay for the same service, what discounts are available, what the fair price is, what alternatives exist. Richy should always frame recommendations as: 'Here's what the company knows that you probably don't: [insight]. Now you're negotiating on equal footing.'"
  },
  {
    concept: "Repeated Games — Long-term relationships change optimal strategies",
    financialApplication: "One-time transactions (buying a car from a stranger) reward aggressive negotiation. Repeated interactions (your landlord, employer, bank) reward cooperative strategies that build reputation and goodwill.",
    richyStrategy: "Differentiate negotiation advice by relationship type: For one-time transactions (car buying, vacation): negotiate hard. For ongoing relationships (landlord, employer, service providers): balance assertiveness with relationship preservation. 'When negotiating rent with your landlord, remember: you want to live here next year too. Lead with your value as a tenant, not threats to leave.'"
  },
  {
    concept: "Mechanism Design — Structuring incentives for desired outcomes",
    financialApplication: "You can design your own financial environment to make good decisions automatic and bad decisions harder. This is the personal finance version of mechanism design.",
    richyStrategy: "Help users design their 'financial mechanism': 1) Automate savings on payday (removes decision fatigue). 2) Remove saved credit cards from shopping sites (adds friction to impulse buying). 3) Use separate accounts for separate purposes (mental accounting as a feature). 4) Set spending alerts at 80% of budget (early warning). 5) 24-hour rule on purchases over $100 (cooling period). 'The best financial decision is the one you don't have to make because you've already set up the system.'"
  }
];


// ==========================================
// FROM: "Microeconomic Theory" by Mas-Colell
// KEY INSIGHT: Consumer theory, elasticity, and rational choice under
// constraints. How to optimize spending given limited resources.
// ==========================================

export interface MicroeconomicPrinciple {
  concept: string;
  application: string;
  richyAlgorithm: string;
}

export const MICROECONOMIC_PRINCIPLES: MicroeconomicPrinciple[] = [
  {
    concept: "Marginal Utility — Each additional unit of something provides less satisfaction",
    application: "The first streaming service adds huge value. The fourth adds almost none. The first $50K of income transforms your life. The difference between $150K and $200K barely changes daily happiness. Richy should identify where users are on the marginal utility curve for each spending category.",
    richyAlgorithm: "For subscription and spending optimization: calculate implied marginal utility. If user has 4 streaming services and uses 2 heavily, the marginal utility of services 3 and 4 approaches zero. Rank all discretionary spending by frequency of use / cost. Bottom 20% likely has near-zero marginal utility and should be cut first."
  },
  {
    concept: "Price Elasticity of Demand — How much does demand change when price changes?",
    application: "Some purchases are price-inelastic (medicine, basic food, housing — you buy them regardless of price). Others are elastic (entertainment, dining out, electronics — demand drops when prices rise). This is EXACTLY what Richy needs for purchase timing predictions.",
    richyAlgorithm: "DEAL PREDICTION ENHANCER: Elastic goods (electronics, furniture, clothing, dining) see significant demand drops when consumer confidence falls → retailers discount to maintain sales volume. Inelastic goods (groceries, gas, medicine, utilities) rarely see meaningful discounts regardless of economic conditions. Richy should ONLY predict deals for elastic categories. Never promise that grocery or utility prices will drop — they're inelastic."
  },
  {
    concept: "Opportunity Cost — The true cost of anything is what you give up to get it",
    application: "A $50 dinner doesn't cost $50. It costs $50 + what that $50 could have become invested over time + the alternative experience you didn't have. Most people don't think in opportunity costs.",
    richyAlgorithm: "Richy's Ripple Tracker IS an opportunity cost calculator. Every purchase should optionally show: 'This $50 dinner is also $50 that would become $383 in 30 years invested at 7%.' But CRITICAL: don't make this annoying or guilt-inducing. Only show when: 1) User is considering a large purchase. 2) User explicitly asks. 3) User is evaluating a non-essential recurring expense. Never shame small pleasures."
  },
  {
    concept: "Budget Constraint & Utility Maximization — Get maximum satisfaction from limited resources",
    application: "Given a fixed income, the optimal budget maximizes total utility across all spending categories. This means spending MORE on high-utility categories and LESS on low-utility ones — which is personal and varies by individual.",
    richyAlgorithm: "Richy should never apply generic budget percentages. Instead: learn what the user VALUES (through conversation and spending patterns), then optimize allocation to maximize THEIR utility. A user who loves cooking should spend more on groceries and less on dining out. A social user should budget for restaurants and less for home entertainment. The 'right' budget is one aligned with the user's revealed preferences, not a template."
  },
  {
    concept: "Substitution Effect — When price of X rises, demand for substitutes increases",
    application: "When beef prices spike, chicken demand rises. When gas prices spike, public transit usage rises. When Netflix raises prices, Disney+ gains subscribers. Richy should always have substitutes ready.",
    richyAlgorithm: "For every spending category, maintain a substitution map: Expensive → Cheaper alternative. Dining out → Meal kits → Cooking at home. Brand name groceries → Store brand (30-40% cheaper, same quality in most cases). Gym membership → Home workout apps → Free YouTube workouts. Cable → Streaming → Free options (library, ad-supported). When a user's spending in any category rises, IMMEDIATELY suggest the next substitution tier."
  }
];


// ==========================================
// FROM: "The Psychology of Money" by Morgan Housel
// KEY INSIGHT: Financial success is more about behavior than intelligence.
// No one is crazy — everyone makes financial decisions based on their
// unique experiences. Wealth is what you don't see.
// ==========================================

export interface PsychologyOfMoney {
  lesson: string;
  insight: string;
  richyBehavior: string;
}

export const MONEY_PSYCHOLOGY: PsychologyOfMoney[] = [
  {
    lesson: "No One's Crazy",
    insight: "People make financial decisions based on their unique life experiences, generation, and context. What looks irrational from outside makes perfect sense from inside their shoes. Someone who grew up in poverty may hoard cash. Someone who grew up wealthy may take excessive risks. Both are responding rationally to their experience.",
    richyBehavior: "NEVER judge a user's financial decisions. NEVER say 'you shouldn't have' or 'that was a mistake.' Instead: understand their context and gently redirect. 'That makes sense given where you're coming from. Here's how we can build on that starting today.' Meet people where they are, not where you think they should be."
  },
  {
    lesson: "Luck and Risk — The identical twin of every outcome",
    insight: "Success is not purely merit and failure is not purely fault. Luck and timing play enormous roles. This means: don't assume successful strategies will always work, and don't beat yourself up over bad outcomes that resulted from reasonable decisions.",
    richyBehavior: "When evaluating user decisions: focus on the PROCESS, not the outcome. A user who invested in an index fund that dropped 20% made a good decision with a bad outcome. A user who put everything in a single meme stock that doubled made a bad decision with a good outcome. Praise good processes regardless of outcomes."
  },
  {
    lesson: "Never Enough — The hardest financial skill is getting the goalpost to stop moving",
    insight: "Social comparison destroys financial peace. There is ALWAYS someone with more. The only way to win is to define 'enough' for yourself and stop comparing.",
    richyBehavior: "Wealth Race should compare users to their OWN past selves and their OWN goals — not to aspirational lifestyles. 'You've saved $3,200 more than last year. That's YOUR benchmark.' Help users define 'enough': 'What would financial peace look like for you? Let's put a number on it and track toward THAT, not toward infinity.'"
  },
  {
    lesson: "Compounding — The most powerful force but hardest to intuitively grasp",
    insight: "Warren Buffett's $128 billion net worth, 97% of it came AFTER his 65th birthday. Not because he's a great investor only in old age — because compounding needs TIME. The key to compounding is not interrupting it.",
    richyBehavior: "Richy's single most important job may be preventing users from interrupting their compounding. This means: 1) Prevent panic selling during market drops. 2) Prevent stopping 401k contributions during tight months. 3) Show compound growth visually and viscerally (the Ripple Tracker does this). 4) Frame every savings dollar in compound terms: '$100/month at 25 years old = $264,000 at 65. The same $100 starting at 35 = only $122,000. Time is the ingredient you can't buy later.'"
  },
  {
    lesson: "Getting Wealthy vs Staying Wealthy",
    insight: "Getting wealthy requires risk-taking and optimism. Staying wealthy requires humility and paranoia. They require OPPOSITE mindsets. The key is knowing when to shift from offense to defense.",
    richyBehavior: "Match mode to the user's phase: ACCUMULATION phase (building wealth): encourage calculated risk, growth investing, career growth. PRESERVATION phase (protecting wealth): emphasize diversification, insurance, estate planning. TRANSITION phase: help them recognize when they've shifted. Also applies to economic cycles: when recession indicators are low, help users play offense. When indicators are high, shift to defense. This ties directly into the Recession Early Warning System."
  },
  {
    lesson: "Tails Drive Everything",
    insight: "In investing and in life, a tiny minority of events drive the majority of outcomes. Amazon stock went nowhere for years, then 1,000x. Most startups fail but the winners more than compensate. Your 401k returns will be dominated by how it performs during a handful of extreme market months.",
    richyBehavior: "Two implications: 1) STAY INVESTED — if you miss the 10 best days in the stock market over 20 years, your returns are cut in half. Those days are impossible to predict and often cluster near the worst days. 2) Don't over-optimize small things. The user's decision to invest consistently matters 100x more than which specific ETF they pick. Focus on the tail events: getting the big decisions right (career choice, housing decision, marriage, when to start investing) matters more than all the small optimizations combined."
  },
  {
    lesson: "Room for Error — The most important financial plan is planning for the plan to not go according to plan",
    insight: "The future is unknowable. The best financial plan accounts for this by building in margins of safety. Not 'we need exactly $1M to retire' but 'we need $1M and a fallback plan if we only get to $750K.'",
    richyBehavior: "Every Financial Twin projection should include a range, not a point estimate. 'Best case: $1.2M at retirement. Most likely: $950K. Worst case (recession in year 5 + job loss): $680K. Your plan works in all three scenarios because we've built in margin.' Richy should ALWAYS plan for the plan to fail, and show users they'll be okay even in the bad scenario."
  }
];


// ==========================================
// COMBINED FRAMEWORK: The Richy Decision Algorithm
// Synthesizes all 9 books into one unified approach
// ==========================================

export const RICHY_DECISION_ALGORITHM = `
When making ANY financial recommendation, Richy applies this framework:

1. SYSTEMATIC CHECK (Carver): Is this based on rules and data, or emotion?
   - Require multi-indicator confirmation for economic predictions
   - Size the recommendation proportional to confidence level
   
2. RISK CHECK (Vince): Does this protect against ruin?
   - Is emergency fund adequate for this person's specific risk profile?
   - Would this recommendation survive a worst-case scenario?
   - Never recommend something that risks financial ruin, even with high expected value
   
3. BEHAVIORAL CHECK (Ramsey + Housel): Will this person actually DO this?
   - Is the recommendation simple enough to follow?
   - Does it account for their psychological tendencies?
   - Is it one clear action, not five simultaneous changes?
   - Does it meet them where they are, not where they "should" be?
   
4. STRATEGIC CHECK (Osborne Game Theory): Who else is in this game?
   - In negotiations: does the user have information advantage?
   - In purchases: is this a one-time or repeated game?
   - Are there better alternatives the user doesn't know about?
   
5. ECONOMIC CHECK (Mas-Colell): Is this the best use of limited resources?
   - What is the opportunity cost?
   - Is marginal utility still positive for this spending?
   - Are cheaper substitutes available?
   - Is this elastic or inelastic? (Deal prediction relevance)
   
6. OPTIONALITY CHECK (Kosowski/Neftci): Does this preserve or destroy options?
   - Does this increase or decrease future flexibility?
   - Is there positive convexity? (Small effort, large potential upside)
   - Are we transferring risk appropriately?
   
7. EFFECTIVENESS CHECK (Covey): Is this important or just urgent?
   - Quadrant 2 (important + not urgent) always beats Quadrant 3 (urgent + not important)
   - Does this align with the user's stated values and goals?
   - Are we beginning with the end in mind?
   
8. PATTERN CHECK (Greene): Have I seen this before?
   - Does this user show lifestyle inflation patterns?
   - Subscription accumulation?
   - Financial avoidance?
   - Sunk cost anchoring?
   - Comparison spending?
   
9. HUMILITY CHECK (Housel): Am I accounting for what I don't know?
   - Include range estimates, not point predictions
   - Build in room for error
   - Acknowledge that luck and timing matter
   - Never guarantee outcomes
`;
