import { NextRequest, NextResponse } from 'next/server';
import { compoundInterest, generateCharts } from '@/lib/calculators';
import { rateLimit } from '@/lib/rateLimit';

export async function POST(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? 'unknown';
  const rl = rateLimit('calculator', ip, 30, 60_000);
  if (!rl.ok) return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 });

  try {
    const body = await request.json();
    const { principal, annual_rate = 8, years = 30, monthly_contribution = 0 } = body;
    if (typeof principal !== 'number' || principal < 0) {
      return NextResponse.json({ error: 'principal must be a non-negative number' }, { status: 400 });
    }
    const result = compoundInterest(principal, annual_rate, years, monthly_contribution);
    const charts = generateCharts('compound_interest', result);
    return NextResponse.json({ ...result, charts });
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}
