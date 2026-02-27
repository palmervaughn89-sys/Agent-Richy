import { NextRequest, NextResponse } from 'next/server';
import { netWorthCalculator, generateCharts } from '@/lib/calculators';
import { rateLimit } from '@/lib/rateLimit';

export async function POST(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? 'unknown';
  const rl = rateLimit('calculator', ip, 30, 60_000);
  if (!rl.ok) return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 });

  try {
    const body = await request.json();
    const { assets, liabilities } = body;
    if (typeof assets !== 'object' || typeof liabilities !== 'object') {
      return NextResponse.json({ error: 'assets and liabilities must be objects' }, { status: 400 });
    }
    const result = netWorthCalculator(assets, liabilities);
    const charts = generateCharts('net_worth_calculator', result);
    return NextResponse.json({ ...result, charts });
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}
