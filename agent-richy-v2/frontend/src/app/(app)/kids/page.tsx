'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TopNav } from '@/components/layout';
import {
  BookOpen,
  PiggyBank,
  Building,
  Wallet,
  TrendingUp,
  Play,
  Clock,
  CheckCircle2,
  ChevronRight,
  Star,
} from 'lucide-react';

/* ── Learning Modules ─────────────────────────────────────────────────── */
const MODULES = [
  {
    icon: BookOpen,
    title: 'What is Money?',
    ages: '5–8',
    desc: 'Discover where money comes from, what it can do, and why it matters.',
    letter: 'M',
  },
  {
    icon: PiggyBank,
    title: 'Saving vs. Spending',
    ages: '6–10',
    desc: 'Learn the power of putting money aside and making smart choices.',
    letter: 'S',
  },
  {
    icon: Building,
    title: 'How Banks Work',
    ages: '8–12',
    desc: 'What happens when you put money in a bank? Interest, accounts, and more.',
    letter: 'B',
  },
  {
    icon: Wallet,
    title: 'Your First Budget',
    ages: '10–14',
    desc: 'Plan your money like a pro — allocate income to needs, wants, and savings.',
    letter: 'B',
  },
  {
    icon: TrendingUp,
    title: 'Investing Basics',
    ages: '12–16',
    desc: 'Stocks, bonds, and compound interest — start thinking like an investor.',
    letter: 'I',
  },
];

/* ── Quiz Data ────────────────────────────────────────────────────────── */
const QUIZ_QUESTIONS = [
  {
    q: 'If you save $5 every week, how much will you have after 1 year?',
    options: ['$52', '$260', '$520'],
    correct: 1,
    explain: '$5 × 52 weeks = $260. Small amounts add up!',
  },
  {
    q: 'What does "interest" mean at a bank?',
    options: ['Being curious', 'Money the bank pays you for saving', 'A fee you pay'],
    correct: 1,
    explain: 'Banks pay you interest as a reward for keeping your money with them.',
  },
  {
    q: "What's the smartest thing to do with birthday money?",
    options: ['Spend it all', 'Save some, spend some', 'Hide it under the bed'],
    correct: 1,
    explain: 'A balanced approach: enjoy some now and save the rest to grow!',
  },
  {
    q: 'What is compound interest?',
    options: ['Interest on your interest', 'A type of tax', 'A bank fee'],
    correct: 0,
    explain: 'Compound interest means you earn interest on your original money AND the interest it already earned.',
  },
  {
    q: 'What is a "need" vs. a "want"?',
    options: [
      'Needs are things you must have; wants are nice to have',
      "They're the same thing",
      'Wants are more important than needs',
    ],
    correct: 0,
    explain: 'Needs (food, shelter) keep you alive. Wants (games, toys) make life fun but aren\'t essential.',
  },
];

/* ── Video Placeholders ───────────────────────────────────────────────── */
const VIDEOS = [
  { title: 'Money 101: Where Does Money Come From?', duration: '4:30' },
  { title: 'The Magic of Compound Interest', duration: '5:15' },
  { title: 'Needs vs. Wants: The Game', duration: '3:45' },
  { title: 'How to Start a Lemonade Stand Business', duration: '6:00' },
];

/* ══════════════════════════════════════════════════════════════════════
   KIDS ZONE PAGE
   ══════════════════════════════════════════════════════════════════════ */
export default function KidsPage() {
  return (
    <div className="flex flex-col h-full">
      <TopNav title="Richy's Kids Zone" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6 space-y-10">
        {/* Header */}
        <div>
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
            <p className="section-label">KIDS ZONE</p>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-txt tracking-tight">
              Richy&apos;s Kids Zone
            </h1>
          </motion.div>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-txt-off mt-2 text-sm"
          >
            Financial superpowers for the next generation
          </motion.p>
        </div>

        {/* ── Section 1: Learning Modules ────────────────────────────── */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.15 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="font-mono text-[10px] font-semibold text-amber-400 uppercase tracking-label mb-1">LEARNING</p>
          <h2 className="text-lg font-bold text-txt mb-4">Learning Modules</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {MODULES.map((mod, i) => (
              <motion.div
                key={mod.title}
                initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="ds-card group"
              >
                <span className="absolute top-3 right-4 text-[80px] font-extrabold text-accent/[.06] leading-none select-none pointer-events-none">{mod.letter}</span>
                <div className="flex items-start gap-3 mb-3 relative z-10">
                  <div className="w-10 h-10 rounded-xl border border-line bg-ghost flex items-center justify-center">
                    <mod.icon className="w-5 h-5 text-accent" />
                  </div>
                  <span className="badge-pill text-[10px]">Ages {mod.ages}</span>
                </div>
                <h3 className="text-sm font-semibold text-txt mb-1 relative z-10">{mod.title}</h3>
                <p className="text-xs text-txt-off leading-relaxed mb-4 relative z-10">{mod.desc}</p>
                <button className="flex items-center gap-1 text-xs font-semibold text-accent group-hover:gap-2 transition-all relative z-10">
                  Start Learning <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ── Section 2: Quick Quiz ──────────────────────────────────── */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.15 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="font-mono text-[10px] font-semibold text-amber-400 uppercase tracking-label mb-1">CHALLENGE</p>
          <h2 className="text-lg font-bold text-txt mb-4">Quick Quiz</h2>
          <QuizComponent />
        </motion.section>

        {/* ── Section 3: Video Corner ────────────────────────────────── */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.15 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="font-mono text-[10px] font-semibold text-amber-400 uppercase tracking-label mb-1">WATCH & LEARN</p>
          <h2 className="text-lg font-bold text-txt mb-4">Video Corner</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {VIDEOS.map((video, i) => (
              <motion.div
                key={video.title}
                initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="rounded-card bg-card border border-line overflow-hidden hover:border-line-hover transition-colors cursor-pointer group"
              >
                {/* Thumbnail placeholder */}
                <div className="relative h-32 bg-gradient-to-br from-s2 to-card flex items-center justify-center">
                  <div className="w-12 h-12 rounded-full bg-accent/20 backdrop-blur-sm flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Play className="w-5 h-5 text-accent ml-0.5" />
                  </div>
                  <div className="absolute bottom-2 right-2 bg-black/60 text-txt text-[10px] px-1.5 py-0.5 rounded flex items-center gap-1">
                    <Clock className="w-2.5 h-2.5" />
                    {video.duration}
                  </div>
                </div>
                <div className="p-3">
                  <p className="text-xs font-medium text-txt-off leading-snug">{video.title}</p>
                </div>
              </motion.div>
            ))}
          </div>
          <p className="text-[10px] text-txt-muted mt-3 text-center">
            More videos coming soon!
          </p>
        </motion.section>
      </div>
    </div>
  );
}

/* ── Quiz Component ───────────────────────────────────────────────────── */
function QuizComponent() {
  const [current, setCurrent] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);
  const [showExplain, setShowExplain] = useState(false);

  const q = QUIZ_QUESTIONS[current];

  const handleSelect = (idx: number) => {
    if (selected !== null) return;
    setSelected(idx);
    setShowExplain(true);
    if (idx === q.correct) setScore((s) => s + 1);
  };

  const handleNext = () => {
    if (current + 1 >= QUIZ_QUESTIONS.length) {
      setFinished(true);
    } else {
      setCurrent((c) => c + 1);
      setSelected(null);
      setShowExplain(false);
    }
  };

  const handleRestart = () => {
    setCurrent(0);
    setSelected(null);
    setScore(0);
    setFinished(false);
    setShowExplain(false);
  };

  if (finished) {
    const pct = Math.round((score / QUIZ_QUESTIONS.length) * 100);
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="rounded-card bg-card border border-line p-6 text-center max-w-md mx-auto"
      >
        <Star className="w-10 h-10 text-amber-400 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-txt mb-1">Quiz Complete!</h3>
        <p className="text-3xl font-extrabold text-accent mb-2">{score}/{QUIZ_QUESTIONS.length}</p>
        <p className="text-sm text-txt-off mb-4">
          {pct >= 80 ? 'Amazing! You\'re a money genius!' : pct >= 60 ? 'Great job! Keep learning!' : 'Good try! Review the lessons and try again.'}
        </p>
        <button
          onClick={handleRestart}
          className="btn-primary text-sm"
        >
          Try Again
        </button>
      </motion.div>
    );
  }

  return (
    <div className="rounded-card bg-card border border-line p-5 max-w-lg mx-auto">
      {/* Progress */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs text-txt-muted">Question {current + 1} of {QUIZ_QUESTIONS.length}</span>
        <span className="text-xs text-accent font-semibold">Score: {score}</span>
      </div>
      <div className="h-1 rounded-full bg-s2 mb-5 overflow-hidden border border-line">
        <div
          className="h-full bg-accent rounded-full transition-all"
          style={{ width: `${((current + 1) / QUIZ_QUESTIONS.length) * 100}%` }}
        />
      </div>

      <h3 className="text-sm font-semibold text-txt mb-4">{q.q}</h3>

      <div className="space-y-2">
        {q.options.map((opt, idx) => {
          let style = 'bg-s2 border-line text-txt-off hover:border-line-hover hover:text-txt';
          if (selected !== null) {
            if (idx === q.correct) style = 'bg-accent/10 border-accent/40 text-accent';
            else if (idx === selected) style = 'bg-red-500/10 border-red-500/40 text-red-400';
            else style = 'bg-s2 border-line text-txt-muted';
          }
          return (
            <button
              key={idx}
              onClick={() => handleSelect(idx)}
              disabled={selected !== null}
              className={`w-full text-left px-4 py-3 rounded-card border text-xs font-medium transition-all ${style}`}
            >
              <span className="inline-block w-5 text-txt-muted mr-1">{String.fromCharCode(97 + idx)})</span>
              {opt}
              {selected !== null && idx === q.correct && <CheckCircle2 className="w-4 h-4 inline ml-2 text-accent" />}
            </button>
          );
        })}
      </div>

      <AnimatePresence>
        {showExplain && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 overflow-hidden"
          >
            <div className="bg-s1 rounded-card p-3 text-xs text-txt-off border border-line">
              {q.explain}
            </div>
            <button
              onClick={handleNext}
              className="mt-3 w-full btn-primary text-xs"
            >
              {current + 1 >= QUIZ_QUESTIONS.length ? 'See Results' : 'Next Question'}
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
