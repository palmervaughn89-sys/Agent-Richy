/* ── Financial calculator functions (ported from Python backend) ──────── */

export function compoundInterest(
  principal: number,
  annualRate: number,
  years: number,
  monthlyContribution: number = 0,
) {
  const monthlyRate = annualRate / 100 / 12;
  const months = years * 12;
  const yearByYear: Record<string, number>[] = [];

  let balance = principal;
  let totalContributed = principal;

  for (let month = 1; month <= months; month++) {
    balance = balance * (1 + monthlyRate) + monthlyContribution;
    totalContributed += monthlyContribution;
    if (month % 12 === 0) {
      yearByYear.push({
        year: month / 12,
        balance: Math.round(balance * 100) / 100,
        contributed: Math.round(totalContributed * 100) / 100,
        interest_earned: Math.round((balance - totalContributed) * 100) / 100,
      });
    }
  }

  return {
    final_amount: Math.round(balance * 100) / 100,
    total_contributed: Math.round(totalContributed * 100) / 100,
    total_interest: Math.round((balance - totalContributed) * 100) / 100,
    year_by_year: yearByYear,
  };
}

export function debtPayoff(balance: number, apr: number, monthlyPayment: number) {
  const monthlyRate = apr / 100 / 12;
  let remaining = balance;
  let totalPaid = 0;
  let totalInterest = 0;
  let months = 0;
  const monthByMonth: Record<string, number>[] = [];

  while (remaining > 0.01 && months < 600) {
    const interest = remaining * monthlyRate;
    if (monthlyPayment <= interest) {
      return { error: `Payment too low — doesn't cover interest. Need at least $${(interest + 1).toFixed(2)}/month` };
    }
    const principalPayment = Math.min(monthlyPayment - interest, remaining);
    remaining -= principalPayment;
    totalPaid += monthlyPayment;
    totalInterest += interest;
    months++;

    if (months <= 60 || months % 12 === 0) {
      monthByMonth.push({
        month: months,
        payment: Math.round(monthlyPayment * 100) / 100,
        principal: Math.round(principalPayment * 100) / 100,
        interest: Math.round(interest * 100) / 100,
        remaining: Math.round(Math.max(remaining, 0) * 100) / 100,
      });
    }
  }

  return {
    months_to_payoff: months,
    years_to_payoff: Math.round((months / 12) * 10) / 10,
    total_paid: Math.round(totalPaid * 100) / 100,
    total_interest: Math.round(totalInterest * 100) / 100,
    month_by_month: monthByMonth,
  };
}

export function debtSnowballVsAvalanche(debts: { name: string; balance: number; apr: number; min_payment: number }[]) {
  function simulate(debtsList: typeof debts, sortFn: (a: typeof debts[0], b: typeof debts[0]) => number) {
    const copies = debtsList.map((d) => ({ ...d }));
    copies.sort(sortFn);
    let totalInterest = 0;
    let months = 0;
    const payoffOrder: { name: string; month: number }[] = [];

    while (copies.some((d) => d.balance > 0.01) && months < 600) {
      months++;
      let extra = 0;
      for (const debt of copies) {
        if (debt.balance <= 0.01) {
          extra += debt.min_payment;
          continue;
        }
        const interest = debt.balance * (debt.apr / 100 / 12);
        totalInterest += interest;
        const payment = debt.min_payment + extra;
        extra = 0;
        debt.balance = Math.max(0, debt.balance + interest - payment);
        if (debt.balance <= 0.01) {
          if (!payoffOrder.some((p) => p.name === debt.name)) {
            payoffOrder.push({ name: debt.name, month: months });
          }
        }
      }
    }
    return {
      months,
      years: Math.round((months / 12) * 10) / 10,
      total_interest: Math.round(totalInterest * 100) / 100,
      payoff_order: payoffOrder,
    };
  }

  const snowball = simulate(debts, (a, b) => a.balance - b.balance);
  const avalanche = simulate(debts, (a, b) => b.apr - a.apr);
  const saved = Math.round((snowball.total_interest - avalanche.total_interest) * 100) / 100;

  return {
    snowball,
    avalanche,
    interest_saved_with_avalanche: saved,
    recommendation: saved > 0 ? 'avalanche' : 'snowball',
  };
}

export function emergencyFundStatus(monthlyExpenses: number, currentSavings: number) {
  const monthsCovered = monthlyExpenses > 0 ? currentSavings / monthlyExpenses : 0;
  const target3 = monthlyExpenses * 3;
  const target6 = monthlyExpenses * 6;

  let status: string, message: string;
  if (monthsCovered >= 6) { status = 'excellent'; message = 'Strong emergency fund! Consider investing excess.'; }
  else if (monthsCovered >= 3) { status = 'good'; message = 'Good shape. Try to build toward 6 months.'; }
  else if (monthsCovered >= 1) { status = 'needs_work'; message = 'You have a start — aim for 3 months minimum.'; }
  else { status = 'critical'; message = 'Building an emergency fund should be your top priority.'; }

  return {
    months_covered: Math.round(monthsCovered * 10) / 10,
    current_savings: currentSavings,
    target_3_months: Math.round(target3 * 100) / 100,
    target_6_months: Math.round(target6 * 100) / 100,
    gap_to_3_months: Math.round(Math.max(0, target3 - currentSavings) * 100) / 100,
    gap_to_6_months: Math.round(Math.max(0, target6 - currentSavings) * 100) / 100,
    status,
    message,
  };
}

export function budget503020(monthlyIncome: number, currentExpenses?: Record<string, number>) {
  const recommended = {
    needs: Math.round(monthlyIncome * 0.50 * 100) / 100,
    wants: Math.round(monthlyIncome * 0.30 * 100) / 100,
    savings: Math.round(monthlyIncome * 0.20 * 100) / 100,
  };
  const result: Record<string, unknown> = { monthly_income: monthlyIncome, recommended };

  if (currentExpenses) {
    result.current = currentExpenses;
    const adjustments: Record<string, unknown> = {};
    for (const cat of ['needs', 'wants', 'savings'] as const) {
      const current = currentExpenses[cat] ?? 0;
      const diff = current - recommended[cat];
      adjustments[cat] = {
        current,
        recommended: recommended[cat],
        difference: Math.round(diff * 100) / 100,
        status: diff > 0 ? 'over' : diff < 0 ? 'under' : 'on_track',
      };
    }
    result.adjustments = adjustments;
  }
  return result;
}

export function savingsGoalTimeline(goalAmount: number, currentSavings: number, monthlyContribution: number, annualReturn: number = 0) {
  const remaining = goalAmount - currentSavings;
  if (remaining <= 0) return { already_reached: true, surplus: Math.round(-remaining * 100) / 100 };
  if (monthlyContribution <= 0) return { error: 'Need a positive monthly contribution to reach your goal.' };

  let months: number;
  if (annualReturn === 0) {
    months = Math.ceil(remaining / monthlyContribution);
  } else {
    const r = annualReturn / 100 / 12;
    months = Math.ceil(Math.log(1 + (remaining * r / monthlyContribution)) / Math.log(1 + r));
  }

  return {
    months_to_goal: months,
    years_to_goal: Math.round((months / 12) * 10) / 10,
    total_contributed: Math.round(months * monthlyContribution * 100) / 100,
    goal_amount: goalAmount,
    monthly_contribution: monthlyContribution,
  };
}

export function netWorthCalculator(assets: Record<string, number>, liabilities: Record<string, number>) {
  const totalA = Object.values(assets).reduce((s, v) => s + v, 0);
  const totalL = Object.values(liabilities).reduce((s, v) => s + v, 0);
  const nw = totalA - totalL;
  return {
    assets,
    total_assets: Math.round(totalA * 100) / 100,
    liabilities,
    total_liabilities: Math.round(totalL * 100) / 100,
    net_worth: Math.round(nw * 100) / 100,
    debt_to_asset_ratio: totalA > 0 ? Math.round((totalL / totalA * 100) * 10) / 10 : 0,
  };
}

/* ── Chart generator (ported from Python chart_generator.py) ──────────── */

interface ChartConfig {
  type: string;
  title: string;
  data: Record<string, unknown>[];
  x_key: string;
  y_key: string;
  color: string;
}

export function generateCharts(calcName: string, result: Record<string, unknown>): ChartConfig[] {
  const charts: ChartConfig[] = [];
  if (!result || 'error' in result) return charts;

  if (calcName === 'compound_interest') {
    const yby = result.year_by_year as Record<string, number>[] | undefined;
    if (yby?.length) {
      charts.push({
        type: 'area', title: 'Investment Growth Over Time',
        data: yby.map((i) => ({ year: `Year ${i.year}`, balance: i.balance, contributed: i.contributed, interest: i.interest_earned })),
        x_key: 'year', y_key: 'balance', color: '#10B981',
      });
    }
  } else if (calcName === 'debt_payoff') {
    const mdata = result.month_by_month as Record<string, number>[] | undefined;
    if (mdata?.length) {
      charts.push({
        type: 'line', title: 'Debt Payoff Timeline',
        data: mdata.slice(0, 48).map((i) => ({ month: `Month ${i.month}`, remaining: i.remaining, principal: i.principal, interest: i.interest })),
        x_key: 'month', y_key: 'remaining', color: '#EF4444',
      });
    }
  } else if (calcName === 'debt_snowball_vs_avalanche') {
    const snowball = result.snowball as Record<string, unknown> | undefined;
    const avalanche = result.avalanche as Record<string, unknown> | undefined;
    if (snowball && avalanche) {
      charts.push({
        type: 'bar', title: 'Snowball vs Avalanche Comparison',
        data: [
          { strategy: 'Snowball', months: snowball.months, total_interest: snowball.total_interest },
          { strategy: 'Avalanche', months: avalanche.months, total_interest: avalanche.total_interest },
        ],
        x_key: 'strategy', y_key: 'total_interest', color: '#F59E0B',
      });
    }
  } else if (calcName === 'budget_50_30_20') {
    const rec = result.recommended as Record<string, number> | undefined;
    if (rec) {
      charts.push({
        type: 'pie', title: '50/30/20 Budget Breakdown',
        data: [
          { name: 'Needs (50%)', value: rec.needs },
          { name: 'Wants (30%)', value: rec.wants },
          { name: 'Savings (20%)', value: rec.savings },
        ],
        x_key: 'name', y_key: 'value', color: '#2563EB',
      });
    }
  } else if (calcName === 'emergency_fund_status') {
    charts.push({
      type: 'bar', title: 'Emergency Fund Progress',
      data: [
        { label: 'Current', amount: result.current_savings },
        { label: '3-Month Target', amount: result.target_3_months },
        { label: '6-Month Target', amount: result.target_6_months },
      ],
      x_key: 'label', y_key: 'amount', color: '#8B5CF6',
    });
  } else if (calcName === 'savings_goal_timeline') {
    const goal = result.goal_amount as number;
    const monthly = result.monthly_contribution as number;
    const mos = result.months_to_goal as number;
    if (mos > 0 && monthly > 0) {
      const data: Record<string, unknown>[] = [];
      let running = 0;
      for (let m = 1; m <= Math.min(mos, 60); m++) {
        running += monthly;
        data.push({ month: `Month ${m}`, saved: Math.round(running * 100) / 100, goal });
      }
      charts.push({ type: 'area', title: 'Savings Goal Progress', data, x_key: 'month', y_key: 'saved', color: '#10B981' });
    }
  }

  return charts;
}
