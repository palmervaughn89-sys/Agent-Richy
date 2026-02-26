import { NextRequest, NextResponse } from 'next/server';
import {
  routeToAgent,
  findCachedResponse,
  buildFallbackResponse,
  buildStructuredResponse,
  getAgentSystemPrompt,
  determineEmotion,
} from '@/lib/chatEngine';

export async function POST(request: NextRequest) {
  const { message, agent, session_id, skill } = await request.json();

  const agentKey = agent || routeToAgent(message);

  // 1. Check cached responses first
  const cached = findCachedResponse(message);
  if (cached) {
    return NextResponse.json(
      buildStructuredResponse(cached.message, cached.agentKey, cached.emotion),
    );
  }

  // 2. Try Anthropic Claude if configured
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (apiKey) {
    try {
      const systemPrompt = getAgentSystemPrompt(agentKey, skill);

      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify({
          model: process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-20250514',
          max_tokens: 4096,
          system: systemPrompt,
          messages: [{ role: 'user', content: message }],
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const text = data.content?.[0]?.text || '';
        const emotion = determineEmotion(text, agentKey);
        return NextResponse.json(buildStructuredResponse(text, agentKey, emotion));
      }
    } catch (e) {
      console.error('Anthropic error:', e);
    }
  }

  // 3. Fallback to offline response
  const fallback = buildFallbackResponse(message, agentKey);
  return NextResponse.json(buildStructuredResponse(fallback, agentKey, 'friendly'));
}
