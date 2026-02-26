import { NextRequest } from 'next/server';
import {
  routeToAgent,
  findCachedResponse,
  buildFallbackResponse,
  buildStructuredResponse,
  getAgentSystemPrompt,
  determineEmotion,
} from '@/lib/chatEngine';

export const runtime = 'nodejs';

console.log('[stream/route] MODULE LOADED — API KEY EXISTS:', !!process.env.ANTHROPIC_API_KEY);

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { message, agent, skill } = body;
  console.log('[stream/route] POST received:', JSON.stringify({ message: message?.slice(0, 80), agent, skill }));

  const agentKey = agent || routeToAgent(message);
  console.log('[stream/route] Routed to agent:', agentKey);

  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      function sendEvent(data: string) {
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
      }

      // 1. Check cached responses
      const cached = findCachedResponse(message);
      if (cached) {
        console.log('[stream/route] CACHED RESPONSE HIT for:', message?.slice(0, 40));
        // Simulate streaming by chunking the cached text
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

      // 2. Try Anthropic Claude streaming
      const apiKey = process.env.ANTHROPIC_API_KEY;
      console.log('[stream/route] API KEY EXISTS:', !!apiKey, 'KEY PREFIX:', apiKey?.slice(0, 12));
      if (apiKey) {
        try {
          const systemPrompt = getAgentSystemPrompt(agentKey, skill);
          console.log('[stream/route] CALLING ANTHROPIC — model:', process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-20250514');
          console.log('[stream/route] System prompt length:', systemPrompt.length);

          const requestBody = {
            model: process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-20250514',
            max_tokens: 4096,
            stream: true,
            system: systemPrompt,
            messages: [{ role: 'user', content: message }],
          };

          const res = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'x-api-key': apiKey,
              'anthropic-version': '2023-06-01',
            },
            body: JSON.stringify(requestBody),
          });

          console.log('[stream/route] Anthropic response status:', res.status, res.statusText);

          if (!res.ok) {
            const errBody = await res.text();
            console.error('[stream/route] Anthropic error body:', errBody);
          }

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

                // Anthropic SSE: event lines followed by data lines
                if (!trimmed.startsWith('data: ')) continue;
                const data = trimmed.slice(6);
                if (data === '[DONE]') continue;

                try {
                  const parsed = JSON.parse(data);

                  // Anthropic streaming events:
                  // - content_block_delta: { type: "content_block_delta", delta: { type: "text_delta", text: "..." } }
                  // - message_stop: end of message
                  if (parsed.type === 'content_block_delta') {
                    const token = parsed.delta?.text;
                    if (token) {
                      fullText += token;
                      sendEvent(JSON.stringify({ type: 'token', content: token }));
                    }
                  }
                  // message_stop signals end — we handle it after the loop
                } catch {
                  // skip malformed
                }
              }
            }

            const emotion = determineEmotion(fullText, agentKey);
            console.log('[stream/route] Stream complete — text length:', fullText.length, 'emotion:', emotion);
            const resp = buildStructuredResponse(fullText, agentKey, emotion);
            sendEvent(JSON.stringify({ type: 'complete', response: resp }));
            sendEvent('[DONE]');
            controller.close();
            return;
          }
        } catch (e) {
          console.error('[stream/route] Anthropic stream error:', e);
        }
      }

      // 3. Fallback — simulate streaming
      console.log('[stream/route] USING FALLBACK — no API key or API call failed');
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
