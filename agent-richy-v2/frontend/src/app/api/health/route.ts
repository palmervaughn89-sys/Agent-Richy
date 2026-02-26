import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    llm_configured: !!process.env.OPENAI_API_KEY,
    agents_available: 6,
  });
}
