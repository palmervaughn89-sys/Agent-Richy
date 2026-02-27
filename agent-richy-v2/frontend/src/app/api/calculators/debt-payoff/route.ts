import { NextRequest, NextResponse } from 'next/server';
import { debtPayoff, generateCharts } from '@/lib/calculators';
import { rateLimit } from '@/lib/rateLimit';

export async function POST(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? 'unknown';
  const rl = rateLimit('calculator', ip, 30, 60_000);
  if (!rl.ok) return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 });

  try {
    const body = await request.json();
    const { balance, apr, monthly_payment } = body;
    if (typeof balance !== 'number' || balance <= 0) {
      return NextResponse.json({ error: 'balance must be a positive number' }, { status: 400 });
    }
    const result = debtPayoff(balance, apr, monthly_payment);
    if ('error' in result) return NextResponse.json(result, { status: 400 });
    const charts = generateCharts('debt_payoff', result);
    return NextResponse.json({ ...result, charts });
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}
