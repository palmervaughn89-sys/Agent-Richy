import { NextRequest, NextResponse } from 'next/server';
import { savingsGoalTimeline, generateCharts } from '@/lib/calculators';
import { rateLimit } from '@/lib/rateLimit';

export async function POST(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? 'unknown';
  const rl = rateLimit('calculator', ip, 30, 60_000);
  if (!rl.ok) return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 });

  try {
    const body = await request.json();
    const { goal_amount, current_savings = 0, monthly_contribution = 100, annual_return = 0 } = body;
    if (typeof goal_amount !== 'number' || goal_amount <= 0) {
      return NextResponse.json({ error: 'goal_amount must be a positive number' }, { status: 400 });
    }
    const result = savingsGoalTimeline(goal_amount, current_savings, monthly_contribution, annual_return);
    if ('error' in result) return NextResponse.json(result, { status: 400 });
    const charts = generateCharts('savings_goal_timeline', result);
    return NextResponse.json({ ...result, charts });
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}
