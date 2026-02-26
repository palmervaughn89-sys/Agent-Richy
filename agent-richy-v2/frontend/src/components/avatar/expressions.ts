/* ── Avatar expression definitions & transition rules ────────────────── */

import type { AvatarExpression } from '@/lib/types';

export interface ExpressionConfig {
  label: string;
  emoji: string;
  eyeStyle: string;
  mouthStyle: string;
  browStyle: string;
  bodyAnimation: string;
  bgGlow: string;
}

export const EXPRESSIONS: Record<AvatarExpression, ExpressionConfig> = {
  idle: {
    label: 'Idle',
    emoji: '😊',
    eyeStyle: 'normal',
    mouthStyle: 'smile',
    browStyle: 'normal',
    bodyAnimation: 'float',
    bgGlow: 'rgba(245, 158, 11, 0.1)',
  },
  watching: {
    label: 'Watching',
    emoji: '👀',
    eyeStyle: 'tracking',
    mouthStyle: 'slight-smile',
    browStyle: 'raised-one',
    bodyAnimation: 'lean-forward',
    bgGlow: 'rgba(59, 130, 246, 0.1)',
  },
  confused: {
    label: 'Confused',
    emoji: '🤨',
    eyeStyle: 'squint',
    mouthStyle: 'wavy',
    browStyle: 'furrowed',
    bodyAnimation: 'head-scratch',
    bgGlow: 'rgba(245, 158, 11, 0.15)',
  },
  excited: {
    label: 'Excited',
    emoji: '🤩',
    eyeStyle: 'wide',
    mouthStyle: 'big-smile',
    browStyle: 'raised',
    bodyAnimation: 'bounce',
    bgGlow: 'rgba(16, 185, 129, 0.2)',
  },
  thinking: {
    label: 'Thinking',
    emoji: '🤔',
    eyeStyle: 'look-up',
    mouthStyle: 'pursed',
    browStyle: 'raised-one',
    bodyAnimation: 'chin-tap',
    bgGlow: 'rgba(139, 92, 246, 0.15)',
  },
  presenting: {
    label: 'Presenting',
    emoji: '📊',
    eyeStyle: 'confident',
    mouthStyle: 'smile',
    browStyle: 'normal',
    bodyAnimation: 'gesture',
    bgGlow: 'rgba(37, 99, 235, 0.15)',
  },
  laughing: {
    label: 'Laughing',
    emoji: '😂',
    eyeStyle: 'squint-happy',
    mouthStyle: 'open-laugh',
    browStyle: 'raised',
    bodyAnimation: 'shake',
    bgGlow: 'rgba(245, 158, 11, 0.2)',
  },
  empathetic: {
    label: 'Empathetic',
    emoji: '🫂',
    eyeStyle: 'soft',
    mouthStyle: 'slight-frown',
    browStyle: 'concerned',
    bodyAnimation: 'nod',
    bgGlow: 'rgba(139, 92, 246, 0.12)',
  },
  serious: {
    label: 'Serious',
    emoji: '😐',
    eyeStyle: 'focused',
    mouthStyle: 'flat',
    browStyle: 'furrowed',
    bodyAnimation: 'still',
    bgGlow: 'rgba(239, 68, 68, 0.1)',
  },
  celebrating: {
    label: 'Celebrating',
    emoji: '🎉',
    eyeStyle: 'wide',
    mouthStyle: 'big-smile',
    browStyle: 'raised',
    bodyAnimation: 'fist-pump',
    bgGlow: 'rgba(245, 158, 11, 0.25)',
  },
  teaching: {
    label: 'Teaching',
    emoji: '👨‍🏫',
    eyeStyle: 'warm',
    mouthStyle: 'smile',
    browStyle: 'raised-one',
    bodyAnimation: 'point',
    bgGlow: 'rgba(6, 182, 212, 0.15)',
  },
  friendly: {
    label: 'Friendly',
    emoji: '😄',
    eyeStyle: 'warm',
    mouthStyle: 'smile',
    browStyle: 'normal',
    bodyAnimation: 'wave',
    bgGlow: 'rgba(245, 158, 11, 0.15)',
  },
};

export interface ExpressionTrigger {
  keywords: string[];
  expression: AvatarExpression;
  priority: number;
}

export const KEYSTROKE_TRIGGERS: ExpressionTrigger[] = [
  { keywords: ['debt', 'owe', 'behind', 'late payment'], expression: 'empathetic', priority: 2 },
  { keywords: ['crypto', 'bitcoin', 'moon', 'yolo', 'nft'], expression: 'confused', priority: 3 },
  { keywords: ['save', 'invest', 'grow', 'compound', 'roth'], expression: 'excited', priority: 2 },
  { keywords: ['help', 'how do i', 'explain', 'what is'], expression: 'teaching', priority: 1 },
  { keywords: ['lost', 'scared', 'worried', 'stressed'], expression: 'empathetic', priority: 3 },
  { keywords: ['budget', 'plan', 'goal', 'track'], expression: 'thinking', priority: 1 },
  { keywords: ['lol', 'haha', 'funny', '😂'], expression: 'laughing', priority: 2 },
  { keywords: ['rich', 'million', 'lambo', 'retire early'], expression: 'excited', priority: 2 },
  { keywords: ['tax', 'irs', 'deduction'], expression: 'serious', priority: 1 },
  { keywords: ['kid', 'child', 'teach my'], expression: 'excited', priority: 1 },
];

/** Reaction bubbles — short quips keyed by expression */
export const REACTION_BUBBLES: Record<string, string[]> = {
  empathetic: [
    "Oof, let's work through this together 💪",
    "I hear you — we'll figure this out",
    "It's okay, everyone starts somewhere",
  ],
  confused: [
    "Oh boy, here we go... 👀",
    "Hmm, interesting choice... 🤔",
    "Wait, let me process that...",
  ],
  excited: [
    "Now you're speaking my language! 🎯",
    "Love where this is going! 🚀",
    "YES! Let's talk about this! 💰",
  ],
  teaching: [
    "Great question! Let me explain... 📚",
    "Ooh, I love teaching this!",
    "Perfect — here's the deal...",
  ],
  thinking: [
    "Let's get you organized! 📊",
    "Hmm, running some numbers...",
    "Good thinking — let me crunch this",
  ],
  laughing: [
    "Ha! Good one 😄",
    "LOL, okay okay... 😂",
  ],
  serious: [
    "Nobody's favorite topic... but I got you 😅",
    "Important stuff — pay attention!",
  ],
};
