import { NextRequest, NextResponse } from 'next/server';
import { debtSnowballVsAvalanche, generateCharts } from '@/lib/calculators';
import { rateLimit } from '@/lib/rateLimit';

export async function POST(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? 'unknown';
  const rl = rateLimit('calculator', ip, 30, 60_000);
  if (!rl.ok) return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 });

  try {
    const body = await request.json();
    const { debts } = body;
    if (!Array.isArray(debts) || debts.length === 0) {
      return NextResponse.json({ error: 'debts must be a non-empty array' }, { status: 400 });
    }
    const result = debtSnowballVsAvalanche(debts);
    const charts = generateCharts('debt_snowball_vs_avalanche', result);
    return NextResponse.json({ ...result, charts });
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }
}
