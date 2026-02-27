// ==========================================
// FREE GOVERNMENT DATA FEEDS
// ==========================================

export interface EconomicFeed {
  id: string;
  name: string;
  source: string;
  apiType: "fred" | "bls" | "eia" | "bea" | "census" | "treasury" | "web_search";

  // API details
  endpoint?: string;
  seriesId?: string;                       // FRED series ID or BLS series ID
  apiKeyRequired: boolean;
  apiKeyEnvVar?: string;

  // Update schedule
  frequency: "daily" | "weekly" | "biweekly" | "monthly" | "quarterly" | "annual";
  releaseSchedule?: string;                // "Second Tuesday of each month"
  lastKnownValue?: number;
  lastKnownDate?: string;

  // What it means for users
  userImpactCategory: string[];            // Which spending/saving/investing categories this affects
  knowledgeFilesAffected: string[];        // Which of our 19 knowledge files this informs
  capabilitiesAffected: number[];          // Which of our 27 capabilities this powers

  // Correlation chains
  correlations: {
    trigger: string;                       // "When this metric rises above X"
    effect: string;                        // "Expect Y to happen"
    userAction: string;                    // "Tell user to do Z"
    confidence: "high" | "medium" | "low";
    lagTime: string;                       // "2-4 weeks" — how long before the effect manifests
  }[];

  // How Richy fetches this
  fetchMethod: "api_call" | "web_search" | "scheduled_pull";
  searchQuery?: string;                    // If web_search, what to search for
  cacheMinutes: number;                    // How long to cache before re-fetching
}

export const ECONOMIC_FEEDS: EconomicFeed[] = [

  // ==========================================
  // INFLATION & PRICES (affect every user)
  // ==========================================

  {
    id: "cpi_all",
    name: "Consumer Price Index (All Items)",
    source: "Bureau of Labor Statistics",
    apiType: "bls",
    seriesId: "CUSR0000SA0",
    apiKeyRequired: false,
    frequency: "monthly",
    releaseSchedule: "Around 10th-14th of each month for prior month data",
    userImpactCategory: ["all_spending", "budgeting", "savings_real_value"],
    knowledgeFilesAffected: ["economic-reference.json", "bill-benchmarks.json"],
    capabilitiesAffected: [1, 2, 7, 20, 24, 26],
    correlations: [
      {
        trigger: "CPI YoY > 4%",
        effect: "Real purchasing power declining significantly",
        userAction: "Alert user: budget needs inflation adjustment. Suggest TIPS, I-bonds. Push HYSA if savings in low-yield account.",
        confidence: "high",
        lagTime: "Immediate"
      },
      {
        trigger: "CPI YoY declining for 3+ months",
        effect: "Disinflation — prices still rising but slower",
        userAction: "Good news messaging. Purchasing power erosion slowing. May be safe to resume delayed purchases.",
        confidence: "high",
        lagTime: "Immediate"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "current CPI inflation rate year over year latest",
    cacheMinutes: 1440
  },

  {
    id: "cpi_food_home",
    name: "CPI — Food at Home (Groceries)",
    source: "Bureau of Labor Statistics",
    apiType: "bls",
    seriesId: "CUSR0000SAF11",
    apiKeyRequired: false,
    frequency: "monthly",
    userImpactCategory: ["groceries", "meal_planning"],
    knowledgeFilesAffected: ["economic-reference.json", "seasonal-produce.json", "store-rankings.json"],
    capabilitiesAffected: [3, 10, 16, 26],
    correlations: [
      {
        trigger: "Food at home CPI > 5% YoY",
        effect: "Grocery bills rising fast",
        userAction: "Push grocery planner hard. Emphasize store brands (30-40% savings), seasonal produce, and store switching. Calculate exact dollar impact on user's grocery budget.",
        confidence: "high",
        lagTime: "Immediate"
      },
      {
        trigger: "Food at home CPI decelerating while food away stays high",
        effect: "Cooking at home becoming relatively cheaper vs eating out",
        userAction: "Highlight the gap: 'Eating at home saves you ${X} more per month than last year vs dining out'",
        confidence: "high",
        lagTime: "Immediate"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "food at home CPI grocery inflation latest month",
    cacheMinutes: 1440
  },

  {
    id: "cpi_food_away",
    name: "CPI — Food Away From Home (Restaurants)",
    source: "Bureau of Labor Statistics",
    apiType: "bls",
    seriesId: "CUSR0000SEFV",
    apiKeyRequired: false,
    frequency: "monthly",
    userImpactCategory: ["dining_out", "food_delivery"],
    knowledgeFilesAffected: ["economic-reference.json", "bill-benchmarks.json"],
    capabilitiesAffected: [2, 7, 26],
    correlations: [
      {
        trigger: "Restaurant CPI rising faster than grocery CPI",
        effect: "Widening gap makes cooking at home more valuable",
        userAction: "Calculate exact savings: 'Cooking at home vs dining out saves you ${X}/week right now — that gap has grown ${Y}% this year'",
        confidence: "high",
        lagTime: "Immediate"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "restaurant food prices inflation CPI food away from home",
    cacheMinutes: 1440
  },

  {
    id: "cpi_energy",
    name: "CPI — Energy",
    source: "Bureau of Labor Statistics",
    apiType: "bls",
    seriesId: "CUSR0000SA0E",
    apiKeyRequired: false,
    frequency: "monthly",
    userImpactCategory: ["utilities", "gas", "transportation"],
    knowledgeFilesAffected: ["economic-reference.json", "bill-benchmarks.json"],
    capabilitiesAffected: [2, 12, 26],
    correlations: [
      {
        trigger: "Energy CPI rising > 10% YoY",
        effect: "Utility bills and gas costs spiking",
        userAction: "Push bill negotiation for electricity/gas. Suggest thermostat adjustments ($3/degree/month). Recalculate grocery planner multi-store vs single-store threshold based on gas cost.",
        confidence: "high",
        lagTime: "1-2 months for utility bills"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "energy prices CPI electricity natural gas inflation",
    cacheMinutes: 1440
  },

  {
    id: "cpi_medical",
    name: "CPI — Medical Care",
    source: "Bureau of Labor Statistics",
    apiType: "bls",
    seriesId: "CUSR0000SAM",
    apiKeyRequired: false,
    frequency: "monthly",
    userImpactCategory: ["healthcare", "insurance", "prescriptions"],
    knowledgeFilesAffected: ["economic-reference.json", "prescription-savings.json"],
    capabilitiesAffected: [2, 26],
    correlations: [
      {
        trigger: "Medical CPI > 4% YoY",
        effect: "Healthcare costs accelerating",
        userAction: "Push prescription savings programs (GoodRx, Cost Plus). Remind about HSA/FSA tax advantages. Suggest shopping insurance during open enrollment.",
        confidence: "high",
        lagTime: "Immediate for prescriptions, annual for insurance"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "medical care CPI healthcare inflation latest",
    cacheMinutes: 1440
  },

  {
    id: "cpi_shelter",
    name: "CPI — Shelter (Housing)",
    source: "Bureau of Labor Statistics",
    apiType: "bls",
    seriesId: "CUSR0000SAH1",
    apiKeyRequired: false,
    frequency: "monthly",
    userImpactCategory: ["rent", "housing", "mortgage"],
    knowledgeFilesAffected: ["economic-reference.json", "cost-of-living.json", "life-event-costs.json"],
    capabilitiesAffected: [2, 21, 26],
    correlations: [
      {
        trigger: "Shelter CPI decelerating",
        effect: "Rent growth slowing — negotiating power increasing for renters",
        userAction: "If user rents: 'Rent growth is slowing nationally. You have better negotiating leverage at renewal. Use our rent negotiation script.' If user considering buying: update Financial Twin with current rent vs buy math.",
        confidence: "medium",
        lagTime: "CPI shelter lags real-time rents by 6-12 months"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "shelter CPI rent inflation housing costs latest",
    cacheMinutes: 1440
  },

  {
    id: "cpi_apparel",
    name: "CPI — Apparel",
    source: "Bureau of Labor Statistics",
    apiType: "bls",
    seriesId: "CUSR0000SAA",
    apiKeyRequired: false,
    frequency: "monthly",
    userImpactCategory: ["clothing", "shopping"],
    knowledgeFilesAffected: ["economic-reference.json", "seasonal-pricing.json"],
    capabilitiesAffected: [10, 27],
    correlations: [
      {
        trigger: "Apparel CPI negative (deflation)",
        effect: "Clothing prices dropping — good time to buy",
        userAction: "If user has mentioned needing clothing: 'Clothing prices are actually falling right now. Good time to stock up on basics.'",
        confidence: "medium",
        lagTime: "Immediate"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "apparel clothing CPI prices inflation latest",
    cacheMinutes: 1440
  },


  // ==========================================
  // INTEREST RATES (affect borrowing, saving, investing)
  // ==========================================

  {
    id: "fed_funds_rate",
    name: "Federal Funds Rate",
    source: "Federal Reserve via FRED",
    apiType: "fred",
    seriesId: "FEDFUNDS",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "daily",
    userImpactCategory: ["savings_rates", "borrowing_costs", "mortgage", "credit_cards"],
    knowledgeFilesAffected: ["economic-reference.json", "savings-accounts.json", "credit-cards.json", "etf-reference.json"],
    capabilitiesAffected: [1, 2, 17, 20, 21, 26],
    correlations: [
      {
        trigger: "Fed cuts rates",
        effect: "HYSA rates will drop, mortgage rates may drop, bond prices rise",
        userAction: "MULTIPLE ACTIONS: 1) Lock in current HYSA rates with CDs before they drop. 2) If mortgage rate > new market rate by 0.75%+, suggest refinance. 3) Bond allocation may benefit — update allocation mapper. 4) Tell savers: 'HYSA rates are about to drop. Consider locking in a 12-month CD at current rates.'",
        confidence: "high",
        lagTime: "HYSA: 1-4 weeks. Mortgages: 1-8 weeks. CDs: immediate."
      },
      {
        trigger: "Fed raises rates",
        effect: "HYSA rates will rise, borrowing becomes more expensive",
        userAction: "1) Update HYSA recommendations — new higher rates coming. 2) Warn against new variable-rate debt. 3) Push credit card debt payoff harder (rates rising). 4) 'Good news for savers: your HYSA rate is about to go up.'",
        confidence: "high",
        lagTime: "HYSA: 1-4 weeks. Credit cards: 1-2 billing cycles."
      },
      {
        trigger: "Fed holds rates steady",
        effect: "Current rate environment continues",
        userAction: "Stability — good time to make rate-dependent decisions (refinance, open HYSA, lock CD) because rates are predictable near-term.",
        confidence: "high",
        lagTime: "N/A"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "current federal funds rate Fed interest rate decision",
    cacheMinutes: 1440
  },

  {
    id: "mortgage_30yr",
    name: "30-Year Fixed Mortgage Rate",
    source: "Freddie Mac via FRED",
    apiType: "fred",
    seriesId: "MORTGAGE30US",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "weekly",
    releaseSchedule: "Every Thursday",
    userImpactCategory: ["mortgage", "housing", "home_buying"],
    knowledgeFilesAffected: ["economic-reference.json", "life-event-costs.json", "savings-accounts.json"],
    capabilitiesAffected: [2, 20, 21, 26],
    correlations: [
      {
        trigger: "30yr mortgage drops below user's current rate by 0.75%+",
        effect: "Refinancing becomes worthwhile",
        userAction: "Proactive alert: 'Mortgage rates just hit X%. Your rate is Y%. Refinancing could save you ${Z}/month. Want me to calculate the full impact?'",
        confidence: "high",
        lagTime: "Immediate"
      },
      {
        trigger: "30yr mortgage drops below 6%",
        effect: "Housing affordability improving",
        userAction: "For users considering buying: update Financial Twin. 'Mortgage rates just dropped below 6%. On a $350K home, that saves $X/month vs last quarter.'",
        confidence: "high",
        lagTime: "Immediate"
      },
      {
        trigger: "30yr mortgage rises above 7.5%",
        effect: "Housing affordability deteriorating",
        userAction: "For users considering buying: 'Mortgage rates are elevated at X%. Consider: can you wait? Every 1% drop saves ~$200/month on a $350K home. Meanwhile, grow your down payment in a HYSA at Y%.'",
        confidence: "high",
        lagTime: "Immediate"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "current 30 year mortgage rate this week",
    cacheMinutes: 10080
  },

  {
    id: "treasury_10yr",
    name: "10-Year Treasury Yield",
    source: "Federal Reserve via FRED",
    apiType: "fred",
    seriesId: "DGS10",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "daily",
    userImpactCategory: ["bonds", "investing", "mortgage_prediction"],
    knowledgeFilesAffected: ["etf-reference.json", "economic-reference.json"],
    capabilitiesAffected: [9, 15, 17, 26],
    correlations: [
      {
        trigger: "10yr yield > 2yr yield (normal curve)",
        effect: "Economy healthy, bonds function normally",
        userAction: "Standard bond allocation advice. BND/AGG appropriate.",
        confidence: "high",
        lagTime: "N/A"
      },
      {
        trigger: "10yr yield < 2yr yield (inverted curve)",
        effect: "Recession signal — historically precedes recession by 6-18 months",
        userAction: "Increase emergency fund target. Shift allocation slightly more conservative. 'The yield curve is inverted — historically a recession warning sign. Let's make sure your emergency fund is solid.'",
        confidence: "medium",
        lagTime: "6-18 months for recession (if it materializes)"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "10 year treasury yield today",
    cacheMinutes: 1440
  },

  {
    id: "prime_rate",
    name: "Prime Rate",
    source: "Federal Reserve via FRED",
    apiType: "fred",
    seriesId: "DPRIME",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "daily",
    userImpactCategory: ["credit_cards", "heloc", "variable_rate_loans"],
    knowledgeFilesAffected: ["credit-cards.json", "economic-reference.json"],
    capabilitiesAffected: [2, 26],
    correlations: [
      {
        trigger: "Prime rate increases",
        effect: "Credit card APRs increase (most are prime + margin)",
        userAction: "Push credit card debt payoff. 'Your credit card rate just went up. Every $1,000 in balance costs you ${X} more per year. Let's prioritize paying this down.'",
        confidence: "high",
        lagTime: "1-2 billing cycles"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "current prime rate today",
    cacheMinutes: 1440
  },


  // ==========================================
  // ENERGY & GAS (affect daily costs + grocery strategy)
  // ==========================================

  {
    id: "gas_national_avg",
    name: "National Average Gas Price",
    source: "EIA (Energy Information Administration)",
    apiType: "eia",
    endpoint: "https://api.eia.gov/v2/petroleum/pri/gas/data/",
    apiKeyRequired: true,
    apiKeyEnvVar: "EIA_API_KEY",
    frequency: "weekly",
    releaseSchedule: "Every Monday",
    userImpactCategory: ["transportation", "commute", "grocery_strategy"],
    knowledgeFilesAffected: ["economic-reference.json"],
    capabilitiesAffected: [2, 13, 16, 26],
    correlations: [
      {
        trigger: "Gas > $4.00/gallon",
        effect: "Transportation costs elevated",
        userAction: "GROCERY PLANNER ADJUSTMENT: Increase the 'convenience threshold' for multi-store shopping. At $4+/gallon, driving to 3 stores might cost more in gas than the grocery savings. Also: push carpooling, consolidate errands, WFH days if applicable.",
        confidence: "high",
        lagTime: "Immediate"
      },
      {
        trigger: "Gas < $3.00/gallon",
        effect: "Transportation costs low",
        userAction: "GROCERY PLANNER ADJUSTMENT: Lower convenience threshold — multi-store trips are more worthwhile. 'Gas is cheap right now ($X/gallon). That multi-store grocery run I suggested saves you $37 and only costs $3 in gas.'",
        confidence: "high",
        lagTime: "Immediate"
      },
      {
        trigger: "Gas prices trending down for 4+ weeks",
        effect: "Gas station competition increases, road trip costs dropping",
        userAction: "Mention in relevant contexts: commute cost recalculation, road trip vs flight comparison for travel planning.",
        confidence: "medium",
        lagTime: "Immediate"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "national average gas price today per gallon",
    cacheMinutes: 10080
  },

  {
    id: "electricity_price",
    name: "Average Electricity Price (Residential)",
    source: "EIA",
    apiType: "eia",
    apiKeyRequired: false,
    frequency: "monthly",
    userImpactCategory: ["utilities", "bills"],
    knowledgeFilesAffected: ["bill-benchmarks.json", "economic-reference.json"],
    capabilitiesAffected: [2, 7, 12, 26],
    correlations: [
      {
        trigger: "Electricity price rises > 10% YoY",
        effect: "Utility bills spiking",
        userAction: "Push energy-saving recommendations. 'Electric rates are up X% in your area. Each degree on your thermostat = ~$3/month. Smart power strips save $50-100/year. Consider LED bulbs if you haven't switched.'",
        confidence: "high",
        lagTime: "1-2 billing cycles"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "average residential electricity rate per kwh [STATE]",
    cacheMinutes: 43200
  },


  // ==========================================
  // EMPLOYMENT & INCOME (affect earning potential + risk)
  // ==========================================

  {
    id: "unemployment_rate",
    name: "Unemployment Rate",
    source: "Bureau of Labor Statistics",
    apiType: "bls",
    seriesId: "LNS14000000",
    apiKeyRequired: false,
    frequency: "monthly",
    releaseSchedule: "First Friday of each month",
    userImpactCategory: ["job_security", "emergency_fund", "career", "investing_risk"],
    knowledgeFilesAffected: ["economic-reference.json", "life-event-costs.json"],
    capabilitiesAffected: [1, 8, 17, 20, 21, 26],
    correlations: [
      {
        trigger: "Unemployment < 4% (tight labor market)",
        effect: "Workers have leverage — good time to negotiate or switch jobs",
        userAction: "'The job market is strong right now (X% unemployment). This is a good time to: 1) Negotiate a raise (see our script), 2) Explore higher-paying roles, 3) Ask about benefits you're not using.'",
        confidence: "high",
        lagTime: "Immediate"
      },
      {
        trigger: "Unemployment rising for 3+ consecutive months",
        effect: "Job market softening — increased risk",
        userAction: "RISK ADJUSTMENT: 1) Increase emergency fund recommendation from 3 months to 6 months. 2) Shift investing advice slightly more conservative. 3) Wealth Trajectory should widen confidence intervals. 4) 'The job market is softening. Let's make sure your safety net is strong.'",
        confidence: "high",
        lagTime: "Immediate for advice, 3-6 months for personal impact"
      },
      {
        trigger: "Unemployment > 6%",
        effect: "Significant job market weakness",
        userAction: "DEFENSIVE MODE: Push emergency fund, cut discretionary, delay major purchases, avoid new debt. Financial Twin should add job loss scenario automatically.",
        confidence: "high",
        lagTime: "Immediate"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "current unemployment rate latest jobs report",
    cacheMinutes: 43200
  },

  {
    id: "wage_growth",
    name: "Average Hourly Earnings Growth (YoY)",
    source: "Bureau of Labor Statistics",
    apiType: "bls",
    seriesId: "CES0500000003",
    apiKeyRequired: false,
    frequency: "monthly",
    userImpactCategory: ["income", "salary_negotiation", "career"],
    knowledgeFilesAffected: ["economic-reference.json", "negotiation-database.json"],
    capabilitiesAffected: [2, 21, 26],
    correlations: [
      {
        trigger: "Wage growth > CPI (real wages rising)",
        effect: "Workers gaining purchasing power",
        userAction: "'Real wages are rising — your paycheck buys more than last year. Direct the extra purchasing power to savings/debt, not lifestyle inflation.'",
        confidence: "high",
        lagTime: "Immediate"
      },
      {
        trigger: "Wage growth < CPI (real wages falling)",
        effect: "Workers losing purchasing power despite raises",
        userAction: "'Even with raises, inflation is eating into your purchasing power. Time to optimize spending and negotiate harder. Your raise needs to be at least X% to keep up.'",
        confidence: "high",
        lagTime: "Immediate"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "average hourly earnings growth wage growth latest",
    cacheMinutes: 43200
  },


  // ==========================================
  // CONSUMER BEHAVIOR (predict retail pricing)
  // ==========================================

  {
    id: "consumer_confidence",
    name: "Consumer Confidence Index",
    source: "Conference Board via FRED",
    apiType: "fred",
    seriesId: "CSCICP03USM665S",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "monthly",
    releaseSchedule: "Last Tuesday of each month",
    userImpactCategory: ["deal_predictions", "purchase_timing", "retail_pricing"],
    knowledgeFilesAffected: ["economic-reference.json", "seasonal-pricing.json"],
    capabilitiesAffected: [26, 27],
    correlations: [
      {
        trigger: "Consumer confidence declining for 3+ months",
        effect: "Consumers pulling back on spending → retailers will discount to maintain sales",
        userAction: "DEAL PREDICTION ENGINE: Flag categories where consumer spending is weakening. 'Consumer confidence is dropping. Retailers in [category] are likely to offer deeper discounts in coming weeks to attract shoppers. Hold off on that purchase.'",
        confidence: "medium",
        lagTime: "2-6 weeks for retail discounts to appear"
      },
      {
        trigger: "Consumer confidence surging",
        effect: "Consumers spending freely → less incentive for retailers to discount",
        userAction: "'Consumer demand is high right now. Retailers have less reason to discount. If you need something, buy it — prices aren't likely to drop soon.'",
        confidence: "medium",
        lagTime: "Immediate"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "consumer confidence index latest month",
    cacheMinutes: 43200
  },

  {
    id: "retail_sales",
    name: "Retail Sales (Monthly)",
    source: "Census Bureau via FRED",
    apiType: "fred",
    seriesId: "RSXFS",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "monthly",
    releaseSchedule: "Around 15th of each month",
    userImpactCategory: ["deal_predictions", "purchase_timing"],
    knowledgeFilesAffected: ["economic-reference.json", "seasonal-pricing.json"],
    capabilitiesAffected: [26, 27],
    correlations: [
      {
        trigger: "Retail sales declining in a category MoM for 2+ months",
        effect: "Category-specific demand weakening → inventory buildup → discounts coming",
        userAction: "CATEGORY-SPECIFIC DEAL PREDICTION: 'Retail sales in [electronics/apparel/furniture] have dropped for 2 consecutive months. Retailers are likely sitting on excess inventory. Expect deals in 2-4 weeks.'",
        confidence: "medium",
        lagTime: "2-4 weeks"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "retail sales latest month census bureau",
    cacheMinutes: 43200
  },

  {
    id: "personal_savings_rate",
    name: "Personal Savings Rate",
    source: "Bureau of Economic Analysis via FRED",
    apiType: "fred",
    seriesId: "PSAVERT",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "monthly",
    userImpactCategory: ["savings", "wealth_race_benchmarking"],
    knowledgeFilesAffected: ["economic-reference.json"],
    capabilitiesAffected: [1, 20, 22, 26],
    correlations: [
      {
        trigger: "National savings rate < 4%",
        effect: "Most Americans saving very little — user who saves more is ahead",
        userAction: "Wealth Race context: 'The national savings rate is just X%. Your Y% puts you in the top Z% of savers.' Motivational framing.",
        confidence: "high",
        lagTime: "N/A"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "personal savings rate latest month BEA",
    cacheMinutes: 43200
  },


  // ==========================================
  // HOUSING MARKET (affect largest expense)
  // ==========================================

  {
    id: "home_price_index",
    name: "S&P/Case-Shiller Home Price Index",
    source: "S&P via FRED",
    apiType: "fred",
    seriesId: "CSUSHPISA",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "monthly",
    releaseSchedule: "Last Tuesday of each month (2-month lag)",
    userImpactCategory: ["housing", "home_buying", "net_worth"],
    knowledgeFilesAffected: ["cost-of-living.json", "life-event-costs.json", "economic-reference.json"],
    capabilitiesAffected: [20, 21, 26],
    correlations: [
      {
        trigger: "Home prices declining YoY",
        effect: "Buyer's market forming",
        userAction: "For home buyers: 'Home prices are declining in many markets. Your negotiating power is increasing. Financial Twin shows buying now at X% below peak saves you ${Y}.'",
        confidence: "medium",
        lagTime: "Data has 2-month lag. Real-time indicator: inventory months of supply."
      },
      {
        trigger: "Home prices rising > 10% YoY",
        effect: "Housing bubble risk, affordability declining",
        userAction: "For potential buyers: 'Home prices are rising fast. Make sure you're not stretching beyond the 28% rule (housing < 28% of gross income). Consider: at these prices, renting + investing the difference may build more wealth.'",
        confidence: "medium",
        lagTime: "2-month data lag"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "Case Shiller home price index latest year over year change",
    cacheMinutes: 43200
  },

  {
    id: "housing_inventory",
    name: "Housing Inventory (Months of Supply)",
    source: "National Association of Realtors via FRED",
    apiType: "fred",
    seriesId: "MSACSR",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "monthly",
    userImpactCategory: ["housing", "rent_vs_buy"],
    knowledgeFilesAffected: ["economic-reference.json", "life-event-costs.json"],
    capabilitiesAffected: [21, 26],
    correlations: [
      {
        trigger: "Inventory < 4 months (seller's market)",
        effect: "Homes selling fast, less negotiating power for buyers",
        userAction: "For buyers: 'It's a seller's market. Homes are moving fast. Be prepared to act quickly and don't expect major concessions.'",
        confidence: "high",
        lagTime: "Real-time indicator"
      },
      {
        trigger: "Inventory > 6 months (buyer's market)",
        effect: "Homes sitting longer, buyers have leverage",
        userAction: "For buyers: 'Buyer's market! Homes are sitting longer. You have negotiating power — ask for seller concessions, closing cost credits, and take your time.'",
        confidence: "high",
        lagTime: "Real-time indicator"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "housing inventory months supply latest real estate market",
    cacheMinutes: 43200
  },


  // ==========================================
  // MARKET & INVESTING (affect wealth building)
  // ==========================================

  {
    id: "sp500",
    name: "S&P 500 Index",
    source: "Market data",
    apiType: "web_search",
    apiKeyRequired: false,
    frequency: "daily",
    userImpactCategory: ["investing", "retirement", "net_worth"],
    knowledgeFilesAffected: ["etf-reference.json"],
    capabilitiesAffected: [9, 15, 17, 20],
    correlations: [
      {
        trigger: "S&P 500 drops > 10% from recent high (correction)",
        effect: "Stocks on sale — long-term buying opportunity",
        userAction: "For long-term investors: 'The market is down X% from its high. Historically, corrections of this size recover within 12-18 months. If your time horizon is 10+ years, this is a buying opportunity, not a reason to sell. Stay the course with dollar-cost averaging.'",
        confidence: "high",
        lagTime: "Immediate"
      },
      {
        trigger: "S&P 500 drops > 20% (bear market)",
        effect: "Significant decline — emotional pressure to sell",
        userAction: "CRITICAL: Prevent panic selling. 'This is a bear market. They happen roughly every 3-5 years. The average bear market lasts 9 months. Every single one in history has been followed by a recovery. DO NOT sell. If anything, increase your monthly investment.'",
        confidence: "high",
        lagTime: "Immediate"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "S&P 500 today current level year to date return",
    cacheMinutes: 60
  },

  {
    id: "vix",
    name: "VIX (Market Volatility Index)",
    source: "CBOE via market data",
    apiType: "web_search",
    apiKeyRequired: false,
    frequency: "daily",
    userImpactCategory: ["investing", "risk_assessment"],
    knowledgeFilesAffected: ["etf-reference.json", "economic-reference.json"],
    capabilitiesAffected: [9, 15, 17, 26],
    correlations: [
      {
        trigger: "VIX > 30 (high fear)",
        effect: "Market is fearful — historically good buying opportunity",
        userAction: "For investors: 'Market fear is elevated (VIX at X). Warren Buffett's rule: be greedy when others are fearful. If you have a long time horizon, this is historically a good entry point.'",
        confidence: "medium",
        lagTime: "Immediate"
      },
      {
        trigger: "VIX < 15 (low fear / complacency)",
        effect: "Market is calm — potential for sudden volatility",
        userAction: "No immediate action needed but good time to rebalance portfolio and ensure emergency fund is adequate.",
        confidence: "low",
        lagTime: "N/A"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "VIX volatility index today current level",
    cacheMinutes: 60
  },


  // ==========================================
  // TIER 1 LEADING INDICATORS (predict 3-12 months ahead)
  // These are the ones hedge funds and central banks watch
  // ==========================================

  {
    id: "lei",
    name: "Conference Board Leading Economic Index (LEI)",
    source: "Conference Board",
    apiType: "web_search",
    apiKeyRequired: false,
    frequency: "monthly",
    releaseSchedule: "Third week of each month",
    userImpactCategory: ["recession_risk", "all_financial_planning", "emergency_fund", "investing"],
    knowledgeFilesAffected: ["economic-reference.json", "etf-reference.json", "life-event-costs.json"],
    capabilitiesAffected: [1, 8, 9, 15, 17, 20, 21, 22, 26],
    correlations: [
      {
        trigger: "LEI declines YoY by 2% or more for 3+ consecutive months",
        effect: "Recession probability elevated — historically this has preceded most US recessions within 6-12 months",
        userAction: "DEFENSIVE POSTURE: 1) Increase emergency fund target to 6-9 months. 2) Shift investing allocation 5-10% more conservative. 3) Delay major purchases unless necessary. 4) Financial Twin should auto-add recession scenario. 5) Push debt payoff harder. 6) 'Multiple economic signals are weakening. Smart move: build your safety net now while you still can.'",
        confidence: "high",
        lagTime: "6-12 months lead time before recession"
      },
      {
        trigger: "LEI turns positive after prolonged decline",
        effect: "Recovery signal — economy stabilizing",
        userAction: "Cautiously optimistic messaging. 'Economic indicators are improving. Good time to resume paused financial goals and consider increasing investment contributions.'",
        confidence: "medium",
        lagTime: "3-6 months for recovery to be felt"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "Conference Board Leading Economic Index latest release LEI",
    cacheMinutes: 43200
  },

  {
    id: "ism_manufacturing_pmi",
    name: "ISM Manufacturing PMI",
    source: "Institute for Supply Management",
    apiType: "web_search",
    apiKeyRequired: false,
    frequency: "monthly",
    releaseSchedule: "1st business day of each month at 10:00 AM EST",
    userImpactCategory: ["deal_predictions", "investing", "job_market", "purchase_timing"],
    knowledgeFilesAffected: ["economic-reference.json", "seasonal-pricing.json"],
    capabilitiesAffected: [9, 15, 26, 27],
    correlations: [
      {
        trigger: "ISM Manufacturing PMI < 50 for 3+ months (contraction)",
        effect: "Manufacturing sector shrinking — factories cutting orders, may start cutting jobs",
        userAction: "DEAL PREDICTION: 'Manufacturing is contracting. Retailers receiving fewer goods orders = possible inventory buildups ahead = discounts likely in durable goods (appliances, electronics, furniture) in 4-8 weeks.' Also: if user works in manufacturing, push emergency fund.",
        confidence: "high",
        lagTime: "4-8 weeks for retail pricing impact"
      },
      {
        trigger: "ISM Manufacturing New Orders sub-index < 45",
        effect: "Sharp drop in demand — strongest recession signal within ISM data",
        userAction: "This is the most predictive ISM component. When new orders crash, production cuts and layoffs follow in 2-4 months. Defensive financial posture recommended.",
        confidence: "high",
        lagTime: "2-4 months"
      },
      {
        trigger: "ISM Manufacturing PMI < 42.3",
        effect: "Overall GDP is likely contracting — recession territory",
        userAction: "FULL DEFENSIVE MODE. Emergency fund priority. Cut discretionary. Avoid new debt. 'Manufacturing data indicates the overall economy may be contracting. This is a time for financial defense, not offense.'",
        confidence: "high",
        lagTime: "Concurrent — GDP likely already contracting"
      },
      {
        trigger: "ISM Manufacturing PMI crosses above 50 after prolonged contraction",
        effect: "Manufacturing recovering — early expansion signal",
        userAction: "Recovery mode. 'Manufacturing is expanding again. Historically, this precedes broader economic improvement. Good time to resume investing and paused financial goals.'",
        confidence: "medium",
        lagTime: "1-3 months"
      },
      {
        trigger: "ISM Prices Paid sub-index rising above 60",
        effect: "Input costs surging — producer inflation building, will flow to consumer prices in 2-4 months",
        userAction: "EARLY INFLATION WARNING: 'Factory input costs are surging. Consumer prices in [affected categories] are likely to rise in the coming months. Consider stocking up on durable goods at current prices.'",
        confidence: "medium",
        lagTime: "2-4 months for producer costs to reach consumer prices"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "ISM manufacturing PMI latest month new orders prices",
    cacheMinutes: 43200
  },

  {
    id: "ism_services_pmi",
    name: "ISM Services PMI",
    source: "Institute for Supply Management",
    apiType: "web_search",
    apiKeyRequired: false,
    frequency: "monthly",
    releaseSchedule: "3rd business day of each month at 10:00 AM EST",
    userImpactCategory: ["job_market", "service_prices", "dining", "healthcare", "entertainment"],
    knowledgeFilesAffected: ["economic-reference.json", "bill-benchmarks.json"],
    capabilitiesAffected: [2, 7, 26],
    correlations: [
      {
        trigger: "ISM Services PMI < 50 (services contracting)",
        effect: "CRITICAL: Services = 90% of US economy. Contraction here is a massive red flag.",
        userAction: "This is more important than manufacturing PMI because services dominate the economy. If services contract: maximum financial defense. Emergency fund, cut spending, pause non-essential goals.",
        confidence: "high",
        lagTime: "Concurrent — services contraction IS the recession"
      },
      {
        trigger: "ISM Services Employment sub-index < 50",
        effect: "Service sector cutting jobs — since services employ most Americans, this directly threatens users",
        userAction: "Job market warning. Push emergency fund, update resume, network. 'The service sector — where most jobs are — is cutting workers. Make sure your financial safety net is strong.'",
        confidence: "high",
        lagTime: "1-2 months"
      },
      {
        trigger: "ISM Services Prices Paid rising significantly",
        effect: "Service inflation building — rent, healthcare, dining, insurance costs rising",
        userAction: "These are the stickiest prices. 'Service costs are rising: expect higher restaurant bills, insurance premiums, and healthcare costs. Time to renegotiate bills and review subscriptions.'",
        confidence: "high",
        lagTime: "1-3 months"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "ISM services PMI latest month employment prices",
    cacheMinutes: 43200
  },

  {
    id: "initial_jobless_claims",
    name: "Initial Jobless Claims (Weekly)",
    source: "Department of Labor via FRED",
    apiType: "fred",
    seriesId: "ICSA",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "weekly",
    releaseSchedule: "Every Thursday at 8:30 AM EST for the prior week",
    userImpactCategory: ["job_security", "emergency_fund", "recession_risk"],
    knowledgeFilesAffected: ["economic-reference.json"],
    capabilitiesAffected: [1, 8, 20, 21, 22, 26],
    correlations: [
      {
        trigger: "4-week moving average crosses above 250,000",
        effect: "Layoffs accelerating — historically this level signals economic stress",
        userAction: "Early warning. 'Weekly layoff filings are rising. While not yet at crisis levels, this trend bears watching. Good time to ensure your emergency fund has at least 3 months of expenses.'",
        confidence: "medium",
        lagTime: "Leading by 1-3 months"
      },
      {
        trigger: "4-week moving average crosses above 300,000",
        effect: "Significant job losses — recession likely underway or imminent",
        userAction: "URGENT: 'Layoffs have accelerated significantly. Build emergency fund to 6 months. Cut discretionary spending. If your industry is affected, consider diversifying income sources.'",
        confidence: "high",
        lagTime: "Concurrent or slightly leading"
      },
      {
        trigger: "Claims trending down and below 220,000",
        effect: "Labor market very healthy — few layoffs",
        userAction: "Positive signal. Good time for career moves, salary negotiation, job switching.",
        confidence: "high",
        lagTime: "Concurrent"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "initial jobless claims this week weekly unemployment filings",
    cacheMinutes: 10080
  },

  {
    id: "continuing_claims",
    name: "Continuing Jobless Claims",
    source: "Department of Labor via FRED",
    apiType: "fred",
    seriesId: "CCSA",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "weekly",
    releaseSchedule: "Every Thursday (1-week lag behind initial claims)",
    userImpactCategory: ["job_security", "emergency_fund", "recession_risk"],
    knowledgeFilesAffected: ["economic-reference.json"],
    capabilitiesAffected: [1, 8, 20, 21, 26],
    correlations: [
      {
        trigger: "Continuing claims rising steadily for 4+ weeks",
        effect: "People who lost jobs are NOT finding new ones — much more concerning than initial claims alone",
        userAction: "This is the signal that the job market is truly deteriorating, not just seeing temporary layoffs. 'People who are being laid off are having trouble finding new work. The job market is weakening. Let's strengthen your financial position now.'",
        confidence: "high",
        lagTime: "Concurrent — reflects current difficulty of finding work"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "continuing jobless claims this week insured unemployment",
    cacheMinutes: 10080
  },

  {
    id: "yield_curve",
    name: "Yield Curve (10yr Treasury minus 2yr Treasury)",
    source: "Federal Reserve via FRED",
    apiType: "fred",
    seriesId: "T10Y2Y",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "daily",
    userImpactCategory: ["recession_risk", "investing", "bonds", "mortgage_prediction"],
    knowledgeFilesAffected: ["economic-reference.json", "etf-reference.json"],
    capabilitiesAffected: [9, 15, 17, 20, 21, 26],
    correlations: [
      {
        trigger: "Yield curve inverts (10yr < 2yr, spread goes negative)",
        effect: "Historically preceded every US recession since 1955 with 6-24 month lead time. HOWEVER: recent false signal (inverted 2022-2024, no recession). QE may have distorted this indicator.",
        userAction: "DO NOT PANIC. This is a warning sign, not a guarantee. 'The yield curve has inverted — a historically reliable recession signal, though not perfect. It's a reason to be PREPARED, not panicked. Consider: 1) Ensure 6-month emergency fund. 2) Review portfolio allocation. 3) Avoid overextending on new debt.'",
        confidence: "medium",
        lagTime: "6-24 months (wide range, recent unreliability noted)"
      },
      {
        trigger: "Yield curve UN-inverts after prolonged inversion",
        effect: "CAUTION: Counter-intuitively, un-inversion often happens BECAUSE the Fed is cutting rates in response to economic weakness. Recessions often BEGIN after the curve normalizes.",
        userAction: "'The yield curve has normalized, but historically this can happen as the Fed responds to economic weakness. Stay vigilant. This is NOT an all-clear signal.'",
        confidence: "medium",
        lagTime: "0-6 months after un-inversion"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "yield curve 10 year 2 year treasury spread today inverted",
    cacheMinutes: 1440
  },

  {
    id: "sahm_rule",
    name: "Sahm Rule Recession Indicator",
    source: "Claudia Sahm / Federal Reserve via FRED",
    apiType: "fred",
    seriesId: "SAHMREALTIME",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "monthly",
    releaseSchedule: "With monthly jobs report (first Friday)",
    userImpactCategory: ["recession_risk", "all_financial_planning"],
    knowledgeFilesAffected: ["economic-reference.json"],
    capabilitiesAffected: [1, 8, 17, 20, 21, 22, 26],
    correlations: [
      {
        trigger: "Sahm Rule indicator >= 0.50 (triggered)",
        effect: "In every recession since 1960, the Sahm Rule was triggered by month 4. HOWEVER: false-triggered in summer 2024 due to immigration-driven labor supply increase, not demand weakness. Context matters.",
        userAction: "MAJOR ALERT but with context: 'The Sahm Rule recession indicator has triggered. Historically, this has been extremely accurate. However, context matters — check if unemployment is rising due to layoffs (bad) or new workers entering the market (less bad). Either way: maximize emergency fund, review spending, ensure portfolio matches your risk tolerance.'",
        confidence: "high",
        lagTime: "Concurrent — indicates recession likely in progress"
      },
      {
        trigger: "Sahm Rule indicator between 0.30 and 0.49 (approaching threshold)",
        effect: "Getting close to trigger — watch closely",
        userAction: "Early warning. 'Unemployment is trending upward. Not yet at recession levels, but the trend matters. This is a good time to prepare: review emergency fund, identify expenses to cut if needed.'",
        confidence: "medium",
        lagTime: "1-3 months if trend continues"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "Sahm rule recession indicator current value latest",
    cacheMinutes: 43200
  },

  {
    id: "building_permits",
    name: "Building Permits (New Private Housing)",
    source: "Census Bureau via FRED",
    apiType: "fred",
    seriesId: "PERMIT",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "monthly",
    releaseSchedule: "Around 17th of each month",
    userImpactCategory: ["housing", "construction_jobs", "home_buying"],
    knowledgeFilesAffected: ["economic-reference.json", "life-event-costs.json", "cost-of-living.json"],
    capabilitiesAffected: [20, 21, 26],
    correlations: [
      {
        trigger: "Building permits declining > 10% YoY",
        effect: "Future housing supply shrinking — could push prices/rents up in 12-18 months. Also a leading recession indicator (LEI component).",
        userAction: "For renters: 'New housing construction is slowing. If you're considering moving, locking in a lease now may be wise — supply tightening could push rents up next year.' For buyers: 'Fewer new homes being built means less competition from new construction. Existing home prices could firm up.'",
        confidence: "medium",
        lagTime: "12-18 months for housing supply impact"
      },
      {
        trigger: "Building permits increasing > 10% YoY",
        effect: "More housing coming — future supply increase could moderate price growth",
        userAction: "For buyers considering waiting: 'Construction is ramping up. More housing supply coming online in 12-18 months could moderate price growth.'",
        confidence: "medium",
        lagTime: "12-18 months"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "building permits new housing latest month census",
    cacheMinutes: 43200
  },

  {
    id: "hy_credit_spreads",
    name: "High-Yield Corporate Credit Spreads",
    source: "ICE BofA via FRED",
    apiType: "fred",
    seriesId: "BAMLH0A0HYM2",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "daily",
    userImpactCategory: ["recession_risk", "investing", "credit_availability"],
    knowledgeFilesAffected: ["economic-reference.json", "etf-reference.json"],
    capabilitiesAffected: [9, 15, 17, 26],
    correlations: [
      {
        trigger: "High-yield spreads widen above 500 basis points (5%)",
        effect: "Financial stress rising — investors demanding significant premium for risk. Credit tightening likely. This preceded the 2008 crisis, 2020 crash, and every other major downturn.",
        userAction: "FINANCIAL STRESS ALERT: 'Credit markets are showing stress. When investors demand more to lend to companies, it often means: 1) Borrowing gets harder for businesses → hiring slows. 2) Stock market volatility increases. 3) This is a time to be defensive. Ensure emergency fund is full. Avoid speculative investments.'",
        confidence: "high",
        lagTime: "1-4 months (credit stress flows to economy quickly)"
      },
      {
        trigger: "High-yield spreads widen above 800 basis points",
        effect: "SEVERE financial stress — last seen in 2008 and March 2020. Credit markets seizing up.",
        userAction: "MAXIMUM DEFENSE. But also: historically, buying stocks when credit spreads are this extreme has been one of the best long-term entry points. 'Credit markets are showing severe stress. For your emergency fund: ensure 6-9 months. For your investments: if you can stomach volatility, history shows these extremes are often incredible long-term buying opportunities.'",
        confidence: "high",
        lagTime: "Concurrent — crisis conditions"
      },
      {
        trigger: "High-yield spreads below 300 basis points",
        effect: "Maximum complacency — investors not pricing in much risk. This is normal in strong economies but also seen before corrections.",
        userAction: "No alarm, but a good time to rebalance and ensure portfolio isn't overweighted to risky assets. 'Markets are calm and investors are confident. Good time to review your portfolio allocation.'",
        confidence: "low",
        lagTime: "N/A — not directly predictive"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "high yield credit spread OAS BofA current level",
    cacheMinutes: 1440
  },

  {
    id: "michigan_sentiment",
    name: "University of Michigan Consumer Sentiment",
    source: "University of Michigan via FRED",
    apiType: "fred",
    seriesId: "UMCSENT",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "monthly",
    releaseSchedule: "Preliminary: 2nd Friday. Final: 4th Friday.",
    userImpactCategory: ["deal_predictions", "consumer_spending", "retail_pricing"],
    knowledgeFilesAffected: ["economic-reference.json", "seasonal-pricing.json"],
    capabilitiesAffected: [22, 26, 27],
    correlations: [
      {
        trigger: "Consumer sentiment drops below 60 (recessionary levels)",
        effect: "Consumers are deeply pessimistic — will pull back spending sharply. Retailers will be desperate to move inventory.",
        userAction: "MAJOR DEAL PREDICTION SIGNAL: 'Consumer sentiment has crashed to recessionary levels. When consumers feel this bad, they stop buying. Retailers respond with aggressive discounts to move inventory. If you can wait 4-6 weeks on big purchases, significant deals are coming.' Also: validate user's feelings. 'If you're feeling financially stressed right now, you're not alone.'",
        confidence: "high",
        lagTime: "2-6 weeks for retail discounting response"
      },
      {
        trigger: "Michigan inflation expectations (1-year) above 4%",
        effect: "Consumers expect prices to keep rising — may front-load purchases, creating short-term demand surge then pullback",
        userAction: "Nuanced: 'Consumers expect inflation to stay high. This sometimes creates a rush to buy now (pushing prices temporarily higher) followed by a spending hangover. For non-urgent purchases, patience may pay off.'",
        confidence: "medium",
        lagTime: "1-3 months"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "University of Michigan consumer sentiment index latest preliminary",
    cacheMinutes: 20160
  },

  {
    id: "nonfarm_payrolls",
    name: "Nonfarm Payrolls (Monthly Jobs Report)",
    source: "Bureau of Labor Statistics",
    apiType: "bls",
    seriesId: "CES0000000001",
    apiKeyRequired: false,
    frequency: "monthly",
    releaseSchedule: "First Friday of each month at 8:30 AM EST",
    userImpactCategory: ["job_market", "career", "salary_negotiation", "emergency_fund"],
    knowledgeFilesAffected: ["economic-reference.json", "negotiation-database.json"],
    capabilitiesAffected: [2, 8, 20, 21, 22, 26],
    correlations: [
      {
        trigger: "Monthly job gains below 100,000 for 3+ months",
        effect: "Hiring has stalled — economy not creating enough jobs to absorb new workers",
        userAction: "Job market is soft. 'Hiring has slowed significantly. If you're employed: this isn't the best time for risky career moves unless you have a strong safety net. Focus on making yourself indispensable. If you're job hunting: be prepared for a longer search.'",
        confidence: "high",
        lagTime: "Concurrent"
      },
      {
        trigger: "Monthly job gains above 200,000",
        effect: "Strong hiring — workers have leverage",
        userAction: "Opportunity. 'The job market is adding jobs rapidly. You have leverage: consider negotiating a raise, exploring new opportunities, or asking for better benefits.'",
        confidence: "high",
        lagTime: "Concurrent"
      },
      {
        trigger: "Significant negative revision to prior months' data",
        effect: "Economy was weaker than initially reported — revisions matter more than most people realize",
        userAction: "Context. 'The government revised job numbers lower — the economy was adding fewer jobs than reported. Watch for continuation of this trend.'",
        confidence: "medium",
        lagTime: "Revisions reflect past, but pattern predicts future direction"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "nonfarm payrolls jobs report latest month BLS",
    cacheMinutes: 43200
  },

  {
    id: "real_personal_income",
    name: "Real Personal Income (Less Transfers)",
    source: "BEA via FRED",
    apiType: "fred",
    seriesId: "W875RX1",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "monthly",
    userImpactCategory: ["income", "purchasing_power", "wealth_race"],
    knowledgeFilesAffected: ["economic-reference.json"],
    capabilitiesAffected: [2, 22, 25, 26],
    correlations: [
      {
        trigger: "Real personal income declining for 2+ months",
        effect: "Americans are getting poorer in real terms — one of the NBER's primary recession indicators",
        userAction: "This is one of the two most important indicators the NBER uses to declare recessions. If real income is falling: 'Real income is declining — your money buys less even if your paycheck hasn't changed. Time to optimize every dollar. Let's review your spending and find savings.'",
        confidence: "high",
        lagTime: "Concurrent — this IS the recession for most people"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "real personal income less transfers latest month",
    cacheMinutes: 43200
  },

  {
    id: "durable_goods_orders",
    name: "Durable Goods Orders",
    source: "Census Bureau via FRED",
    apiType: "fred",
    seriesId: "DGORDER",
    apiKeyRequired: true,
    apiKeyEnvVar: "FRED_API_KEY",
    frequency: "monthly",
    releaseSchedule: "Around 26th of each month",
    userImpactCategory: ["deal_predictions", "job_market", "investing"],
    knowledgeFilesAffected: ["economic-reference.json", "seasonal-pricing.json"],
    capabilitiesAffected: [26, 27],
    correlations: [
      {
        trigger: "Durable goods orders declining for 3+ months",
        effect: "Businesses are pulling back on big purchases (machinery, equipment, fleets). This is a HARD DATA alternative to ISM survey sentiment. Peaks in durable goods lead recessions by 6-10 months.",
        userAction: "DEAL PREDICTION: When businesses stop buying durable goods, manufacturers have excess inventory they need to move. Consumer durable goods (appliances, cars, electronics) often see discounts 2-4 months later. 'Business orders for durable goods are falling. Consumer prices for big-ticket items may soften in coming months.'",
        confidence: "medium",
        lagTime: "2-4 months for consumer pricing impact, 6-10 months as recession predictor"
      }
    ],
    fetchMethod: "web_search",
    searchQuery: "durable goods orders latest month census bureau",
    cacheMinutes: 43200
  }
];


// ==========================================
// CORRELATION ENGINE — How feeds connect
// ==========================================

export interface CorrelationChain {
  name: string;
  description: string;
  feeds: string[];                         // IDs of feeds involved
  logic: string;                           // The correlation algorithm
  prediction: string;
  userBenefit: string;
  knowledgeFilesUpdated: string[];
}

export const CORRELATION_CHAINS: CorrelationChain[] = [
  {
    name: "Grocery Cost Optimizer",
    description: "Combines food CPI + gas prices + seasonal produce to optimize grocery strategy",
    feeds: ["cpi_food_home", "gas_national_avg"],
    logic: "IF food_cpi_rising AND gas_cheap THEN multi-store_shopping_saves_more. IF food_cpi_rising AND gas_expensive THEN single-store_with_coupons_better. IF food_cpi_stable AND produce_in_season THEN push_seasonal_substitutions.",
    prediction: "Predicts optimal grocery strategy for the current economic conditions",
    userBenefit: "Saves $30-80/month by adapting grocery strategy to real-time conditions",
    knowledgeFilesUpdated: ["store-rankings.json", "seasonal-produce.json"]
  },
  {
    name: "Purchase Timing Predictor",
    description: "Combines consumer confidence + retail sales + category CPI to predict deals",
    feeds: ["consumer_confidence", "retail_sales", "cpi_apparel", "cpi_energy"],
    logic: "IF consumer_confidence_declining AND retail_sales_dropping_in_category THEN predict_discounts_in_2_to_4_weeks. Overlay with seasonal_pricing patterns for confidence boost.",
    prediction: "Predicts when retailers will discount specific product categories",
    userBenefit: "Saves 10-25% on major purchases by timing correctly",
    knowledgeFilesUpdated: ["seasonal-pricing.json"]
  },
  {
    name: "Rate Optimization Cascade",
    description: "Fed funds rate change triggers cascade of savings/borrowing advice",
    feeds: ["fed_funds_rate", "mortgage_30yr", "prime_rate", "treasury_10yr"],
    logic: "WHEN fed_changes_rate: UPDATE savings_account_recommendations, UPDATE mortgage_refinance_threshold, UPDATE credit_card_payoff_urgency, UPDATE bond_allocation_advice, UPDATE CD_lock_in_strategy.",
    prediction: "Predicts optimal savings and borrowing decisions based on rate environment",
    userBenefit: "Captures $200-2,000/year in rate optimization",
    knowledgeFilesUpdated: ["savings-accounts.json", "credit-cards.json", "etf-reference.json", "economic-reference.json"]
  },
  {
    name: "Job Market Risk Adjuster",
    description: "Employment data adjusts risk profiles and emergency fund targets",
    feeds: ["unemployment_rate", "wage_growth"],
    logic: "IF unemployment_rising_3_months: INCREASE emergency_fund_target, DECREASE risk_tolerance_for_investing, FLAG job_loss_scenario_in_financial_twin. IF unemployment_low AND wages_rising: SUGGEST salary_negotiation, INCREASE investment_aggressiveness.",
    prediction: "Adjusts all financial advice based on employment risk",
    userBenefit: "Prevents financial disaster by preparing before job loss",
    knowledgeFilesUpdated: ["economic-reference.json", "life-event-costs.json"]
  },
  {
    name: "Housing Decision Engine",
    description: "Combines mortgage rates + home prices + inventory + rent CPI",
    feeds: ["mortgage_30yr", "home_price_index", "housing_inventory", "cpi_shelter"],
    logic: "CALCULATE monthly_mortgage = median_price * (1-down_pct) * monthly_rate_factor. COMPARE to median_rent. IF mortgage > rent * 1.3 THEN renting_advantage. IF inventory > 6_months THEN buyers_market_bonus. IF rates_dropping THEN wait_signal.",
    prediction: "Tells users whether to buy, rent, wait, or refinance right now",
    userBenefit: "Prevents the single biggest financial mistake most people make (buying at wrong time/price)",
    knowledgeFilesUpdated: ["cost-of-living.json", "life-event-costs.json", "economic-reference.json"]
  },
  {
    name: "Inflation Defense System",
    description: "Category-by-category inflation tracking personalized to user's spending",
    feeds: ["cpi_all", "cpi_food_home", "cpi_food_away", "cpi_energy", "cpi_medical", "cpi_shelter", "cpi_apparel"],
    logic: "FOR each_category: user_monthly_spend * (category_cpi / 100 / 12) = monthly_inflation_cost. SUM all = total_monthly_inflation_impact. IDENTIFY highest_impact_categories. GENERATE targeted_savings_actions for top 3 impact categories.",
    prediction: "Calculates exact dollar impact of inflation on THIS user",
    userBenefit: "Turns abstract 'inflation is 2.8%' into 'inflation costs you $127/month, mostly from groceries and gas'",
    knowledgeFilesUpdated: ["economic-reference.json", "bill-benchmarks.json"]
  },
  {
    name: "Market Mood Translator",
    description: "S&P 500 + VIX + consumer confidence = investing behavior guide",
    feeds: ["sp500", "vix", "consumer_confidence"],
    logic: "IF sp500_correction AND vix_high AND confidence_low THEN maximum_fear = maximum_opportunity. Prevent panic selling. IF sp500_all_time_high AND vix_low AND confidence_high THEN complacency = rebalance_reminder.",
    prediction: "Translates market conditions into plain-language investing guidance",
    userBenefit: "Prevents panic selling (average investor loses 1-2% annually to bad timing decisions)",
    knowledgeFilesUpdated: ["etf-reference.json"]
  },
  {
    name: "Real Wage Calculator",
    description: "Wage growth vs inflation = are you actually getting richer?",
    feeds: ["wage_growth", "cpi_all"],
    logic: "real_wage_growth = nominal_wage_growth - cpi_inflation. IF positive: purchasing_power_growing. IF negative: purchasing_power_shrinking_despite_raises.",
    prediction: "Tells users whether their raise actually made them richer",
    userBenefit: "Context for salary negotiations: 'You need at least a X% raise to keep up with inflation'",
    knowledgeFilesUpdated: ["economic-reference.json"]
  },

  // ==========================================
  // ADVANCED MULTI-INDICATOR PREDICTION ALGORITHMS
  // ==========================================

  {
    name: "Recession Early Warning System",
    description: "Combines the most proven recession predictors into a single probability score",
    feeds: ["lei", "yield_curve", "sahm_rule", "ism_manufacturing_pmi", "initial_jobless_claims", "hy_credit_spreads"],
    logic: `
      SCORE starts at 0 (out of 100 = maximum recession risk):
      
      IF LEI declining YoY > 2% for 3+ months: +25 points
      IF yield curve inverted: +15 points (reduced from historical importance due to recent false signal)
      IF Sahm Rule > 0.30 (approaching trigger): +10 points. IF > 0.50 (triggered): +20 points
      IF ISM Manufacturing PMI < 50 for 3+ months: +15 points. IF < 42.3: +25 points
      IF initial claims 4-week avg > 250K: +10 points. IF > 300K: +20 points
      IF high-yield spreads > 500 bps: +15 points. IF > 800 bps: +25 points
      
      INTERPRETATION:
      0-15: LOW risk — business as usual, grow wealth
      16-35: ELEVATED risk — strengthen safety net, stay invested but cautious
      36-55: HIGH risk — defensive posture, maximize emergency fund, reduce discretionary
      56-75: VERY HIGH risk — recession likely imminent or underway, full defensive mode
      76-100: EXTREME — multiple indicators confirming severe downturn
      
      KEY INSIGHT: No single indicator is reliable alone (even the yield curve had a false signal).
      The power is in CONVERGENCE. When 3+ indicators agree, confidence is very high.
    `,
    prediction: "Probability-weighted recession risk score updated monthly",
    userBenefit: "Know when to shift from 'grow wealth' mode to 'protect wealth' mode BEFORE it's obvious",
    knowledgeFilesUpdated: ["economic-reference.json"]
  },

  {
    name: "Smart Deal Timing Algorithm",
    description: "Uses multiple demand signals to predict when specific product categories will see discounts",
    feeds: ["consumer_confidence", "michigan_sentiment", "retail_sales", "ism_manufacturing_pmi", "durable_goods_orders"],
    logic: `
      FOR each product category (electronics, appliances, furniture, cars, clothing):
      
      1. CHECK seasonal-pricing.json for current month's typical pricing pattern
      2. CHECK consumer confidence and Michigan sentiment — declining = consumers pulling back
      3. CHECK retail sales in this category — declining = inventory building
      4. CHECK ISM manufacturing — sub-50 in relevant sectors = production cuts coming
      5. CHECK durable goods orders — declining = business demand weakening
      
      SCORING:
      - Seasonal pattern says "buy now" (rating 4-5): +20 buy signal
      - Consumer confidence declining 3+ months: +15 wait signal (deals coming)
      - Retail sales declining in category: +20 wait signal (excess inventory)
      - ISM manufacturing contracting: +10 wait signal (less demand pressure)
      - Durable goods declining: +10 wait signal (business pullback)
      
      NET SCORE > +20 buy signal: "BUY NOW — conditions favor current purchase"
      NET SCORE > +20 wait signal: "WAIT — deals likely coming in {2-4 weeks}"
      MIXED SIGNALS: "Current price is fair. No strong reason to wait or rush."
      
      COMBINE with current web search for:
      - Any active sales or promotions
      - Competitor pricing
      - Upcoming known sale events (Prime Day, Black Friday, etc.)
    `,
    prediction: "Product-specific buy/wait recommendations backed by macro + seasonal data",
    userBenefit: "Saves 10-25% on major purchases by knowing WHEN demand is weak and retailers are desperate",
    knowledgeFilesUpdated: ["seasonal-pricing.json"]
  },

  {
    name: "Income & Career Barometer",
    description: "Combines job market data to tell users when they have leverage and when to be cautious",
    feeds: ["unemployment_rate", "initial_jobless_claims", "wage_growth", "nonfarm_payrolls", "ism_services_pmi"],
    logic: `
      WORKER LEVERAGE SCORE (0-100):
      
      Unemployment < 4%: +25 (tight market, workers have power)
      Initial claims < 220K: +15 (very few layoffs)
      Wage growth > CPI: +20 (real wages rising)
      Nonfarm payrolls > 200K/month: +15 (strong hiring)
      ISM Services Employment > 50: +15 (service sector hiring)
      ISM Services Employment < 48: -20 (service sector cutting)
      Unemployment rising 3+ months: -25 (market softening)
      Initial claims > 250K: -20 (layoffs accelerating)
      
      SCORE > 60: "STRONG leverage — negotiate raise, explore opportunities, ask for better benefits"
      SCORE 30-60: "MODERATE — market is balanced, selective opportunities exist"
      SCORE < 30: "CAUTIOUS — focus on job security, build safety net, avoid risky moves"
    `,
    prediction: "Personalized job market assessment and career action advice",
    userBenefit: "Tells users WHEN to ask for a raise (when they have maximum leverage) and when to play defense",
    knowledgeFilesUpdated: ["negotiation-database.json", "economic-reference.json"]
  },

  {
    name: "K-Shaped Economy Detector",
    description: "Detects when economic conditions differ dramatically between income groups — critical for Richy's target demographic",
    feeds: ["sp500", "consumer_confidence", "real_personal_income", "personal_savings_rate", "cpi_food_home", "cpi_shelter"],
    logic: `
      The 2024-2026 economy is K-shaped: top 20% thriving (stock gains, home equity),
      bottom 80% struggling (food inflation, rent pressure, depleted savings).
      
      Research: Dallas Fed found top 20% = 57% of all consumer spending.
      Bloomberg: "bottom half may already be in recession."
      
      DETECT K-shape:
      IF S&P 500 near highs AND consumer confidence below 70 = K-shaped
      IF wage growth < food + shelter CPI = lower-income squeeze
      IF personal savings rate < 4% = consumers depleting buffers
      
      WHEN K-shape detected:
      - Acknowledge reality: "If the economy doesn't feel good to you, your experience is valid. 
        The stock market is up but everyday costs are hitting hard."
      - Shift from 'grow wealth' advice to 'protect and optimize' advice
      - Push hardest-hitting optimizations: grocery savings, bill negotiation, benefits utilization
      - Focus Wealth Race percentile on comparable income brackets, not overall
    `,
    prediction: "Detects economic divergence between wealthy and working-class Americans",
    userBenefit: "Validates user experience and adjusts ALL advice to their actual economic reality, not headline numbers",
    knowledgeFilesUpdated: ["economic-reference.json"]
  }
];


// ==========================================
// DATA FRESHNESS INSTRUCTION FOR RICHY
// ==========================================

export const ECONOMIC_NERVOUS_SYSTEM_PROMPT = `
## Economic Nervous System — How to Use Live Data

You have access to real-time economic data through web search. Here's how to use it:

### ALWAYS SEARCH BEFORE THESE RECOMMENDATIONS:
1. Before recommending a HYSA → search current best rates
2. Before discussing mortgage → search current 30yr rate  
3. Before gas-dependent advice → search current gas prices
4. Before inflation impact calculations → search latest CPI data
5. Before job market advice → search latest unemployment rate
6. Before investment advice → search current S&P 500 and VIX levels
7. Before home buying advice → search current mortgage rates AND housing inventory

### CORRELATION CHAINS TO APPLY:
When you fetch one data point, think about what it implies for related areas:

Fed cuts rates → HYSA rates dropping soon → suggest CDs to lock in
                → mortgage rates may drop → flag refinance opportunity
                → bond prices rising → adjust allocation advice

Gas prices spike → grocery multi-store trips less worthwhile
                 → push single-store + coupon strategy instead
                 → commute costs up → suggest WFH optimization

CPI food rising → push grocery planner harder
               → emphasize store brands and seasonal produce
               → calculate exact dollar impact on user's budget

Unemployment rising → increase emergency fund recommendation
                    → shift investing more conservative
                    → add job loss scenario to Financial Twin

Consumer confidence dropping → retailers will discount
                             → predict deals in struggling categories
                             → tell user to wait on big purchases

### PREDICTION CONFIDENCE LEVELS:
- HIGH: Fed rate → HYSA rate change (direct mechanical relationship)
- HIGH: Gas price → multi-store grocery trip cost (simple math)
- MEDIUM: Consumer confidence drop → retail discounts (historical pattern)
- MEDIUM: Yield curve inversion → recession (6-18 month lag)
- LOW: Single data point → specific stock prediction (never do this)

### NEVER:
- Predict specific stock prices
- Guarantee future economic conditions
- Give false precision ("inflation will be exactly 2.3% next month")
- Use stale data for rate-sensitive decisions (always search)
`;
