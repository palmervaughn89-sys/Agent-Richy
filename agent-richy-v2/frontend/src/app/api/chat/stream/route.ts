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

export async function POST(request: NextRequest) {
  const { message, agent } = await request.json();
  const agentKey = agent || routeToAgent(message);

  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      function sendEvent(data: string) {
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
      }

      // 1. Check cached responses
      const cached = findCachedResponse(message);
      if (cached) {
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

      // 2. Try OpenAI streaming
      const apiKey = process.env.OPENAI_API_KEY;
      if (apiKey) {
        try {
          const systemPrompt = getAgentSystemPrompt(agentKey);
          const res = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${apiKey}`,
            },
            body: JSON.stringify({
              model: process.env.OPENAI_MODEL || 'gpt-4o',
              temperature: 0.7,
              max_tokens: 1000,
              stream: true,
              messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: message },
              ],
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
                  const token = parsed.choices?.[0]?.delta?.content;
                  if (token) {
                    fullText += token;
                    sendEvent(JSON.stringify({ type: 'token', content: token }));
                  }
                } catch {
                  // skip malformed
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
        } catch (e) {
          console.error('OpenAI stream error:', e);
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
