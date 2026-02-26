/* ── Kids education module data (migrated from video_data.py + config.py) ── */

import type { KidsModule, Quiz, Lesson } from './types';

// ── Badge Definitions ───────────────────────────────────────────────────

export interface Badge {
  id: string;
  name: string;
  icon: string;
  description: string;
  earned: boolean;
}

export const MODULE_BADGES: Record<string, { name: string; icon: string }> = {
  mod_1: { name: 'Money Master', icon: '💰' },
  mod_2: { name: 'Super Saver', icon: '🐷' },
  mod_3: { name: 'Growth Guru', icon: '🌱' },
  mod_4: { name: 'Money Genius', icon: '🧠' },
};

export const MEGA_BADGE = { name: 'Financial Superstar', icon: '🏆' };

// ── Video Modules (with real YouTube URLs from config.py) ───────────────

export const KIDS_MODULES: KidsModule[] = [
  {
    module_id: 'mod_1',
    title: 'What is Money?',
    description: 'Learn what money is, where it comes from, and why we use it!',
    icon: '💰',
    age_range: '5-10',
    lessons: [
      {
        lesson_id: 'mod1_les1',
        title: 'The History of Money',
        description: 'From bartering to Bitcoin — discover how money evolved over thousands of years.',
        video_url: 'https://www.youtube.com/embed/YCN2aTlocOw',
        video_type: 'youtube',
        duration_seconds: 272,
        thumbnail_emoji: '🏛️',
        quiz: [
          {
            question: 'What did people do before money existed?',
            options: ['Traded goods directly (barter)', 'Used credit cards', "Didn't buy anything", 'Used the internet'],
            correct_index: 0,
            explanation: 'Before money, people would trade things they had for things they needed. This is called bartering!',
          },
          {
            question: 'Why was money invented?',
            options: ['To make people rich', 'To make trading easier', 'Because gold is shiny', 'For fun'],
            correct_index: 1,
            explanation: 'Money was invented to make trading easier because everyone agrees on what it\'s worth.',
          },
        ],
      },
      {
        lesson_id: 'mod1_les2',
        title: 'Coins, Bills & Digital Money',
        description: 'Different types of money you use every day — from piggy banks to payment apps.',
        video_url: 'https://www.youtube.com/embed/aF8_AYWKYGA',
        video_type: 'youtube',
        duration_seconds: 315,
        thumbnail_emoji: '🪙',
        quiz: [
          {
            question: 'Which of these is a form of money?',
            options: ['All of the below', 'Coins', 'Dollar bills', 'Money in a bank app'],
            correct_index: 0,
            explanation: 'Coins, bills, and digital money in bank apps are all forms of money!',
          },
          {
            question: 'Where does money come from?',
            options: ['Trees', 'People earn it by working', 'It appears magically', 'The store gives it to you'],
            correct_index: 1,
            explanation: 'Money has to be earned! People work and provide value to earn money.',
          },
        ],
      },
      {
        lesson_id: 'mod1_les3',
        title: 'Needs vs. Wants',
        description: 'The most important money lesson — knowing the difference between needs and wants.',
        video_url: 'https://www.youtube.com/embed/E0F0MU_87b4',
        video_type: 'youtube',
        duration_seconds: 228,
        thumbnail_emoji: '🤔',
        quiz: [
          {
            question: 'Which is a NEED?',
            options: ['Food and water', 'A new video game', 'Designer sneakers', 'A skateboard'],
            correct_index: 0,
            explanation: 'Food and water are things we need to survive! The others are wants.',
          },
          {
            question: 'What should you buy first?',
            options: ['Needs', 'Wants', 'Whatever is on sale', 'Whatever your friends buy'],
            correct_index: 0,
            explanation: 'Always take care of your needs (food, shelter, clothing) before spending on wants.',
          },
          {
            question: 'Is a phone a need or a want?',
            options: ['It depends on the situation', 'Always a need', 'Always a want', "It's free"],
            correct_index: 0,
            explanation: 'A basic phone for safety can be a need, but the latest smartphone is usually a want!',
          },
        ],
      },
      {
        lesson_id: 'mod1_les4',
        title: 'How Banks Work',
        description: "Your money's safe home — learn how banks keep your money and help it grow.",
        video_url: 'https://www.youtube.com/embed/8N_tupPBtWQ',
        video_type: 'youtube',
        duration_seconds: 295,
        thumbnail_emoji: '🏦',
        quiz: [
          {
            question: 'What does a bank do with your money?',
            options: ['Keeps it safe and lends some to others', 'Spends it on themselves', 'Throws it away', 'Sends it to another country'],
            correct_index: 0,
            explanation: 'Banks keep your money safe and lend some of it to others, paying you interest for the privilege.',
          },
          {
            question: 'What is interest?',
            options: ['Money the bank pays you for keeping your money there', 'A fee for having an account', 'Extra money you owe the bank', 'A type of tax'],
            correct_index: 0,
            explanation: 'Interest is money the bank pays you as a thank-you for letting them hold your money!',
          },
        ],
      },
    ],
  },
  {
    module_id: 'mod_2',
    title: 'Saving & Spending Wisely',
    description: 'Build your savings muscle and learn to spend wisely.',
    icon: '🐷',
    age_range: '5-10',
    lessons: [
      {
        lesson_id: 'mod2_les1',
        title: 'Pay Yourself First',
        description: 'The #1 savings rule — save before you spend!',
        video_url: 'https://www.youtube.com/embed/jm0L5YhSS3g',
        video_type: 'youtube',
        duration_seconds: 252,
        thumbnail_emoji: '💰',
        quiz: [
          {
            question: "What does 'pay yourself first' mean?",
            options: ['Save money before spending on anything else', 'Pay your bills first', 'Buy yourself a gift', "Don't pay anyone"],
            correct_index: 0,
            explanation: 'Pay yourself first means saving a portion of your money before spending on anything else!',
          },
          {
            question: 'When should you save money?',
            options: ['As soon as you get it', 'After buying everything you want', 'Only on holidays', 'Never'],
            correct_index: 0,
            explanation: 'The best time to save is as soon as you receive money. Make it a habit!',
          },
        ],
      },
      {
        lesson_id: 'mod2_les2',
        title: 'Setting Savings Goals',
        description: 'Want something special? Learn to save for it step by step.',
        video_url: 'https://www.youtube.com/embed/KjOAtcLvnyA',
        video_type: 'youtube',
        duration_seconds: 330,
        thumbnail_emoji: '🎯',
        quiz: [
          {
            question: 'What makes a good savings goal?',
            options: ['Specific amount and deadline', "Just 'save more money'", 'As much as possible', 'Whatever your parents say'],
            correct_index: 0,
            explanation: 'A SMART savings goal has a specific amount and a deadline, like "Save $100 by June."',
          },
          {
            question: 'You want to buy a $60 game. You save $10/week. How many weeks?',
            options: ['6 weeks', '60 weeks', '10 weeks', '1 week'],
            correct_index: 0,
            explanation: '$60 ÷ $10/week = 6 weeks. Simple math shows you exactly when you\'ll reach your goal!',
          },
        ],
      },
      {
        lesson_id: 'mod2_les3',
        title: 'Smart Spending Decisions',
        description: 'Learn to think before you spend — and keep more money in your pocket.',
        video_url: 'https://www.youtube.com/embed/TXA2jdEaqJs',
        video_type: 'youtube',
        duration_seconds: 285,
        thumbnail_emoji: '🛒',
        quiz: [
          {
            question: 'What is the 24-hour rule?',
            options: ['Wait 24 hours before buying something you want', 'You can only shop for 24 hours', 'Return items within 24 hours', 'Spend for only 24 minutes'],
            correct_index: 0,
            explanation: 'The 24-hour rule means waiting a day before making a purchase to avoid impulse buys.',
          },
          {
            question: 'What should you do before buying something?',
            options: ['Compare prices and think about it', 'Buy it immediately', 'Buy the most expensive version', 'Ask a stranger'],
            correct_index: 0,
            explanation: 'Smart shoppers compare prices and think about whether they really need something.',
          },
        ],
      },
      {
        lesson_id: 'mod2_les4',
        title: 'The Power of Compound Interest',
        description: 'How your money can grow while you sleep — the magic of compound interest!',
        video_url: 'https://www.youtube.com/embed/MjAHcCpEmMM',
        video_type: 'youtube',
        duration_seconds: 310,
        thumbnail_emoji: '✨',
        quiz: [
          {
            question: 'What is compound interest?',
            options: ['Earning interest on your interest', 'A type of bank fee', 'Extra money you pay the bank', 'Interest that disappears'],
            correct_index: 0,
            explanation: 'Compound interest means you earn interest on your original savings AND on the interest you\'ve already earned. It\'s like a snowball effect!',
          },
          {
            question: 'Who earns more: someone who starts saving at 15 or at 25?',
            options: ['The person who starts at 15', 'The person who starts at 25', 'They earn the same', 'Neither earns anything'],
            correct_index: 0,
            explanation: 'Starting 10 years earlier gives compound interest much more time to work, so the person who starts at 15 usually ends up with significantly more!',
          },
        ],
      },
    ],
  },
  {
    module_id: 'mod_3',
    title: 'Earning & Growing Money',
    description: 'Discover ways to earn money and make it grow over time.',
    icon: '🌱',
    age_range: '8-12',
    lessons: [
      {
        lesson_id: 'mod3_les1',
        title: 'Ways Kids Can Earn Money',
        description: 'From lemonade stands to lawn care — real ways kids make real money.',
        video_url: 'https://www.youtube.com/embed/346CwLMNVCg',
        video_type: 'youtube',
        duration_seconds: 380,
        thumbnail_emoji: '🍋',
        quiz: [
          {
            question: 'Which is a good way for kids to earn money?',
            options: ['All of the below', 'Do chores for neighbors', 'Sell crafts or baked goods', 'Tutor younger kids'],
            correct_index: 0,
            explanation: 'There are tons of ways kids can earn money — chores, selling things, tutoring, and more!',
          },
          {
            question: "What's the most important quality for earning money?",
            options: ['Being reliable and working hard', 'Being lucky', 'Having rich parents', 'Being the oldest kid'],
            correct_index: 0,
            explanation: 'Reliability and hard work are the keys to earning money at any age!',
          },
        ],
      },
      {
        lesson_id: 'mod3_les2',
        title: 'Entrepreneurship for Young People',
        description: 'Think like a business owner — even as a kid you can start something amazing.',
        video_url: 'https://www.youtube.com/embed/PyIcVsbPbQ0',
        video_type: 'youtube',
        duration_seconds: 345,
        thumbnail_emoji: '💡',
        quiz: [
          {
            question: 'What is an entrepreneur?',
            options: ['Someone who starts a business', 'Someone who works for the government', 'A type of teacher', 'A bank employee'],
            correct_index: 0,
            explanation: 'An entrepreneur is someone who creates and runs their own business!',
          },
          {
            question: "What's the first step to starting a business?",
            options: ['Find a problem you can solve', 'Borrow a lot of money', 'Quit school', "Copy someone else's business exactly"],
            correct_index: 0,
            explanation: 'The best businesses solve real problems. Find something people need and figure out how to provide it!',
          },
        ],
      },
      {
        lesson_id: 'mod3_les3',
        title: 'What is Investing?',
        description: 'Making your money work for YOU — intro to stocks, bonds, and more.',
        video_url: 'https://www.youtube.com/embed/WEDIj9JBTC8',
        video_type: 'youtube',
        duration_seconds: 300,
        thumbnail_emoji: '📈',
        quiz: [
          {
            question: 'What is investing?',
            options: ['Using money to make more money over time', 'Putting money under your mattress', 'Spending money on things you want', 'Giving money away'],
            correct_index: 0,
            explanation: 'Investing means putting your money into something that has the potential to grow and give you more money back over time!',
          },
          {
            question: 'What is a stock?',
            options: ['Owning a tiny piece of a company', 'A type of soup', 'Money in a savings account', 'A loan from the bank'],
            correct_index: 0,
            explanation: 'When you buy a stock, you own a small piece of a company. If the company does well, your stock becomes more valuable!',
          },
        ],
      },
      {
        lesson_id: 'mod3_les4',
        title: 'Good Debt vs. Bad Debt',
        description: 'Not all borrowing is bad — learn the difference between smart and dangerous debt.',
        video_url: 'https://www.youtube.com/embed/WnO1T7bnFGU',
        video_type: 'youtube',
        duration_seconds: 270,
        thumbnail_emoji: '💳',
        quiz: [
          {
            question: "Which is an example of 'good debt'?",
            options: ['A student loan for education', 'Credit card debt for designer clothes', 'Borrowing to buy the latest phone', 'A loan for a vacation'],
            correct_index: 0,
            explanation: 'Good debt helps you build value long-term, like education or a home. Bad debt is for things that lose value quickly.',
          },
          {
            question: "What makes debt 'bad'?",
            options: ['High interest on things that lose value', 'Any borrowing at all', 'Lending money to a friend', 'Having a savings account'],
            correct_index: 0,
            explanation: 'Debt becomes bad when you pay high interest on things that decrease in value over time.',
          },
        ],
      },
    ],
  },
  {
    module_id: 'mod_4',
    title: 'Smart Money Habits',
    description: 'Build lifelong habits that make you wealthy and wise with money.',
    icon: '🧠',
    age_range: '8-12',
    lessons: [
      {
        lesson_id: 'mod4_les1',
        title: 'The 50/30/20 Budget Rule',
        description: 'The simplest budget rule that works for any income level.',
        video_url: 'https://www.youtube.com/embed/HQzoZfc3GwQ',
        video_type: 'youtube',
        duration_seconds: 290,
        thumbnail_emoji: '🫙',
        quiz: [
          {
            question: 'In the 50/30/20 rule, what does 50% go to?',
            options: ['Needs (food, housing, bills)', 'Wants (fun stuff)', 'Savings', 'Investments'],
            correct_index: 0,
            explanation: '50% goes to needs/essentials, 30% to wants, and 20% to savings and investments.',
          },
          {
            question: 'If you earn $100, how much should you save?',
            options: ['$20', '$50', '$30', '$10'],
            correct_index: 0,
            explanation: 'The 50/30/20 rule says save 20% of your income. 20% of $100 = $20!',
          },
        ],
      },
      {
        lesson_id: 'mod4_les2',
        title: 'Avoiding Money Traps',
        description: 'Scams, FOMO spending, and sneaky fees — protect your money!',
        video_url: 'https://www.youtube.com/embed/A8LdSIqzoE4',
        video_type: 'youtube',
        duration_seconds: 320,
        thumbnail_emoji: '⚠️',
        quiz: [
          {
            question: 'What is FOMO spending?',
            options: ["Buying things because you're afraid of missing out", 'Spending money overseas', 'A type of investment', 'Saving for the future'],
            correct_index: 0,
            explanation: "FOMO (Fear Of Missing Out) spending is when you buy things just because everyone else has them.",
          },
          {
            question: "If someone offers you 'free money,' what should you do?",
            options: ["Be suspicious — it's probably a scam", 'Give them your bank account info', 'Send them money first', 'Tell all your friends about it'],
            correct_index: 0,
            explanation: "If it sounds too good to be true, it probably is! Always be cautious with money offers from strangers.",
          },
        ],
      },
      {
        lesson_id: 'mod4_les3',
        title: 'Building a Money Routine',
        description: 'Create daily and weekly money habits that build real wealth over time.',
        video_url: 'https://www.youtube.com/embed/Gs8K-R9PEnw',
        video_type: 'youtube',
        duration_seconds: 255,
        thumbnail_emoji: '📅',
        quiz: [
          {
            question: 'How often should you check your money?',
            options: ['At least once a week', 'Once a year', "Only when you're broke", "Never — it's stressful"],
            correct_index: 0,
            explanation: 'Checking your money weekly helps you stay on track and catch problems early.',
          },
          {
            question: "What's the best money habit?",
            options: ['Saving consistently, even small amounts', 'Spending everything and hoping for the best', 'Only thinking about money when you need something', 'Avoiding all money topics'],
            correct_index: 0,
            explanation: 'Consistency is key! Even saving $5/week adds up to $260/year.',
          },
        ],
      },
      {
        lesson_id: 'mod4_les4',
        title: 'Your Financial Future',
        description: 'Plan ahead — where do you want to be in 5, 10, and 20 years?',
        video_url: 'https://www.youtube.com/embed/fJV-dvf_2HA',
        video_type: 'youtube',
        duration_seconds: 330,
        thumbnail_emoji: '🔮',
        quiz: [
          {
            question: 'Why should you think about your financial future now?',
            options: ['Starting early gives you more time to grow wealth', 'You should only think about today', 'Thinking about the future is scary', "Money doesn't matter"],
            correct_index: 0,
            explanation: 'The earlier you start planning and saving, the more time your money has to grow through compound interest!',
          },
          {
            question: "What's the biggest advantage young people have?",
            options: ['Time — money can grow for decades', 'More allowance', 'Parents pay for everything', 'No bills to pay'],
            correct_index: 0,
            explanation: 'Time is your greatest asset! Starting to save and invest early means decades of compound growth.',
          },
        ],
      },
    ],
  },
];

// ── Helper Functions ────────────────────────────────────────────────────

export function getAllLessonIds(): string[] {
  return KIDS_MODULES.flatMap((mod) => mod.lessons.map((l) => l.lesson_id));
}

export function getTotalLessons(): number {
  return KIDS_MODULES.reduce((sum, mod) => sum + mod.lessons.length, 0);
}

export function getModuleById(moduleId: string): KidsModule | undefined {
  return KIDS_MODULES.find((m) => m.module_id === moduleId);
}

export function getLessonById(lessonId: string): { module: KidsModule; lesson: Lesson } | undefined {
  for (const mod of KIDS_MODULES) {
    const lesson = mod.lessons.find((l) => l.lesson_id === lessonId);
    if (lesson) return { module: mod, lesson };
  }
  return undefined;
}

export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function buildBadgesForProgress(completedLessons: string[]): Badge[] {
  const allBadges: Badge[] = KIDS_MODULES.map((mod) => {
    const moduleLessonIds = mod.lessons.map((l) => l.lesson_id);
    const allComplete = moduleLessonIds.every((id) => completedLessons.includes(id));
    const badgeDef = MODULE_BADGES[mod.module_id];
    return {
      id: mod.module_id,
      name: badgeDef?.name ?? mod.title,
      icon: badgeDef?.icon ?? mod.icon,
      description: `Complete all lessons in "${mod.title}"`,
      earned: allComplete,
    };
  });

  // Check mega badge
  const totalLessons = getTotalLessons();
  const allComplete = completedLessons.length >= totalLessons;
  allBadges.push({
    id: 'mega',
    name: MEGA_BADGE.name,
    icon: MEGA_BADGE.icon,
    description: 'Complete ALL lessons across every module!',
    earned: allComplete,
  });

  return allBadges;
}
