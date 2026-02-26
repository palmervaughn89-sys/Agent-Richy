import { NextRequest, NextResponse } from 'next/server';
import { compoundInterest, generateCharts } from '@/lib/calculators';

export async function POST(request: NextRequest) {
  const { principal, annual_rate = 8, years = 30, monthly_contribution = 0 } = await request.json();
  const result = compoundInterest(principal, annual_rate, years, monthly_contribution);
  const charts = generateCharts('compound_interest', result);
  return NextResponse.json({ ...result, charts });
}
