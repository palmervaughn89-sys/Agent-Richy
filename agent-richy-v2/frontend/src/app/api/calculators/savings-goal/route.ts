import { NextRequest, NextResponse } from 'next/server';
import { savingsGoalTimeline, generateCharts } from '@/lib/calculators';

export async function POST(request: NextRequest) {
  const { goal_amount, current_savings = 0, monthly_contribution = 100, annual_return = 0 } = await request.json();
  const result = savingsGoalTimeline(goal_amount, current_savings, monthly_contribution, annual_return);
  if ('error' in result) return NextResponse.json(result, { status: 400 });
  const charts = generateCharts('savings_goal_timeline', result);
  return NextResponse.json({ ...result, charts });
}
