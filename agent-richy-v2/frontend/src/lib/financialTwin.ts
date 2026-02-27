/* ── Financial Twin — Life Simulation Engine ─────────────────────────── */

// ==========================================
// LIFE EVENT TYPES
// ==========================================

export type LifeEventType =
  | "job_change" | "raise" | "job_loss" | "career_switch"
  | "move_city" | "move_state" | "buy_home" | "sell_home" | "downsize"
  | "marriage" | "divorce" | "baby" | "child_college"
  | "start_business" | "side_hustle" | "freelance"
  | "car_purchase" | "car_payoff" | "go_carless"
  | "debt_payoff" | "take_loan" | "refinance"
  | "health_event" | "disability"
  | "inheritance" | "windfall" | "lawsuit"
  | "retirement" | "early_retirement" | "semi_retirement"
  | "education" | "certification" | "grad_school"
  | "custom";

// ==========================================
// LIFE EVENT
// ==========================================

export interface LifeEvent {
  id: string;
  type: LifeEventType;
  name: string;
  description: string;

  // Financial impact
  oneTimeCost?: number;
  oneTimeIncome?: number;
  monthlyExpenseChange?: number;           // Positive = more spending, negative = less
  monthlyIncomeChange?: number;

  // Timing
  startDate: string;
  endDate?: string;                        // Some events are permanent, some temporary
  duration?: number;                       // Months

  // Cascading effects
  affectsInsurance: boolean;
  affectsTaxBracket: boolean;
  affectsHousing: boolean;
  affectsTransportation: boolean;

  // Metadata
  probability?: number;                    // For uncertain events: "70% chance of getting the raise"
  userConfidence: "planning" | "considering" | "hypothetical";
}

// ==========================================
// TWIN SIMULATION
// ==========================================

export interface TwinSimulation {
  id: string;
  name: string;                            // "What if I move to Austin and take the new job?"
  createdAt: string;

  // The scenario
  events: LifeEvent[];

  // Base state (from Financial DNA)
  baselineSnapshot: {
    monthlyIncome: number;
    monthlyExpenses: number;
    totalDebt: number;
    totalSavings: number;
    netWorth: number;
    location: string;
    costOfLivingIndex: number;
  };

  // Simulated results at each year
  timeline: {
    year: number;
    month: number;                         // Month within the year
    date: string;

    // Core metrics
    monthlyIncome: number;
    monthlyExpenses: number;
    monthlySurplus: number;
    totalDebt: number;
    totalSavings: number;
    totalInvestments: number;
    netWorth: number;

    // Events that trigger this year
    eventsThisYear: string[];

    // Quality of life indicators
    financialStressIndex: number;          // 1-100 (lower = less stress)
    disposableIncomePerDay: number;
    canAffordEmergency: boolean;           // 3-month expenses covered?
  }[];

  // Comparison to baseline (no changes)
  vsBaseline: {
    netWorthDifference5yr: number;
    netWorthDifference10yr: number;
    netWorthDifference20yr: number;
    retirementAgeDifference: number;       // Months earlier/later
    totalLifetimeEarningsDifference: number;
    stressIndexComparison: number;         // Better or worse
    verdict: string;                       // "Moving to Austin puts you $127K ahead in 10 years"
  };

  // Risk analysis
  risks: {
    description: string;
    probability: number;
    financialImpact: number;
    mitigation: string;
  }[];

  // Richy's analysis
  summary: string;
  recommendation: string;
  keyInsight: string;                      // The one thing they need to know
}

// ==========================================
// LIFE EVENT TEMPLATES
// ==========================================

export const LIFE_EVENT_TEMPLATES: Record<LifeEventType, {
  name: string;
  questionsToAsk: string[];
  typicalCosts: { item: string; low: number; mid: number; high: number }[];
  cascadingEffects: string[];
  commonMistakes: string[];
}> = {
  move_city: {
    name: "Move to a New City",
    questionsToAsk: [
      "Which city are you considering?",
      "Do you have a job lined up there, or are you job hunting?",
      "Renting or buying?",
      "What's your timeline?",
    ],
    typicalCosts: [
      { item: "Moving expenses", low: 1500, mid: 4500, high: 12000 },
      { item: "Security deposit + first/last month", low: 2000, mid: 4000, high: 8000 },
      { item: "Cost of living adjustment (monthly)", low: -500, mid: 0, high: 800 },
    ],
    cascadingEffects: [
      "Cost of living changes (housing, groceries, gas, taxes)",
      "State income tax may change (some states have zero)",
      "Car insurance rates vary by state/city",
      "May need new professional licenses in some fields",
      "Social network reset — impacts mental health and career networking",
    ],
    commonMistakes: [
      "Not factoring in state income tax differences",
      "Underestimating moving costs by 40-60%",
      "Not researching cost of living BEFORE accepting a salary",
      "Breaking a lease without calculating penalties",
    ],
  },

  baby: {
    name: "Having a Baby",
    questionsToAsk: [
      "Is this your first child?",
      "Will both parents continue working?",
      "Do you have parental leave benefits?",
      "Have you looked into childcare costs in your area?",
    ],
    typicalCosts: [
      { item: "Birth (with insurance)", low: 2000, mid: 5000, high: 15000 },
      { item: "Baby gear (first year)", low: 1500, mid: 4000, high: 10000 },
      { item: "Childcare (monthly)", low: 800, mid: 1500, high: 3000 },
      { item: "Additional monthly expenses", low: 300, mid: 700, high: 1500 },
    ],
    cascadingEffects: [
      "Health insurance costs increase significantly",
      "May need larger housing",
      "Childcare is often the biggest new expense ($10K-36K/year)",
      "Tax benefits: child tax credit, dependent care FSA",
      "Life insurance becomes important",
      "Will need to start education savings (529 plan)",
    ],
    commonMistakes: [
      "Not accounting for income loss during parental leave",
      "Underestimating childcare costs",
      "Not updating life insurance and will",
      "Over-buying baby gear (most things are used for 3-6 months)",
    ],
  },

  buy_home: {
    name: "Buy a Home",
    questionsToAsk: [
      "What price range are you looking at?",
      "How much do you have saved for a down payment?",
      "What's your current rent?",
      "Have you been pre-approved for a mortgage?",
    ],
    typicalCosts: [
      { item: "Down payment (3-20%)", low: 10000, mid: 40000, high: 100000 },
      { item: "Closing costs (2-5%)", low: 5000, mid: 12000, high: 25000 },
      { item: "Home inspection + appraisal", low: 500, mid: 800, high: 1500 },
      { item: "Monthly mortgage vs rent change", low: -200, mid: 300, high: 1000 },
      { item: "Maintenance (monthly set-aside)", low: 200, mid: 400, high: 800 },
    ],
    cascadingEffects: [
      "Monthly payment may be more or less than rent",
      "Property taxes + insurance add 30-50% on top of mortgage",
      "Maintenance costs: budget 1-2% of home value per year",
      "Mortgage interest deduction (tax benefit)",
      "Building equity vs paying landlord",
      "Reduced flexibility to relocate",
    ],
    commonMistakes: [
      "Only looking at mortgage payment, ignoring taxes/insurance/maintenance",
      "Draining emergency fund for down payment",
      "Not getting pre-approved before house hunting",
      "Buying at the top of your budget instead of comfortably below",
    ],
  },

  job_change: {
    name: "Change Jobs",
    questionsToAsk: [
      "What's the new salary vs current?",
      "How do the benefits compare? (health, 401k match, PTO)",
      "Any relocation involved?",
      "Is there a gap between jobs?",
    ],
    typicalCosts: [
      { item: "Income gap (if any)", low: 0, mid: 5000, high: 15000 },
      { item: "Benefits transition costs", low: 0, mid: 500, high: 2000 },
      { item: "Wardrobe/equipment for new role", low: 0, mid: 300, high: 1500 },
    ],
    cascadingEffects: [
      "Salary change affects ALL financial projections",
      "401k match difference could be worth $2K-10K/year",
      "Health insurance premium differences",
      "Commute cost changes",
      "May lose unvested stock options or RSUs",
      "New 401k may have different fund options/fees",
    ],
    commonMistakes: [
      "Comparing salary without comparing total compensation",
      "Not negotiating (the best time to negotiate is before accepting)",
      "Forgetting to roll over old 401k",
      "Not accounting for benefits gap during transition",
    ],
  },

  raise: {
    name: "Get a Raise",
    questionsToAsk: ["How much?", "When does it start?"],
    typicalCosts: [],
    cascadingEffects: [
      "Lifestyle inflation is the #1 risk — most of the raise should go to savings/debt, not spending",
    ],
    commonMistakes: [
      "Increasing spending to match the raise instead of saving the difference",
    ],
  },

  career_switch: {
    name: "Switch Careers",
    questionsToAsk: ["What field?", "Training needed?", "Expected salary change?"],
    typicalCosts: [
      { item: "Training/certification", low: 500, mid: 5000, high: 50000 },
      { item: "Income reduction during transition", low: 0, mid: 10000, high: 50000 },
    ],
    cascadingEffects: [
      "May require education investment",
      "Short-term income drop for long-term gain",
      "New industry salary curve",
    ],
    commonMistakes: [
      "Not having 6+ months expenses saved before switching",
    ],
  },

  start_business: {
    name: "Start a Business",
    questionsToAsk: ["What type?", "Full-time or side?", "Startup capital needed?"],
    typicalCosts: [
      { item: "Startup costs", low: 1000, mid: 10000, high: 100000 },
    ],
    cascadingEffects: [
      "Income becomes variable",
      "Self-employment tax (15.3%)",
      "Need to handle own benefits",
      "Business expenses may be tax deductible",
    ],
    commonMistakes: [
      "Not keeping 12+ months personal expenses saved",
      "Mixing personal and business finances",
    ],
  },

  retirement: {
    name: "Retire",
    questionsToAsk: ["Target age?", "Expected monthly expenses?", "Social Security strategy?"],
    typicalCosts: [],
    cascadingEffects: [
      "Income drops to savings withdrawals + Social Security",
      "Healthcare costs increase dramatically before Medicare (65)",
      "Taxes change significantly",
    ],
    commonMistakes: [
      "Underestimating healthcare costs",
      "Taking Social Security too early",
      "Not accounting for inflation over 20-30 year retirement",
    ],
  },

  custom: {
    name: "Custom Event",
    questionsToAsk: ["Describe the event", "What's the financial impact?", "When would this happen?"],
    typicalCosts: [],
    cascadingEffects: [],
    commonMistakes: [],
  },

  job_loss: {
    name: "Job Loss",
    questionsToAsk: ["Do you have severance?", "Unemployment benefits eligibility?", "How long to find a new job?"],
    typicalCosts: [
      { item: "Income gap (monthly)", low: 3000, mid: 5000, high: 10000 },
      { item: "COBRA health insurance (monthly)", low: 400, mid: 700, high: 1500 },
    ],
    cascadingEffects: [
      "Immediate income loss — emergency fund becomes critical",
      "COBRA is expensive — explore marketplace alternatives",
      "Unemployment benefits cover ~40-50% of salary in most states",
      "May need to pause retirement contributions",
    ],
    commonMistakes: [
      "Not filing for unemployment immediately",
      "Panic-accepting a lower-paying job instead of taking time to find the right fit",
      "Continuing to spend at pre-job-loss levels",
    ],
  },

  move_state: {
    name: "Move to a New State",
    questionsToAsk: ["Which state?", "Job lined up?", "Know the tax implications?"],
    typicalCosts: [
      { item: "Long-distance moving", low: 3000, mid: 7000, high: 15000 },
      { item: "Housing deposit", low: 2000, mid: 5000, high: 10000 },
    ],
    cascadingEffects: [
      "State income tax changes (could save thousands or cost thousands)",
      "Property tax differences",
      "Cost of living shift across all categories",
      "Insurance rates change",
    ],
    commonMistakes: [
      "Not researching state income tax before moving",
      "Underestimating total cost of living difference",
    ],
  },

  sell_home: {
    name: "Sell Home",
    questionsToAsk: ["Current home value?", "Remaining mortgage?", "Timeline?"],
    typicalCosts: [
      { item: "Agent commissions (5-6%)", low: 10000, mid: 20000, high: 40000 },
      { item: "Closing costs", low: 2000, mid: 5000, high: 10000 },
      { item: "Repairs/staging", low: 1000, mid: 5000, high: 15000 },
    ],
    cascadingEffects: [
      "Capital gains tax exclusion ($250K single, $500K married)",
      "Equity becomes available for next purchase or investment",
      "Monthly housing cost changes",
    ],
    commonMistakes: [
      "Not accounting for selling costs (6-10% of sale price)",
      "Over-improving before selling",
    ],
  },

  downsize: {
    name: "Downsize",
    questionsToAsk: ["Current vs target housing cost?", "Selling or renting out current?"],
    typicalCosts: [
      { item: "Moving costs", low: 1000, mid: 3000, high: 8000 },
    ],
    cascadingEffects: [
      "Lower monthly housing costs",
      "Reduced utilities and maintenance",
      "May free up equity for investing",
    ],
    commonMistakes: [
      "Underestimating emotional difficulty of downsizing",
      "Not factoring in costs of the move itself",
    ],
  },

  marriage: {
    name: "Get Married",
    questionsToAsk: ["Combined income?", "Wedding budget?", "Will you merge finances?"],
    typicalCosts: [
      { item: "Wedding", low: 5000, mid: 30000, high: 80000 },
      { item: "Honeymoon", low: 2000, mid: 5000, high: 15000 },
    ],
    cascadingEffects: [
      "Tax filing status changes — could help or hurt",
      "Health insurance — one plan may be cheaper",
      "Combined household reduces per-person living costs",
      "Legal liability for spouse's debt in some states",
    ],
    commonMistakes: [
      "Going into debt for the wedding",
      "Not discussing finances before marriage",
    ],
  },

  divorce: {
    name: "Get Divorced",
    questionsToAsk: ["Contested or amicable?", "Children involved?", "Asset split expectations?"],
    typicalCosts: [
      { item: "Legal fees", low: 3000, mid: 15000, high: 100000 },
      { item: "New housing setup", low: 2000, mid: 5000, high: 15000 },
    ],
    cascadingEffects: [
      "Income effectively halved if single-income household",
      "Asset division — retirement accounts may be split",
      "Alimony and child support obligations",
      "Need own health insurance",
    ],
    commonMistakes: [
      "Not getting independent financial advice",
      "Keeping the house when you can't afford it solo",
    ],
  },

  child_college: {
    name: "Child Goes to College",
    questionsToAsk: ["Public or private?", "In-state or out-of-state?", "529 plan balance?"],
    typicalCosts: [
      { item: "Tuition (annual)", low: 10000, mid: 25000, high: 60000 },
      { item: "Room & board (annual)", low: 8000, mid: 14000, high: 20000 },
    ],
    cascadingEffects: [
      "4-year commitment ($80K-$320K total)",
      "FAFSA and financial aid implications",
      "529 withdrawals are tax-free for qualified expenses",
      "May reduce household expenses as child moves out",
    ],
    commonMistakes: [
      "Co-signing private student loans",
      "Sacrificing retirement savings for tuition",
    ],
  },

  side_hustle: {
    name: "Start a Side Hustle",
    questionsToAsk: ["What type?", "Hours per week?", "Expected monthly income?"],
    typicalCosts: [
      { item: "Startup supplies/tools", low: 100, mid: 500, high: 3000 },
    ],
    cascadingEffects: [
      "Additional income (typically $500-$2,000/month)",
      "Self-employment tax on side income",
      "May be able to deduct home office and supplies",
    ],
    commonMistakes: [
      "Not setting aside 25-30% for taxes",
      "Burning out trying to work two jobs",
    ],
  },

  freelance: {
    name: "Go Freelance",
    questionsToAsk: ["Current salary?", "Freelance rate?", "Pipeline of clients?"],
    typicalCosts: [
      { item: "Health insurance (monthly)", low: 300, mid: 600, high: 1200 },
      { item: "Equipment/software", low: 500, mid: 2000, high: 5000 },
    ],
    cascadingEffects: [
      "Income becomes variable — feast or famine cycles",
      "Self-employment tax (15.3%)",
      "Must handle own health insurance, retirement, taxes",
      "Can deduct business expenses",
    ],
    commonMistakes: [
      "Not having 6-12 months emergency fund",
      "Underpricing services (rule: freelance rate = salary / 1000 as hourly minimum)",
    ],
  },

  car_purchase: {
    name: "Buy a Car",
    questionsToAsk: ["New or used?", "Financing or cash?", "Trade-in value?"],
    typicalCosts: [
      { item: "Purchase price", low: 8000, mid: 28000, high: 55000 },
      { item: "Insurance increase (annual)", low: 200, mid: 600, high: 1500 },
      { item: "Monthly payment", low: 200, mid: 450, high: 800 },
    ],
    cascadingEffects: [
      "Monthly payment added to expenses",
      "Insurance rates change based on vehicle",
      "Depreciation — new cars lose 20% in year one",
    ],
    commonMistakes: [
      "Focusing on monthly payment instead of total cost",
      "Buying more car than you need",
    ],
  },

  car_payoff: {
    name: "Pay Off Car",
    questionsToAsk: ["Remaining balance?", "Monthly payment being freed up?"],
    typicalCosts: [],
    cascadingEffects: [
      "Monthly payment freed up for savings or investing",
      "Can reduce to liability-only insurance on older vehicles",
    ],
    commonMistakes: [
      "Immediately replacing with a new car payment instead of investing the freed-up money",
    ],
  },

  go_carless: {
    name: "Go Car-Free",
    questionsToAsk: ["Public transit access?", "Work-from-home?", "Current car costs?"],
    typicalCosts: [
      { item: "Transit pass (monthly)", low: 50, mid: 100, high: 200 },
    ],
    cascadingEffects: [
      "Eliminates car payment, insurance, gas, maintenance ($500-$1,000/month typical savings)",
      "May limit job opportunities and social activities",
      "Occasional ride-share costs",
    ],
    commonMistakes: [
      "Not testing the lifestyle before selling the car",
    ],
  },

  debt_payoff: {
    name: "Pay Off Debt",
    questionsToAsk: ["Which debt?", "Balance and rate?", "Strategy: lump sum or accelerated?"],
    typicalCosts: [],
    cascadingEffects: [
      "Monthly payment freed up permanently",
      "Credit score improvement",
      "Reduced financial stress",
      "Interest savings compound over time",
    ],
    commonMistakes: [
      "Paying off low-interest debt before high-interest",
      "Depleting emergency fund to pay off debt",
    ],
  },

  take_loan: {
    name: "Take a Loan",
    questionsToAsk: ["Purpose?", "Amount needed?", "Credit score?"],
    typicalCosts: [
      { item: "Origination fees", low: 0, mid: 500, high: 3000 },
    ],
    cascadingEffects: [
      "New monthly payment obligation",
      "Interest costs over the life of the loan",
      "Debt-to-income ratio increases (affects future borrowing)",
    ],
    commonMistakes: [
      "Not shopping multiple lenders",
      "Not reading the fine print on variable rates",
    ],
  },

  refinance: {
    name: "Refinance",
    questionsToAsk: ["Current rate?", "New rate available?", "Remaining balance?", "How long staying?"],
    typicalCosts: [
      { item: "Closing costs", low: 1500, mid: 4000, high: 8000 },
      { item: "Appraisal", low: 300, mid: 500, high: 800 },
    ],
    cascadingEffects: [
      "Lower monthly payment or shorter term",
      "Break-even point: closing costs / monthly savings = months to recoup",
      "May reset amortization schedule",
    ],
    commonMistakes: [
      "Refinancing when you'll move before break-even",
      "Extending the term (lower payment but more total interest)",
    ],
  },

  health_event: {
    name: "Health Event",
    questionsToAsk: ["Expected treatment costs?", "Insurance coverage?", "Ability to work affected?"],
    typicalCosts: [
      { item: "Out-of-pocket maximum", low: 2000, mid: 6000, high: 16000 },
      { item: "Income loss if unable to work", low: 0, mid: 5000, high: 30000 },
    ],
    cascadingEffects: [
      "Medical bills can accumulate quickly",
      "May need to use emergency fund",
      "Disability insurance becomes critical",
      "HSA funds can be used tax-free for medical expenses",
    ],
    commonMistakes: [
      "Not negotiating medical bills (always ask for itemized bill)",
      "Not knowing your out-of-pocket maximum",
    ],
  },

  disability: {
    name: "Disability",
    questionsToAsk: ["Short-term or long-term?", "Disability insurance?", "Can you do modified work?"],
    typicalCosts: [
      { item: "Income reduction (monthly)", low: 1000, mid: 3000, high: 6000 },
    ],
    cascadingEffects: [
      "Income drops to disability benefit level (typically 60% of salary)",
      "May qualify for SSDI",
      "Medical costs increase",
      "May need home modifications",
    ],
    commonMistakes: [
      "Not having disability insurance before it's needed",
      "Not applying for SSDI early (process takes months)",
    ],
  },

  inheritance: {
    name: "Receive Inheritance",
    questionsToAsk: ["Expected amount?", "Cash, property, or investments?", "Tax implications?"],
    typicalCosts: [],
    cascadingEffects: [
      "Inherited IRAs have required distribution rules",
      "Inherited property gets stepped-up cost basis",
      "May trigger estate tax for very large inheritances",
      "Opportunity to pay off debt or invest significantly",
    ],
    commonMistakes: [
      "Lifestyle inflation after receiving inheritance",
      "Not understanding tax rules for inherited retirement accounts",
    ],
  },

  windfall: {
    name: "Receive Windfall",
    questionsToAsk: ["Source?", "Amount?", "One-time or recurring?"],
    typicalCosts: [],
    cascadingEffects: [
      "Tax implications depend on source (lottery, bonus, gift)",
      "Opportunity to accelerate financial goals dramatically",
      "Psychological impact — sudden wealth syndrome is real",
    ],
    commonMistakes: [
      "Spending it all immediately",
      "Not setting aside taxes owed",
      "Telling too many people (social pressure to spend/share)",
    ],
  },

  lawsuit: {
    name: "Legal Settlement",
    questionsToAsk: ["Expected amount?", "Attorney fees?", "Taxable or non-taxable?"],
    typicalCosts: [
      { item: "Attorney fees (contingency)", low: 0, mid: 0, high: 0 },
    ],
    cascadingEffects: [
      "Physical injury settlements are generally tax-free",
      "Punitive damages and interest are taxable",
      "Attorney fees reduce the net amount significantly (33-40%)",
    ],
    commonMistakes: [
      "Not planning for taxes on taxable portions",
      "Spending the settlement without a financial plan",
    ],
  },

  early_retirement: {
    name: "Early Retirement",
    questionsToAsk: ["Target age?", "Annual expenses?", "Healthcare plan before 65?"],
    typicalCosts: [
      { item: "Healthcare (annual, pre-Medicare)", low: 6000, mid: 12000, high: 24000 },
    ],
    cascadingEffects: [
      "Need to bridge gap until Social Security and Medicare",
      "Roth conversion ladder can access retirement funds penalty-free",
      "Rule of 55 for 401k access",
      "Need 25x annual expenses saved (4% rule)",
    ],
    commonMistakes: [
      "Not planning for healthcare costs (the #1 early retirement killer)",
      "Using 4% rule without adjusting for early retirement (may need 3.5%)",
    ],
  },

  semi_retirement: {
    name: "Semi-Retirement",
    questionsToAsk: ["Part-time income expected?", "Target hours per week?", "Which expenses drop?"],
    typicalCosts: [],
    cascadingEffects: [
      "Reduced income supplemented by savings withdrawals",
      "May maintain employer health benefits if working enough hours",
      "Smaller savings draw-down rate extends portfolio life",
    ],
    commonMistakes: [
      "Assuming part-time work will always be available",
      "Not having a backup plan if part-time income drops",
    ],
  },

  education: {
    name: "Go Back to School",
    questionsToAsk: ["Program?", "Full-time or part-time?", "Employer tuition assistance?"],
    typicalCosts: [
      { item: "Tuition (total)", low: 5000, mid: 20000, high: 80000 },
      { item: "Income reduction if part-time work", low: 0, mid: 10000, high: 40000 },
    ],
    cascadingEffects: [
      "Student loan interest is tax-deductible (up to $2,500)",
      "May qualify for education tax credits",
      "Career advancement potential after completion",
    ],
    commonMistakes: [
      "Taking on excessive debt for uncertain ROI",
      "Not exploring employer tuition reimbursement first",
    ],
  },

  certification: {
    name: "Get Certified",
    questionsToAsk: ["Which certification?", "Cost?", "Expected salary bump?"],
    typicalCosts: [
      { item: "Exam + prep materials", low: 200, mid: 1500, high: 5000 },
    ],
    cascadingEffects: [
      "Often the highest ROI education investment",
      "Some employers reimburse certification costs",
      "May open doors to higher-paying roles",
    ],
    commonMistakes: [
      "Getting certifications that don't move the salary needle",
      "Not negotiating a raise after earning the certification",
    ],
  },

  grad_school: {
    name: "Graduate School",
    questionsToAsk: ["MBA, JD, MD, MS, or other?", "Full-time or part-time?", "Funded or self-pay?"],
    typicalCosts: [
      { item: "Tuition (total)", low: 20000, mid: 80000, high: 250000 },
      { item: "Lost income (if full-time)", low: 0, mid: 80000, high: 200000 },
      { item: "Living expenses during school", low: 15000, mid: 30000, high: 50000 },
    ],
    cascadingEffects: [
      "2-7 year income gap or reduction",
      "Significant debt potential",
      "Dramatically higher earning potential in some fields (MD, JD, MBA from top schools)",
      "Opportunity cost is the real cost — not just tuition",
    ],
    commonMistakes: [
      "Not calculating total cost including lost income",
      "Assuming grad school guarantees higher salary (field-dependent)",
      "Not exploring employer-sponsored programs",
    ],
  },
};

// ==========================================
// SIMULATION PROMPT INSTRUCTIONS
// ==========================================

export const FINANCIAL_TWIN_INSTRUCTIONS = `
When running a Financial Twin simulation:

1. IDENTIFY THE SCENARIO — What life event(s) is the user considering?
2. GATHER SPECIFICS — Use the questionsToAsk from LIFE_EVENT_TEMPLATES to fill in details
3. BUILD THE TIMELINE — Project month-by-month financial impact for 1, 3, 5, 10, 20 years
4. COMPARE TO BASELINE — Show the delta vs. changing nothing
5. SURFACE RISKS — What could go wrong? What's the mitigation?
6. FIND THE CASCADE — Every major event triggers secondary effects. Map them all.
7. DELIVER THE VERDICT — One clear sentence: "This decision puts you $X ahead/behind in Y years"

CRITICAL RULES:
- Always show BOTH paths — the user needs to see what happens if they DO and DON'T take action
- Account for cascading effects — a job change isn't just a salary change, it's benefits, commute, taxes
- Use real cost data from LIFE_EVENT_TEMPLATES for typical ranges
- Flag common mistakes — users consistently underestimate certain costs
- Be honest about uncertainty — use probability when events aren't guaranteed
- Never make the decision FOR the user — illuminate the financial reality and let them choose

THE POWER MOVE:
"You're not just asking about moving to Austin. You're asking about a $127,000 decision.
Let me show you exactly how that number breaks down."

Every life decision is secretly a financial decision. The Financial Twin makes the invisible visible.
`;

// ==========================================
// FACTORY
// ==========================================

export function createEmptySimulation(name: string): TwinSimulation {
  const now = new Date().toISOString();
  return {
    id: `sim_${Date.now()}`,
    name,
    createdAt: now,
    events: [],
    baselineSnapshot: {
      monthlyIncome: 0,
      monthlyExpenses: 0,
      totalDebt: 0,
      totalSavings: 0,
      netWorth: 0,
      location: "",
      costOfLivingIndex: 100,
    },
    timeline: [],
    vsBaseline: {
      netWorthDifference5yr: 0,
      netWorthDifference10yr: 0,
      netWorthDifference20yr: 0,
      retirementAgeDifference: 0,
      totalLifetimeEarningsDifference: 0,
      stressIndexComparison: 0,
      verdict: "",
    },
    risks: [],
    summary: "",
    recommendation: "",
    keyInsight: "",
  };
}
