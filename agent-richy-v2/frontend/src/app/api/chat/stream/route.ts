import { NextRequest, NextResponse } from 'next/server';
import {
  routeToAgent,
  findCachedResponse,
  buildFallbackResponse,
  buildStructuredResponse,
  getAgentSystemPrompt,
  determineEmotion,
} from '@/lib/chatEngine';
import { rateLimit } from '@/lib/rateLimit';

export const runtime = 'nodejs';

interface HistoryMessage {
  role: 'user' | 'assistant';
  content: string;
}

export async function POST(request: NextRequest) {
  // Rate limit: 10 requests per minute for chat
  const ip = request.headers.get('x-forwarded-for') ?? request.headers.get('x-real-ip') ?? 'unknown';
  const rl = rateLimit('chat', ip, 10, 60_000);
  if (!rl.ok) {
    return NextResponse.json(
      { error: 'Too many requests. Please wait a moment.' },
      { status: 429, headers: { 'Retry-After': String(Math.ceil(rl.retryAfterMs / 1000)) } },
    );
  }

  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
  }

  const { message, agent, skill, messages: history } = body as {
    message?: string;
    agent?: string;
    skill?: string;
    messages?: HistoryMessage[];
  };

  if (!message || typeof message !== 'string') {
    return NextResponse.json({ error: 'message is required' }, { status: 400 });
  }

  const agentKey = (agent as string) || routeToAgent(message);

  // Build Anthropic messages array — include conversation history if provided
  const anthropicMessages: { role: string; content: string }[] = [];
  if (Array.isArray(history) && history.length > 0) {
    // Include up to last 20 turns for context window management
    const recent = history.slice(-20);
    for (const m of recent) {
      if (m.role === 'user' || m.role === 'assistant') {
        anthropicMessages.push({ role: m.role, content: m.content });
      }
    }
  }
  // Always ensure the current message is the last user message
  if (!anthropicMessages.length || anthropicMessages[anthropicMessages.length - 1].content !== message) {
    anthropicMessages.push({ role: 'user', content: message });
  }

  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      function sendEvent(data: string) {
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
      }

      // 1. Check cached responses (only for first message / no history)
      if (anthropicMessages.length <= 1) {
        const cached = findCachedResponse(message);
        if (cached) {
          const words = cached.message.split(' ');
          for (let i = 0; i < words.length; i += 3) {
            const chunk = words.slice(i, i + 3).join(' ') + ' ';
            sendEvent(JSON.stringify({ type: 'token', content: chunk }));
          }
          const resp = buildStructuredResponse(cached.message, cached.agentKey, cached.emotion);
          sendEvent(JSON.stringify({ type: 'complete', response: resp }));
          sendEvent('[DONE]');
          controller.close();
          return;
        }
      }

      // 2. Try Anthropic Claude streaming
      const apiKey = process.env.ANTHROPIC_API_KEY;
      if (apiKey) {
        try {
          const systemPrompt = getAgentSystemPrompt(agentKey, skill as Parameters<typeof getAgentSystemPrompt>[1]);

          const res = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'x-api-key': apiKey,
              'anthropic-version': '2023-06-01',
            },
            body: JSON.stringify({
              model: process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-20250514',
              max_tokens: 4096,
              stream: true,
              system: systemPrompt,
              messages: anthropicMessages,
            }),
          });

          if (res.ok && res.body) {
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let fullText = '';
            let buffer = '';

            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              buffer += decoder.decode(value, { stream: true });
              const lines = buffer.split('\n');
              buffer = lines.pop() || '';

              for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed.startsWith('data: ')) continue;
                const data = trimmed.slice(6);
                if (data === '[DONE]') continue;

                try {
                  const parsed = JSON.parse(data);
                  if (parsed.type === 'content_block_delta') {
                    const token = parsed.delta?.text;
                    if (token) {
                      fullText += token;
                      sendEvent(JSON.stringify({ type: 'token', content: token }));
                    }
                  }
                } catch {
                  // skip malformed SSE data
                }
              }
            }

            const emotion = determineEmotion(fullText, agentKey);
            const resp = buildStructuredResponse(fullText, agentKey, emotion);
            sendEvent(JSON.stringify({ type: 'complete', response: resp }));
            sendEvent('[DONE]');
            controller.close();
            return;
          }
        } catch {
          // Fall through to offline fallback
        }
      }

      // 3. Fallback — simulate streaming
      const fallback = buildFallbackResponse(message, agentKey);
      const words = fallback.split(' ');
      for (let i = 0; i < words.length; i += 3) {
        const chunk = words.slice(i, i + 3).join(' ') + ' ';
        sendEvent(JSON.stringify({ type: 'token', content: chunk }));
      }
      const resp = buildStructuredResponse(fallback, agentKey, 'friendly');
      sendEvent(JSON.stringify({ type: 'complete', response: resp }));
      sendEvent('[DONE]');
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  });
}
