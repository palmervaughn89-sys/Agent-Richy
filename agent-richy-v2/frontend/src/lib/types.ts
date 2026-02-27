/* ── TypeScript types for all API responses ──────────────────────────── */

// ── Chat ────────────────────────────────────────────────────────────────

export interface ChatRequest {
  message: string;
  agent?: string;
  session_id?: string;
  context?: Record<string, unknown>;
  /** Detected skill to inject additional system prompt (keyword-matched). */
  skill?: "coupon" | "optimizer" | "market_intel" | "price_intel" | "subscription_value" | "goal_sim" | "bill_predict" | "local_deals" | "receipt_analyze" | "investment_intel" | "grocery_plan" | "allocation_map" | "proactive" | "trajectory" | "financial_twin" | "wealth_race" | "advisor_match" | "money_map" | "ripple_tracker" | "economic_intel" | "purchase_timing" | null;
  /** Accumulated optimizer expenses for context continuity. */
  optimizer_expenses?: string;
  /** Conversation history for multi-turn context. */
  messages?: { role: 'user' | 'assistant'; content: string }[];
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'area';
  /** @deprecated use `type` — kept for backward compat with backend */
  chart_type?: 'line' | 'bar' | 'pie' | 'area';
  title: string;
  data: Record<string, unknown>[];
  x_key: string;
  y_key?: string;
  /** @deprecated use `y_key` — kept for multi-series charts */
  y_keys?: string[];
  color?: string;
}

export interface Example {
  title: string;
  description: string;
  projected_savings?: string;
  timeline?: string;
  data?: Record<string, unknown>;
}

export interface Milestone {
  date?: string;
  label: string;
  month?: number;
}

export interface TimeHorizon {
  start?: string;
  end?: string;
  label?: string;
  months?: number;
  milestones: Milestone[];
}

export interface Evidence {
  source: string;
  fact: string;
  /** @deprecated use `fact` — kept for backward compat */
  snippet?: string;
  confidence: number;
}

export interface StructuredResponse {
  message: string;
  agent: string;
  charts: ChartConfig[];
  examples: Example[];
  time_horizon?: TimeHorizon;
  evidence: Evidence[];
  avatar_emotion: string;
  suggested_agent?: string;
  calculator_result?: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  agent?: string;
  structured?: StructuredResponse;
  timestamp: number;
}

// ── SSE Stream Events ───────────────────────────────────────────────────

export interface StreamTokenEvent {
  type: 'token';
  content: string;
}

export interface StreamCompleteEvent {
  type: 'complete';
  response: StructuredResponse;
}

export type StreamEvent = StreamTokenEvent | StreamCompleteEvent;

// ── Keystroke ───────────────────────────────────────────────────────────

export interface KeystrokeResponse {
  expression: AvatarExpression;
  bubble: string | null;
}

// ── Avatar ──────────────────────────────────────────────────────────────

export type AvatarExpression =
  | 'idle'
  | 'watching'
  | 'confused'
  | 'excited'
  | 'thinking'
  | 'presenting'
  | 'laughing'
  | 'empathetic'
  | 'serious'
  | 'celebrating'
  | 'teaching'
  | 'friendly';

// ── Profile ─────────────────────────────────────────────────────────────

export interface FinancialProfile {
  id?: string;
  name: string;
  age?: number;
  user_type: 'youth' | 'adult';
  monthly_income: number;
  monthly_expenses: number;
  savings_balance: number;
  emergency_fund: number;
  credit_score?: number;
  debts: Record<string, number>;
  debt_interest_rates: Record<string, number>;
  goals: string[];
  risk_tolerance: string;
  experience_level?: string;
  employment_status?: string;
}

// ── Kids Education ──────────────────────────────────────────────────────

export interface Quiz {
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export interface Lesson {
  lesson_id: string;
  title: string;
  description: string;
  video_url: string;
  video_type?: string;
  duration_seconds: number;
  thumbnail_emoji: string;
  quiz: Quiz[];
}

export interface KidsModule {
  module_id: string;
  title: string;
  description: string;
  icon: string;
  age_range: string;
  lessons: Lesson[];
}

export interface KidsProgress {
  completed_lessons: string[];
  badges: string[];
  quiz_scores: Record<string, { score: number; total: number }>;
}

// ── Agents ──────────────────────────────────────────────────────────────

export interface AgentInfo {
  name: string;
  icon: string;
  color: string;
  specialty: string;
  tagline: string;
  sample_q: string;
  avatar: string;
}

export type AgentKey =
  | 'coach_richy'
  | 'budget_bot'
  | 'invest_intel'
  | 'debt_destroyer'
  | 'savings_sage'
  | 'kid_coach';
