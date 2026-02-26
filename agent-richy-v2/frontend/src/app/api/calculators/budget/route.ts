import { NextRequest, NextResponse } from 'next/server';
import { budget503020, generateCharts } from '@/lib/calculators';

export async function POST(request: NextRequest) {
  const { monthly_income, current_expenses = null } = await request.json();
  const result = budget503020(monthly_income, current_expenses);
  const charts = generateCharts('budget_50_30_20', result);
  return NextResponse.json({ ...result, charts });
}
