import { NextRequest, NextResponse } from 'next/server';

const TRIGGERS = [
  { keywords: ['debt', 'owe', 'behind', 'late payment', 'collections'], expression: 'empathetic', priority: 3 },
  { keywords: ['crypto', 'bitcoin', 'moon', 'yolo', 'nft', 'meme coin'], expression: 'confused', priority: 3 },
  { keywords: ['save', 'invest', 'grow', 'compound', 'retirement', 'roth'], expression: 'excited', priority: 2 },
  { keywords: ['help', 'how do i', 'explain', 'what is', 'teach me'], expression: 'teaching', priority: 1 },
  { keywords: ['lost', 'scared', 'worried', 'stressed', 'anxious', 'overwhelmed'], expression: 'empathetic', priority: 3 },
  { keywords: ['budget', 'plan', 'goal', 'track', 'organize'], expression: 'thinking', priority: 1 },
  { keywords: ['lol', 'haha', 'funny', '😂', 'joke'], expression: 'laughing', priority: 2 },
  { keywords: ['rich', 'million', 'lambo', 'retire early', 'passive income', 'fire'], expression: 'excited', priority: 2 },
  { keywords: ['tax', 'irs', 'deduction', 'filing'], expression: 'serious', priority: 1 },
  { keywords: ['kid', 'child', 'son', 'daughter', 'teach', 'allowance'], expression: 'excited', priority: 1 },
];

const REACTION_BUBBLES: Record<string, string[]> = {
  empathetic: ["Oof, let's work through this together 💪", "I hear you — we'll figure this out", "It's okay, everyone starts somewhere"],
  confused: ['Oh boy, here we go... 👀', 'Hmm, let me think about that one...', 'Interesting choice... 🤔'],
  excited: ["Now you're speaking my language! 🎯", 'Love where this is going! 🚀', "YES! Let's talk about this! 💰"],
  teaching: ['Great question! Let me explain... 📚', 'Ooh, I love teaching this!', "Perfect — here's the deal..."],
  thinking: ["Let's get you organized! 📊", 'Hmm, running some numbers...', 'Good thinking — let me crunch this'],
  laughing: ['Ha! Good one 😄', 'LOL, okay okay... 😂', "You're funny — but seriously..."],
  serious: ["Nobody's favorite topic... but I got you 😅", 'Important stuff — pay attention!', "Let's make sure you're covered"],
};

export async function POST(request: NextRequest) {
  const body = await request.json();
  const text = (body.partial_text || '').toLowerCase().trim();

  if (!text) {
    return NextResponse.json({ expression: 'idle', bubble: null });
  }

  let bestExpression = 'watching';
  let bestPriority = 0;

  for (const trigger of TRIGGERS) {
    for (const kw of trigger.keywords) {
      if (text.includes(kw) && trigger.priority > bestPriority) {
        bestPriority = trigger.priority;
        bestExpression = trigger.expression;
        break;
      }
    }
  }

  const bubbles = REACTION_BUBBLES[bestExpression];
  const bubble = bubbles ? bubbles[Math.floor(Math.random() * bubbles.length)] : null;

  return NextResponse.json({ expression: bestExpression, bubble });
}
