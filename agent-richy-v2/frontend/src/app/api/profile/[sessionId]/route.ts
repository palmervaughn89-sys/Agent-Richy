import { NextRequest, NextResponse } from 'next/server';

// In-memory profiles (Vercel serverless = ephemeral, but works for demo)
// For persistence: swap with Vercel KV, Supabase, or Planetscale
const profiles: Record<string, Record<string, unknown>> = {};

function defaultProfile(id: string) {
  return {
    id,
    name: '',
    age: null,
    user_type: 'adult',
    monthly_income: 0,
    monthly_expenses: 0,
    savings_balance: 0,
    emergency_fund: 0,
    credit_score: null,
    debts: {},
    debt_interest_rates: {},
    goals: [],
    risk_tolerance: 'medium',
    experience_level: null,
    employment_status: null,
  };
}

export async function GET(
  _request: NextRequest,
  { params }: { params: { sessionId: string } },
) {
  const sid = params.sessionId;
  if (!profiles[sid]) profiles[sid] = defaultProfile(sid);
  return NextResponse.json(profiles[sid]);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { sessionId: string } },
) {
  const sid = params.sessionId;
  if (!profiles[sid]) profiles[sid] = defaultProfile(sid);
  const body = await request.json();
  Object.assign(profiles[sid], body);
  return NextResponse.json(profiles[sid]);
}

export async function DELETE(
  _request: NextRequest,
  { params }: { params: { sessionId: string } },
) {
  const sid = params.sessionId;
  delete profiles[sid];
  return NextResponse.json({ status: 'deleted' });
}
