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
  const { message, agent, session_id } = await request.json();

  const agentKey = agent || routeToAgent(message);

  // 1. Check cached responses first
  const cached = findCachedResponse(message);
  if (cached) {
    return NextResponse.json(
      buildStructuredResponse(cached.message, cached.agentKey, cached.emotion),
    );
  }

  // 2. Try OpenAI if configured
  const apiKey = process.env.OPENAI_API_KEY;
  if (apiKey) {
    try {
      const systemPrompt = getAgentSystemPrompt(agentKey);

      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: process.env.OPENAI_MODEL || 'gpt-4o',
          temperature: 0.7,
          max_tokens: 1000,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: message },
          ],
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const text = data.choices?.[0]?.message?.content || '';
        const emotion = determineEmotion(text, agentKey);
        return NextResponse.json(buildStructuredResponse(text, agentKey, emotion));
      }
    } catch (e) {
      console.error('OpenAI error:', e);
    }
  }

  // 3. Fallback to offline response
  const fallback = buildFallbackResponse(message, agentKey);
  return NextResponse.json(buildStructuredResponse(fallback, agentKey, 'friendly'));
}
