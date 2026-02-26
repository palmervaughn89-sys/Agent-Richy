/* ── Static constants & config data (migrated from Streamlit config.py) ── */

import type { AgentKey, AgentInfo } from './types';

// ── Brand Colors ────────────────────────────────────────────────────────

export const COLORS = {
  navy:           '#0A1628',
  navy_light:     '#0F2035',
  navy_card:      '#111D32',
  blue:           '#2563EB',
  blue_light:     '#3B82F6',
  blue_hover:     '#1D4ED8',
  gold:           '#F59E0B',
  gold_light:     '#FBBF24',
  gold_dim:       '#D97706',
  white:          '#FFFFFF',
  text_primary:   '#F1F5F9',
  text_secondary: '#94A3B8',
  text_muted:     '#64748B',
  green:          '#10B981',
  green_light:    '#34D399',
  red:            '#EF4444',
  red_light:      '#F87171',
  border:         '#1E293B',
  border_light:   '#334155',
  surface:        '#0F172A',
  surface_alt:    '#1E293B',
  gray:           '#94A3B8',
  gray_dark:      '#64748B',
  purple:         '#8B5CF6',
  cyan:           '#06B6D4',
} as const;

export const CHART_COLORS = [
  COLORS.blue,
  COLORS.gold,
  COLORS.green,
  COLORS.red,
  COLORS.purple,
  '#EC4899',
  COLORS.cyan,
  '#F97316',
];

// ── Free-Tier Limits ────────────────────────────────────────────────────

export const FREE_MESSAGE_LIMIT = 10;
export const FREE_VIDEO_MODULES = 1;   // Only Module 1
export const FREE_VIDEO_LESSONS = 2;   // First 2 videos in Module 1

// ── Agent Definitions ───────────────────────────────────────────────────

export const AGENTS: Record<AgentKey, AgentInfo> = {
  coach_richy: {
    name: 'Coach Richy',
    icon: '💰',
    color: COLORS.gold,
    specialty: 'General Financial Coaching',
    tagline: 'Your smart friend who happens to be a financial planner',
    sample_q: 'Help me build a complete financial plan',
    avatar: 'https://api.dicebear.com/7.x/personas/svg?seed=CoachRichy&backgroundColor=F59E0B',
  },
  budget_bot: {
    name: 'Budget Bot',
    icon: '📊',
    color: COLORS.blue,
    specialty: 'Budgeting & Expense Tracking',
    tagline: 'Analytical, detail-oriented — loves crunching your numbers',
    sample_q: 'Analyze my spending and build a budget',
    avatar: 'https://api.dicebear.com/7.x/personas/svg?seed=BudgetBot&backgroundColor=2563EB',
  },
  invest_intel: {
    name: 'Invest Intel',
    icon: '📈',
    color: COLORS.green,
    specialty: 'Investing & Portfolio Strategy',
    tagline: 'Confident, strategic, data-driven market insights',
    sample_q: 'How should I invest $500/month?',
    avatar: 'https://api.dicebear.com/7.x/personas/svg?seed=InvestIntel&backgroundColor=10B981',
  },
  debt_destroyer: {
    name: 'Debt Destroyer',
    icon: '💳',
    color: COLORS.red,
    specialty: 'Debt Payoff Strategies',
    tagline: 'Motivational, action-oriented debt elimination',
    sample_q: 'I have $20K in credit card debt — help!',
    avatar: 'https://api.dicebear.com/7.x/personas/svg?seed=DebtDestroyer&backgroundColor=EF4444',
  },
  savings_sage: {
    name: 'Savings Sage',
    icon: '🏦',
    color: COLORS.purple,
    specialty: 'Savings & Emergency Funds',
    tagline: 'Patient, goal-oriented savings strategist',
    sample_q: 'How do I build a 6-month emergency fund?',
    avatar: 'https://api.dicebear.com/7.x/personas/svg?seed=SavingsSage&backgroundColor=8B5CF6',
  },
  kid_coach: {
    name: 'Kid Coach',
    icon: '🎓',
    color: COLORS.cyan,
    specialty: 'Youth Financial Education',
    tagline: 'Fun, educational — makes money lessons exciting',
    sample_q: 'How can I start earning money as a kid?',
    avatar: 'https://api.dicebear.com/7.x/personas/svg?seed=KidCoach&backgroundColor=06B6D4',
  },
};

export const AGENT_KEYS = Object.keys(AGENTS) as AgentKey[];

// ── Onboarding Options ──────────────────────────────────────────────────

export const AGE_RANGES = [
  'Under 13',
  '13-17',
  '18-24',
  '25-34',
  '35-44',
  '45-54',
  '55-64',
  '65+',
];

export const EXPERIENCE_LEVELS = [
  'Beginner — I\'m just starting to learn about money',
  'Intermediate — I know the basics but want to improve',
  'Advanced — I\'m experienced and want expert strategies',
];

export const EMPLOYMENT_STATUS = [
  'Employed (Full-time)',
  'Employed (Part-time)',
  'Self-employed / Freelancer',
  'Student',
  'Unemployed / Between jobs',
  'Retired',
  'Homemaker',
];

export const INCOME_RANGES = [
  'Under $25,000',
  '$25,000 - $49,999',
  '$50,000 - $74,999',
  '$75,000 - $99,999',
  '$100,000 - $149,999',
  '$150,000 - $249,999',
  '$250,000+',
  'Prefer not to say',
];

export const FINANCIAL_GOALS = [
  'Build Emergency Fund',
  'Pay Off Debt',
  'Start Investing',
  'Save for Retirement',
  'Teach Kids About Money',
  'Buy a Home',
  'Build Passive Income',
  'Improve Credit Score',
  'Create a Budget',
  'Plan for College',
];

export const RISK_TOLERANCE_OPTIONS = [
  { value: 'conservative', label: 'Conservative', description: 'Preserve capital, low risk' },
  { value: 'moderate', label: 'Moderate', description: 'Balanced growth and safety' },
  { value: 'aggressive', label: 'Aggressive', description: 'Maximum growth, higher risk' },
];
