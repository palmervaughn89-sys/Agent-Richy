import { NextRequest, NextResponse } from 'next/server';
import { debtSnowballVsAvalanche, generateCharts } from '@/lib/calculators';

export async function POST(request: NextRequest) {
  const { debts } = await request.json();
  const result = debtSnowballVsAvalanche(debts);
  const charts = generateCharts('debt_snowball_vs_avalanche', result);
  return NextResponse.json({ ...result, charts });
}
