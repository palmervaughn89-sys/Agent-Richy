/* ── Wealth Trajectory — Long-Range Financial Projection Engine ──── */

import type { FinancialDNA } from "./financialDNA";

// ==========================================
// WEALTH PROJECTION
// ==========================================

export interface WealthProjection {
  userId: string;
  generatedAt: string;
  basedOn: string; // "Your current financial DNA as of Feb 2026"

  // Current snapshot
  currentNetWorth: number;
  currentMonthlySurplus: number;
  currentSavingsRate: number;

  // Projections at different timeframes
  projections: {
    years: number;
    scenarios: {
      name: "current_path" | "optimized" | "aggressive";
      netWorth: number;
      totalSaved: number;
      totalInvested: number;
      investmentGrowth: number;
      totalDebtRemaining: number;
      passiveIncome: number; // From dividends/interest at that point
      financialIndependenceProgress: number; // % toward FI (expenses covered by passive income)
      monthlySurplus: number;
      assumptions: string[];
    }[];
  }[];

  // Milestones
  milestones: {
    name: string; // "Debt free", "6-month emergency fund", "$100K net worth", "Financial independence"
    currentPathDate: string;
    optimizedPathDate: string;
    timeSavedByOptimizing: number; // Months
  }[];

  // The big number
  retirementProjection: {
    currentPathRetirementAge: number;
    optimizedPathRetirementAge: number;
    retirementSavingsAtCurrentPath: number;
    retirementSavingsOptimized: number;
    monthlyRetirementIncome: number; // Using 4% rule
    socialSecurityEstimate: number;
    gap: number; // Shortfall or surplus
  };

  // Action impact
  topActions: {
    action: string;
    monthlyImpact: number;
    tenYearImpact: number; // Compounded impact over 10 years
    retirementImpact: number; // How much this adds to retirement
  }[];

  // Peer comparison (anonymized)
  peerComparison: {
    metric: string;
    userValue: number;
    peerMedian: number;
    percentile: number;
  }[];
}

// ==========================================
// PROMPT INSTRUCTIONS
// ==========================================

export const WEALTH_TRAJECTORY_INSTRUCTIONS = `
When generating wealth projections:

THREE SCENARIOS:
1. "Current Path" — user changes nothing
2. "Optimized" — user implements all recommended spending optimizations
3. "Aggressive" — user maximizes savings rate (cuts all discretionary, side income)

COMPOUND EVERYTHING:
- Investment returns: use 7% real return (10% nominal - 3% inflation)
- Debt interest: use actual rates
- Salary growth: assume 3% annual raises
- Inflation: 3% on expenses
- Show the DRAMATIC difference between scenarios over 10-20-30 years

THE HOOK:
"The difference between your current path and the optimized path is $347/month.
Over 30 years invested at historical market returns, that's $416,000.
That's not a typo. Three hundred and forty-seven dollars a month becomes
four hundred sixteen thousand dollars. That's the cost of not optimizing."

This is what makes users never leave Richy.
`;

// ==========================================
// CONSTANTS
// ==========================================

const REAL_RETURN = 0.07; // 7% real (10% nominal − 3% inflation)
const NOMINAL_RETURN = 0.10;
const INFLATION = 0.03;
const SALARY_GROWTH = 0.03;
const SAFE_WITHDRAWAL_RATE = 0.04; // 4% rule
const DIVIDEND_YIELD = 0.02; // Rough blended yield for passive income estimate
const PROJECTION_YEARS = [1, 3, 5, 10, 15, 20, 25, 30] as const;

// ==========================================
// MATH HELPERS
// ==========================================

/** Future value of a lump sum. */
function fvLump(pv: number, rate: number, years: number): number {
  return pv * Math.pow(1 + rate, years);
}

/** Future value of a recurring monthly contribution. */
function fvAnnuity(monthlyPmt: number, annualRate: number, years: number): number {
  if (annualRate === 0) return monthlyPmt * 12 * years;
  const r = annualRate / 12;
  const n = years * 12;
  return monthlyPmt * ((Math.pow(1 + r, n) - 1) / r);
}

/** Months until a debt is paid off at a given monthly payment. */
function monthsToPayoff(balance: number, rate: number, payment: number): number {
  if (payment <= 0 || balance <= 0) return Infinity;
  if (rate === 0) return Math.ceil(balance / payment);
  const r = rate / 12;
  if (payment <= balance * r) return Infinity; // Never pays off
  return Math.ceil(-Math.log(1 - (balance * r) / payment) / Math.log(1 + r));
}

/** Remaining debt balance after N months. */
function debtBalanceAfter(balance: number, rate: number, payment: number, months: number): number {
  if (balance <= 0) return 0;
  const r = rate / 12;
  let b = balance;
  for (let m = 0; m < months; m++) {
    b = b * (1 + r) - payment;
    if (b <= 0) return 0;
  }
  return Math.max(0, b);
}

// ==========================================
// SCENARIO BUILDER
// ==========================================

interface ScenarioParams {
  name: "current_path" | "optimized" | "aggressive";
  monthlySurplus: number;
  investRate: number; // % of surplus that goes to investments
  debtExtraPayment: number; // Extra monthly payment toward debt
  assumptions: string[];
}

function buildScenario(
  dna: FinancialDNA,
  params: ScenarioParams,
  years: number,
): WealthProjection["projections"][number]["scenarios"][number] {
  const totalMonths = years * 12;

  // Starting values
  const startingInvestments = dna.wealthProfile.totalInvestments;
  const startingSavings = dna.wealthProfile.totalSavings;

  // Monthly flows
  const monthlyToInvest = params.monthlySurplus * params.investRate;
  const monthlyToSave = params.monthlySurplus * (1 - params.investRate);

  // Investment growth (lump + annuity)
  const investedLumpFV = fvLump(startingInvestments, REAL_RETURN, years);
  const investedAnnuityFV = fvAnnuity(monthlyToInvest, REAL_RETURN, years);
  const totalInvested = investedLumpFV + investedAnnuityFV;
  const investmentGrowth = totalInvested - startingInvestments - monthlyToInvest * totalMonths;

  // Savings (low yield, ~0.5% real)
  const totalSaved = startingSavings + monthlyToSave * totalMonths;

  // Debt remaining
  let totalDebtRemaining = 0;
  for (const d of dna.debtProfile.debts) {
    const payment = d.actualPayment + params.debtExtraPayment / Math.max(dna.debtProfile.debts.length, 1);
    totalDebtRemaining += debtBalanceAfter(d.balance, d.interestRate / 100, payment, totalMonths);
  }

  // Net worth
  const netWorth = totalInvested + totalSaved - totalDebtRemaining;

  // Passive income (dividends + interest at that future point)
  const passiveIncome = (totalInvested * DIVIDEND_YIELD) / 12;

  // FI progress: can passive income cover monthly expenses?
  const futureMonthlyExpenses = dna.cashFlow.monthlyExpenses * Math.pow(1 + INFLATION, years);
  const fiProgress = futureMonthlyExpenses > 0
    ? Math.min(100, (passiveIncome / futureMonthlyExpenses) * 100)
    : 0;

  // Future surplus (salary grows, expenses inflate)
  const futureIncome = dna.cashFlow.monthlyIncome * Math.pow(1 + SALARY_GROWTH, years);
  const futureSurplus = futureIncome - futureMonthlyExpenses;

  return {
    name: params.name,
    netWorth: Math.round(netWorth),
    totalSaved: Math.round(totalSaved),
    totalInvested: Math.round(totalInvested),
    investmentGrowth: Math.round(investmentGrowth),
    totalDebtRemaining: Math.round(totalDebtRemaining),
    passiveIncome: Math.round(passiveIncome),
    financialIndependenceProgress: Math.round(fiProgress * 10) / 10,
    monthlySurplus: Math.round(futureSurplus),
    assumptions: params.assumptions,
  };
}

// ==========================================
// MILESTONE CALCULATOR
// ==========================================

function projectMilestones(dna: FinancialDNA, optimizedSurplus: number): WealthProjection["milestones"] {
  const milestones: WealthProjection["milestones"] = [];
  const now = new Date();
  const currentSurplus = dna.cashFlow.monthlySurplus;

  // Debt free
  if (dna.debtProfile.totalDebt > 0) {
    const currentMonths = dna.debtProfile.debts.reduce((worst, d) => {
      const m = monthsToPayoff(d.balance, d.interestRate / 100, d.actualPayment);
      return Math.max(worst, m);
    }, 0);

    const optimizedMonths = dna.debtProfile.debts.reduce((worst, d) => {
      const extra = (optimizedSurplus - currentSurplus) / Math.max(dna.debtProfile.debts.length, 1);
      const m = monthsToPayoff(d.balance, d.interestRate / 100, d.actualPayment + extra);
      return Math.max(worst, m);
    }, 0);

    const currentDate = new Date(now);
    currentDate.setMonth(currentDate.getMonth() + (isFinite(currentMonths) ? currentMonths : 360));
    const optimizedDate = new Date(now);
    optimizedDate.setMonth(optimizedDate.getMonth() + (isFinite(optimizedMonths) ? optimizedMonths : 360));

    milestones.push({
      name: "Debt free",
      currentPathDate: currentDate.toISOString().slice(0, 10),
      optimizedPathDate: optimizedDate.toISOString().slice(0, 10),
      timeSavedByOptimizing: Math.max(0, (isFinite(currentMonths) ? currentMonths : 360) - (isFinite(optimizedMonths) ? optimizedMonths : 360)),
    });
  }

  // 6-month emergency fund
  const targetEF = dna.cashFlow.monthlyExpenses * 6;
  const efShortfall = Math.max(0, targetEF - dna.wealthProfile.emergencyFund.balance);
  if (efShortfall > 0) {
    const currentMonths = currentSurplus > 0 ? Math.ceil(efShortfall / currentSurplus) : 360;
    const optMonths = optimizedSurplus > 0 ? Math.ceil(efShortfall / optimizedSurplus) : 360;

    const cd = new Date(now);
    cd.setMonth(cd.getMonth() + currentMonths);
    const od = new Date(now);
    od.setMonth(od.getMonth() + optMonths);

    milestones.push({
      name: "6-month emergency fund",
      currentPathDate: cd.toISOString().slice(0, 10),
      optimizedPathDate: od.toISOString().slice(0, 10),
      timeSavedByOptimizing: Math.max(0, currentMonths - optMonths),
    });
  }

  // $100K net worth
  const netWorthTarget = 100_000;
  if (dna.wealthProfile.netWorth < netWorthTarget) {
    const gap = netWorthTarget - dna.wealthProfile.netWorth;
    const currentYears = currentSurplus > 0
      ? yearsToReach(gap, currentSurplus, REAL_RETURN)
      : 99;
    const optYears = optimizedSurplus > 0
      ? yearsToReach(gap, optimizedSurplus, REAL_RETURN)
      : 99;

    const cd = new Date(now);
    cd.setFullYear(cd.getFullYear() + Math.ceil(currentYears));
    const od = new Date(now);
    od.setFullYear(od.getFullYear() + Math.ceil(optYears));

    milestones.push({
      name: "$100K net worth",
      currentPathDate: cd.toISOString().slice(0, 10),
      optimizedPathDate: od.toISOString().slice(0, 10),
      timeSavedByOptimizing: Math.max(0, Math.round((currentYears - optYears) * 12)),
    });
  }

  // Financial independence (25× annual expenses)
  const fiTarget = dna.cashFlow.monthlyExpenses * 12 * 25;
  if (dna.wealthProfile.netWorth < fiTarget) {
    const gap = fiTarget - dna.wealthProfile.netWorth;
    const currentYears = currentSurplus > 0
      ? yearsToReach(gap, currentSurplus, REAL_RETURN)
      : 99;
    const optYears = optimizedSurplus > 0
      ? yearsToReach(gap, optimizedSurplus, REAL_RETURN)
      : 99;

    const cd = new Date(now);
    cd.setFullYear(cd.getFullYear() + Math.ceil(currentYears));
    const od = new Date(now);
    od.setFullYear(od.getFullYear() + Math.ceil(optYears));

    milestones.push({
      name: "Financial independence",
      currentPathDate: cd.toISOString().slice(0, 10),
      optimizedPathDate: od.toISOString().slice(0, 10),
      timeSavedByOptimizing: Math.max(0, Math.round((currentYears - optYears) * 12)),
    });
  }

  return milestones;
}

/** Approximate years to reach a wealth target with monthly contributions + growth. */
function yearsToReach(target: number, monthlySurplus: number, annualReturn: number): number {
  if (monthlySurplus <= 0) return 99;
  const r = annualReturn / 12;
  // Solve: monthlySurplus × ((1+r)^n − 1) / r = target
  // n = ln(target × r / monthlySurplus + 1) / ln(1+r)
  const inner = (target * r) / monthlySurplus + 1;
  if (inner <= 0) return 99;
  const months = Math.log(inner) / Math.log(1 + r);
  return Math.min(99, months / 12);
}

// ==========================================
// TOP ACTIONS CALCULATOR
// ==========================================

function computeTopActions(dna: FinancialDNA): WealthProjection["topActions"] {
  const actions: WealthProjection["topActions"] = [];

  // 1. Subscription cuts
  const lowValueSubs = dna.spendingFingerprint.activeSubscriptions.filter(
    (s) => s.valueScore < 50,
  );
  if (lowValueSubs.length > 0) {
    const monthly = lowValueSubs.reduce((s, sub) => s + sub.amount, 0);
    actions.push({
      action: `Cancel ${lowValueSubs.length} low-value subscription${lowValueSubs.length > 1 ? "s" : ""}`,
      monthlyImpact: monthly,
      tenYearImpact: Math.round(fvAnnuity(monthly, NOMINAL_RETURN, 10)),
      retirementImpact: Math.round(fvAnnuity(monthly, NOMINAL_RETURN, 30)),
    });
  }

  // 2. Spending weakness reduction
  for (const w of dna.spendingFingerprint.spendingWeaknesses.slice(0, 3)) {
    if (w.estimatedMonthlyCost > 0) {
      const monthly = Math.round(w.estimatedMonthlyCost * 0.5); // Assume 50% reduction
      actions.push({
        action: `Reduce ${w.category} spending by 50%`,
        monthlyImpact: monthly,
        tenYearImpact: Math.round(fvAnnuity(monthly, NOMINAL_RETURN, 10)),
        retirementImpact: Math.round(fvAnnuity(monthly, NOMINAL_RETURN, 30)),
      });
    }
  }

  // 3. Employer match capture
  for (const acct of dna.wealthProfile.retirementAccounts) {
    if (
      acct.type.toLowerCase().includes("401k") &&
      acct.employerMatch > 0 &&
      acct.monthlyContribution < acct.employerMatch
    ) {
      const monthly = acct.employerMatch - acct.monthlyContribution;
      actions.push({
        action: "Max employer 401(k) match",
        monthlyImpact: monthly,
        tenYearImpact: Math.round(fvAnnuity(monthly, NOMINAL_RETURN, 10)),
        retirementImpact: Math.round(fvAnnuity(monthly, NOMINAL_RETURN, 30)),
      });
    }
  }

  // 4. High-interest debt payoff
  const highInterest = dna.debtProfile.debts.filter((d) => d.interestRate > 10);
  if (highInterest.length > 0) {
    const monthlyInterest = highInterest.reduce(
      (s, d) => s + (d.balance * (d.interestRate / 100)) / 12,
      0,
    );
    actions.push({
      action: "Eliminate high-interest debt",
      monthlyImpact: Math.round(monthlyInterest),
      tenYearImpact: Math.round(fvAnnuity(monthlyInterest, NOMINAL_RETURN, 10)),
      retirementImpact: Math.round(fvAnnuity(monthlyInterest, NOMINAL_RETURN, 30)),
    });
  }

  // Sort by retirement impact descending
  actions.sort((a, b) => b.retirementImpact - a.retirementImpact);
  return actions.slice(0, 5);
}

// ==========================================
// MAIN GENERATOR
// ==========================================

export function generateWealthProjection(dna: FinancialDNA): WealthProjection {
  const currentSurplus = dna.cashFlow.monthlySurplus;
  const topActions = computeTopActions(dna);
  const optimizedExtra = topActions.reduce((s, a) => s + a.monthlyImpact, 0);
  const optimizedSurplus = currentSurplus + optimizedExtra;
  const aggressiveSurplus = dna.cashFlow.monthlyIncome * 0.5; // Save 50% of income

  const age = dna.identity.age ?? 30;
  const retirementAge = 65;
  const yearsToRetirement = Math.max(1, retirementAge - age);

  // Build scenario params
  const scenarioParams: ScenarioParams[] = [
    {
      name: "current_path",
      monthlySurplus: currentSurplus,
      investRate: 0.7,
      debtExtraPayment: 0,
      assumptions: [
        `Monthly surplus: $${Math.round(currentSurplus)}`,
        "70% invested, 30% saved",
        "7% real investment return",
        "3% annual salary growth",
        "3% inflation on expenses",
        "No change to current habits",
      ],
    },
    {
      name: "optimized",
      monthlySurplus: optimizedSurplus,
      investRate: 0.8,
      debtExtraPayment: optimizedExtra * 0.3,
      assumptions: [
        `Monthly surplus: $${Math.round(optimizedSurplus)} (+$${Math.round(optimizedExtra)})`,
        "All recommended optimizations applied",
        "80% invested, 20% saved",
        "Extra debt payments from savings",
        "7% real investment return",
        "3% annual salary growth",
      ],
    },
    {
      name: "aggressive",
      monthlySurplus: aggressiveSurplus,
      investRate: 0.9,
      debtExtraPayment: aggressiveSurplus * 0.2,
      assumptions: [
        `50% savings rate ($${Math.round(aggressiveSurplus)}/mo)`,
        "Maximum discretionary cuts",
        "90% invested, 10% saved",
        "Aggressive debt elimination",
        "7% real investment return",
        "Side income potential not included",
      ],
    },
  ];

  // Projections at each timeframe
  const projections = PROJECTION_YEARS.map((years) => ({
    years,
    scenarios: scenarioParams.map((sp) => buildScenario(dna, sp, years)),
  }));

  // Milestones
  const milestones = projectMilestones(dna, optimizedSurplus);

  // Retirement projection
  const currentRetireSavings = projections.find((p) => p.years >= yearsToRetirement)
    ?.scenarios.find((s) => s.name === "current_path")?.totalInvested ?? 0;
  const optimizedRetireSavings = projections.find((p) => p.years >= yearsToRetirement)
    ?.scenarios.find((s) => s.name === "optimized")?.totalInvested ?? 0;

  const monthlyRetirementIncome = (optimizedRetireSavings * SAFE_WITHDRAWAL_RATE) / 12;
  const socialSecurity = 1900; // Average estimate
  const targetRetirementIncome = dna.cashFlow.monthlyExpenses * Math.pow(1 + INFLATION, yearsToRetirement);
  const gap = monthlyRetirementIncome + socialSecurity - targetRetirementIncome;

  // Optimized retirement age: when does FI progress hit 100%?
  let optimizedRetirementAge = retirementAge;
  for (const p of projections) {
    const opt = p.scenarios.find((s) => s.name === "optimized");
    if (opt && opt.financialIndependenceProgress >= 100) {
      optimizedRetirementAge = Math.min(optimizedRetirementAge, age + p.years);
      break;
    }
  }

  // Peer comparison
  const peerComparison = buildPeerComparison(dna);

  return {
    userId: dna.userId,
    generatedAt: new Date().toISOString(),
    basedOn: `Your current financial DNA as of ${new Date().toLocaleDateString("en-US", { month: "short", year: "numeric" })}`,
    currentNetWorth: dna.wealthProfile.netWorth,
    currentMonthlySurplus: currentSurplus,
    currentSavingsRate: dna.wealthProfile.savingsRate,
    projections,
    milestones,
    retirementProjection: {
      currentPathRetirementAge: retirementAge,
      optimizedPathRetirementAge: optimizedRetirementAge,
      retirementSavingsAtCurrentPath: Math.round(currentRetireSavings),
      retirementSavingsOptimized: Math.round(optimizedRetireSavings),
      monthlyRetirementIncome: Math.round(monthlyRetirementIncome),
      socialSecurityEstimate: socialSecurity,
      gap: Math.round(gap),
    },
    topActions,
    peerComparison,
  };
}

// ==========================================
// PEER COMPARISON (stub — real data comes from aggregated platform)
// ==========================================

function buildPeerComparison(dna: FinancialDNA): WealthProjection["peerComparison"] {
  // In production, these medians come from aggregated PlatformIntelligence.
  // For now, use age-bucketed national averages as proxies.
  const age = dna.identity.age ?? 30;

  // Rough US median benchmarks by age bracket
  const medians: Record<string, number> = age < 35
    ? { netWorth: 39_000, savingsRate: 8, debtToIncome: 21, emergencyMonths: 1.5 }
    : age < 45
      ? { netWorth: 135_000, savingsRate: 10, debtToIncome: 18, emergencyMonths: 2.5 }
      : age < 55
        ? { netWorth: 247_000, savingsRate: 12, debtToIncome: 15, emergencyMonths: 3 }
        : { netWorth: 364_000, savingsRate: 15, debtToIncome: 10, emergencyMonths: 4 };

  function percentile(user: number, median: number): number {
    if (median === 0) return 50;
    const ratio = user / median;
    return Math.min(99, Math.max(1, Math.round(50 * (1 + Math.log2(Math.max(0.01, ratio))))));
  }

  return [
    {
      metric: "Net worth",
      userValue: dna.wealthProfile.netWorth,
      peerMedian: medians.netWorth,
      percentile: percentile(dna.wealthProfile.netWorth, medians.netWorth),
    },
    {
      metric: "Savings rate",
      userValue: dna.wealthProfile.savingsRate,
      peerMedian: medians.savingsRate,
      percentile: percentile(dna.wealthProfile.savingsRate, medians.savingsRate),
    },
    {
      metric: "Debt-to-income",
      userValue: dna.debtProfile.debtToIncomeRatio,
      peerMedian: medians.debtToIncome,
      // Lower is better for DTI, so invert
      percentile: percentile(medians.debtToIncome, Math.max(1, dna.debtProfile.debtToIncomeRatio)),
    },
    {
      metric: "Emergency fund (months)",
      userValue: dna.wealthProfile.emergencyFund.monthsCovered,
      peerMedian: medians.emergencyMonths,
      percentile: percentile(dna.wealthProfile.emergencyFund.monthsCovered, medians.emergencyMonths),
    },
  ];
}

// ==========================================
// UTILITY — Create empty projection shell
// ==========================================

export function createEmptyProjection(userId: string): WealthProjection {
  return {
    userId,
    generatedAt: new Date().toISOString(),
    basedOn: "Insufficient data — start a conversation to build your Financial DNA",
    currentNetWorth: 0,
    currentMonthlySurplus: 0,
    currentSavingsRate: 0,
    projections: [],
    milestones: [],
    retirementProjection: {
      currentPathRetirementAge: 65,
      optimizedPathRetirementAge: 65,
      retirementSavingsAtCurrentPath: 0,
      retirementSavingsOptimized: 0,
      monthlyRetirementIncome: 0,
      socialSecurityEstimate: 1900,
      gap: 0,
    },
    topActions: [],
    peerComparison: [],
  };
}
