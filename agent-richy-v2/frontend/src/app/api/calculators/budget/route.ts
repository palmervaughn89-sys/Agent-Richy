import { NextRequest, NextResponse } from 'next/server';
import { budget503020, generateCharts } from '@/lib/calculators';
import { rateLimit } from '@/lib/rateLimit';

export async function POST(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? 'unknown';
  const rl = rateLimit('calculator', ip, 30, 60_000);
  if (!rl.ok) return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 });

  try {
    const body = await request.json();
    const { monthly_income, current_expenses = null } = body;
    if (typeof monthly_income !== 'number' || monthly_income <= 0) {
      return NextResponse.json({ error: 'monthly_income must be a positive number' }, { status: 400 });
    }
    const result = budget503020(monthly_income, current_expenses);
    const charts = generateCharts('budget_50_30_20', result);
    return NextResponse.json({ ...result, charts });
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}
