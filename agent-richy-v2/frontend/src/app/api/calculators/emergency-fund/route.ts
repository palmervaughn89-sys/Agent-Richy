import { NextRequest, NextResponse } from 'next/server';
import { emergencyFundStatus, generateCharts } from '@/lib/calculators';
import { rateLimit } from '@/lib/rateLimit';

export async function POST(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? 'unknown';
  const rl = rateLimit('calculator', ip, 30, 60_000);
  if (!rl.ok) return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 });

  try {
    const body = await request.json();
    const { monthly_expenses, current_savings = 0 } = body;
    if (typeof monthly_expenses !== 'number' || monthly_expenses <= 0) {
      return NextResponse.json({ error: 'monthly_expenses must be a positive number' }, { status: 400 });
    }
    const result = emergencyFundStatus(monthly_expenses, current_savings);
    const charts = generateCharts('emergency_fund_status', result);
    return NextResponse.json({ ...result, charts });
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}
