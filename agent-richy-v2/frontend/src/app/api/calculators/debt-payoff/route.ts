import { NextRequest, NextResponse } from 'next/server';
import { debtPayoff, generateCharts } from '@/lib/calculators';

export async function POST(request: NextRequest) {
  const { balance, apr, monthly_payment } = await request.json();
  const result = debtPayoff(balance, apr, monthly_payment);
  if ('error' in result) return NextResponse.json(result, { status: 400 });
  const charts = generateCharts('debt_payoff', result);
  return NextResponse.json({ ...result, charts });
}
