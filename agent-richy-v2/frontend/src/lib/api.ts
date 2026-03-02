/* ── API Client — wraps fetch with error handling ────────────────────── */

import type {
  ChatRequest,
  StructuredResponse,
  KeystrokeResponse,
  FinancialProfile,
  StreamEvent,
  AgentInfo,
} from './types';

async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`API Error ${res.status}: ${error}`);
  }
  return res.json();
}

// ── Chat ────────────────────────────────────────────────────────────────

export async function sendChatMessage(req: ChatRequest): Promise<StructuredResponse> {
  return fetchJSON<StructuredResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export async function streamChatMessage(
  req: ChatRequest,
  onToken: (token: string) => void,
  onComplete: (response: StructuredResponse) => void,
  onError?: (error: Error) => void,
): Promise<void> {
  try {
    const res = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });

    if (!res.ok) throw new Error(`Stream error: ${res.status}`);

    const reader = res.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim();
          if (data === '[DONE]') return;

          try {
            const event: StreamEvent = JSON.parse(data);
            if (event.type === 'token') {
              onToken(event.content);
            } else if (event.type === 'complete') {
              onComplete(event.response);
            }
          } catch {
            // Skip malformed events
          }
        }
      }
    }
  } catch (err) {
    onError?.(err instanceof Error ? err : new Error(String(err)));
  }
}

// ── Keystroke ───────────────────────────────────────────────────────────

export async function analyzeKeystroke(partialText: string): Promise<KeystrokeResponse> {
  return fetchJSON<KeystrokeResponse>('/api/keystroke', {
    method: 'POST',
    body: JSON.stringify({ partial_text: partialText }),
  });
}

// ── Profile ─────────────────────────────────────────────────────────────

export async function getProfile(sessionId: string): Promise<FinancialProfile> {
  return fetchJSON<FinancialProfile>(`/api/profile/${sessionId}`);
}

export async function updateProfile(
  sessionId: string,
  update: Partial<FinancialProfile>,
): Promise<FinancialProfile> {
  return fetchJSON<FinancialProfile>(`/api/profile/${sessionId}`, {
    method: 'PUT',
    body: JSON.stringify(update),
  });
}

// ── Agents ──────────────────────────────────────────────────────────────

export async function getAgents(): Promise<{ agents: Record<string, AgentInfo> }> {
  return fetchJSON('/api/agents');
}

// ── Kids ────────────────────────────────────────────────────────────────

export async function getKidsModules() {
  return fetchJSON('/api/kids/modules');
}

export async function getKidsProgress(sessionId: string) {
  return fetchJSON(`/api/kids/progress/${sessionId}`);
}

// ── Calculators ─────────────────────────────────────────────────────────

export async function calcCompoundInterest(data: {
  principal: number;
  annual_rate: number;
  years: number;
  monthly_contribution: number;
}) {
  return fetchJSON('/api/calculators/compound-interest', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function calcBudget(data: { monthly_income: number }) {
  return fetchJSON('/api/calculators/budget', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function calcEmergencyFund(data: {
  monthly_expenses: number;
  current_savings: number;
}) {
  return fetchJSON('/api/calculators/emergency-fund', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function calcSavingsGoal(data: {
  goal_amount: number;
  current_savings?: number;
  monthly_contribution?: number;
  annual_return?: number;
}) {
  return fetchJSON('/api/calculators/savings-goal', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function calcDebtPayoff(data: {
  balance: number;
  apr: number;
  monthly_payment: number;
}) {
  return fetchJSON('/api/calculators/debt-payoff', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function calcDebtCompare(data: {
  debts: { name: string; balance: number; apr: number; min_payment: number }[];
}) {
  return fetchJSON('/api/calculators/debt-compare', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function calcNetWorth(data: {
  assets: Record<string, number>;
  liabilities: Record<string, number>;
}) {
  return fetchJSON('/api/calculators/net-worth', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// ── Trading ─────────────────────────────────────────────────────────────

export async function getWeeklyPicks(topN: number = 10) {
  return fetchJSON<any[]>(`/api/trading/weekly-picks?top_n=${topN}`);
}

export async function scoreStock(ticker: string) {
  return fetchJSON<any>(`/api/trading/score/${encodeURIComponent(ticker)}`);
}

export async function getPortfolioAnalysis(tickers: string[]) {
  return fetchJSON<any>('/api/trading/portfolio-analysis', {
    method: 'POST',
    body: JSON.stringify({ tickers }),
  });
}

export async function getPerformance() {
  return fetchJSON<any>('/api/trading/performance');
}
