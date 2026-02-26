import { NextRequest, NextResponse } from 'next/server';
import { netWorthCalculator, generateCharts } from '@/lib/calculators';

export async function POST(request: NextRequest) {
  const { assets, liabilities } = await request.json();
  const result = netWorthCalculator(assets, liabilities);
  const charts = generateCharts('net_worth_calculator', result);
  return NextResponse.json({ ...result, charts });
}
