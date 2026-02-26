import { NextRequest, NextResponse } from 'next/server';
import { emergencyFundStatus, generateCharts } from '@/lib/calculators';

export async function POST(request: NextRequest) {
  const { monthly_expenses, current_savings = 0 } = await request.json();
  const result = emergencyFundStatus(monthly_expenses, current_savings);
  const charts = generateCharts('emergency_fund_status', result);
  return NextResponse.json({ ...result, charts });
}
