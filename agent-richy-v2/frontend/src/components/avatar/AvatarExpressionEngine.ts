import type { AvatarExpression } from '@/lib/types';
import { EXPRESSIONS, type ExpressionConfig } from './expressions';

/**
 * Maps context (agent, response content, calculator type)
 * to an avatar expression. Used by response pipeline
 * to set avatar state when a message arrives.
 */

interface ExpressionContext {
  agent?: string;
  text?: string;
  hasChart?: boolean;
  calculatorType?: string;
  isError?: boolean;
  isGreeting?: boolean;
}

const AGENT_DEFAULT_EXPRESSIONS: Record<string, AvatarExpression> = {
  coach_richy: 'friendly',
  budget_bot: 'presenting',
  invest_intel: 'thinking',
  debt_destroyer: 'serious',
  savings_sage: 'excited',
  kid_coach: 'teaching',
};

const TEXT_SENTIMENT_RULES: { pattern: RegExp; expression: AvatarExpression }[] = [
  { pattern: /congratulations|great job|well done|awesome/i, expression: 'celebrating' },
  { pattern: /unfortunately|bad news|warning|careful/i, expression: 'serious' },
  { pattern: /let me explain|here'?s how|the key is/i, expression: 'teaching' },
  { pattern: /interesting|huh|wow|whoa/i, expression: 'excited' },
  { pattern: /don'?t worry|it'?s okay|take your time/i, expression: 'empathetic' },
  { pattern: /ha(ha)+|lol|funny|joke/i, expression: 'laughing' },
];

export function resolveExpression(ctx: ExpressionContext): AvatarExpression {
  // Error state
  if (ctx.isError) return 'empathetic';

  // Greeting
  if (ctx.isGreeting) return 'friendly';

  // Chart/calculator → presenting
  if (ctx.hasChart || ctx.calculatorType) return 'presenting';

  // Text sentiment
  if (ctx.text) {
    for (const rule of TEXT_SENTIMENT_RULES) {
      if (rule.pattern.test(ctx.text)) {
        return rule.expression;
      }
    }
  }

  // Agent default
  if (ctx.agent && ctx.agent in AGENT_DEFAULT_EXPRESSIONS) {
    return AGENT_DEFAULT_EXPRESSIONS[ctx.agent];
  }

  return 'idle';
}

export function getExpressionConfig(expression: AvatarExpression): ExpressionConfig {
  return EXPRESSIONS[expression] ?? EXPRESSIONS.idle;
}
