'use client';

import React, { useRef, useEffect, useState } from 'react';
import Link from 'next/link';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  ChevronRight,
  ChevronDown,
  Wallet,
  BarChart3,
  TrendingUp,
  Calculator,
  GraduationCap,
  Zap,
} from 'lucide-react';

/* ── Animation helper ─────────────────────────────────────────────── */
function FadeUp({ children, delay = 0, className = '' }: { children: React.ReactNode; delay?: number; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 45 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.9, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ── Marquee items ────────────────────────────────────────────────── */
const MARQUEE_ITEMS = [
  '17 Core Capabilities',
  'All-in-One Finance AI',
  '$847 Avg. Annual Savings',
  '24/7 Always Available',
  '100% Free to Start',
  '10+ Financial Calculators',
  '<2s Response Time',
];

/* ── Why Agent Richy rows ─────────────────────────────────────────── */
const WHY_ROWS = [
  { num: '01', title: 'One Agent, Zero Hand-Offs', desc: 'Other apps make you jump between budgeting tools, coupon sites, and financial calculators. Richy handles everything in one conversation. Ask about coupons at 9am, analyze your budget at noon, plan your taxes at 8pm \u2014 same agent, full context.' },
  { num: '02', title: 'Finds Money You Didn\u2019t Know You Were Losing', desc: 'The average American wastes $133/month on forgotten subscriptions alone. Richy audits every recurring charge, benchmarks your bills against market rates, and generates word-for-word negotiation scripts. He\u2019s found users an average of $847 in annual savings.' },
  { num: '03', title: 'Deals That Actually Work', desc: 'Ask Richy for coupons to any store and he searches, validates, and confidence-scores every code before showing it to you. No expired codes. No fake promos. Every deal is rated Verified, Likely Valid, or Unverified \u2014 so you know what you\u2019re getting.' },
  { num: '04', title: 'Gets Smarter About YOUR Money', desc: 'Richy remembers your financial picture across conversations. He knows your bills, your goals, your spending patterns. The more you use him, the more specific and valuable his recommendations become. Like a financial advisor that costs $0/hour.' },
];

/* ── How It Works ─────────────────────────────────────────────────── */
const STEPS = [
  { letter: 'T', title: 'Tell Richy What\u2019s Up', desc: 'No forms. No spreadsheets. Just tell Richy about your money in plain English. What you earn, what you spend, what\u2019s stressing you out. He picks up context and asks smart follow-ups.', label: 'STEP 01' },
  { letter: 'A', title: 'Get Real Analysis', desc: 'Richy crunches your numbers and finds the gaps \u2014 zombie subscriptions, bills you\u2019re overpaying, deals you\u2019re missing, and money moves that actually fit your life.', label: 'STEP 02' },
  { letter: 'W', title: 'Watch Your Money Grow', desc: 'Follow Richy\u2019s prioritized action plan. Negotiate bills with his scripts. Grab coupons he finds. Hit savings goals he sets. Every dollar saved is tracked and celebrated.', label: 'STEP 03' },
];

/* ── Deep Dive categories ─────────────────────────────────────────── */
const DEEP_DIVE_CATEGORIES = [
  {
    emoji: '💰',
    name: 'Saving Money',
    queries: [
      'I\u2019m spending too much on food delivery. Help me cut back.',
      'Audit all my subscriptions and tell me what to cancel.',
      'I\u2019m paying $95/month for internet. Am I getting ripped off?',
      'Generate a script to negotiate my Verizon bill down.',
      'What\u2019s one thing I can buy today that\u2019ll save me money every month?',
    ],
  },
  {
    emoji: '🏷️',
    name: 'Coupons & Deals',
    queries: [
      'Find me coupons for Target',
      'Any deals on DoorDash right now?',
      'I\u2019m going to Home Depot this weekend. Got any codes?',
      'What are the best restaurant deals near me?',
      'Is there a cheaper alternative to my Adobe subscription?',
    ],
  },
  {
    emoji: '📊',
    name: 'Budgeting',
    queries: [
      'Build me a budget based on my $4,500 take-home pay',
      'What\u2019s my financial health score?',
      'I have $800 in unexpected expenses next month. Help me plan.',
      'What if I got a $500/month raise \u2014 where should that money go?',
      'Show me where my money actually goes each month.',
    ],
  },
  {
    emoji: '📈',
    name: 'Building Wealth',
    queries: [
      'Explain index funds like I\u2019m 16',
      'I have $5,000 saved. What\u2019s the smartest thing to do with it?',
      'Show me my Lifestyle Portfolio based on where I shop',
      'Help me build an investment allocation plan',
      'I have $500/month to invest \u2014 how should I split it?',
      'Map out my 401k allocation',
    ],
  },
  {
    emoji: '🛒',
    name: 'Grocery & Shopping',
    queries: [
      'Here\u2019s my grocery list for the week \u2014 find me the best prices',
      'Where should I buy groceries to save the most?',
      'I need chicken, rice, broccoli, and pasta \u2014 cheapest option?',
      'Optimize my weekly grocery run',
    ],
  },
  {
    emoji: '💡',
    name: 'Smart Decisions',
    queries: [
      'Should I rent or buy in Atlanta on my salary?',
      'Is it worth paying off my car loan early?',
      'Company A offers $85k with great benefits. Company B offers $100k with minimal benefits. Help me compare.',
      'I have 3 credit cards. Which should I pay off first?',
    ],
  },
  {
    emoji: '📊',
    name: 'Market Intelligence',
    queries: [
      'What sectors look strong heading into Q2?',
      'What are analysts saying about healthcare stocks?',
      'Show me the bull and bear case for the tech sector',
      'Any recent analyst upgrades or downgrades?',
      'What does Morningstar say about the energy sector valuation?',
    ],
  },
  {
    emoji: '🏷️',
    name: 'Price Intelligence',
    queries: [
      'I just paid $47 for headphones at Best Buy. Did I overpay?',
      'Where\u2019s the cheapest place to buy groceries near me?',
      'Rank the best stores for electronics',
      'I buy diapers at Target every month. Is there a better option?',
      'Score my subscriptions \u2014 am I getting my money\u2019s worth?',
    ],
  },
  {
    emoji: '🎯',
    name: 'Goals & Planning',
    queries: [
      'I want to save $10,000 for an emergency fund. Simulate it.',
      'How long until I can afford a $25K down payment?',
      'Bill forecast for next month — what\'s coming?',
      'Goal planning: I want to save for a vacation by December',
      'Run a Monte Carlo on my retirement contributions',
    ],
  },
  {
    emoji: '📍',
    name: 'Deals & Receipts',
    queries: [
      'What grocery deals are near me this week?',
      'Analyze my Publix receipt — did I overpay anywhere?',
      'Show me weekly ads for stores near 30518',
      'I just spent $87 at the grocery store. Break it down.',
      'Find local deals on household essentials',
    ],
  },  {
    emoji: '�',
    name: 'Investment Intelligence',
    queries: [
      'Show me the top rated stocks by analyst consensus',
      'What do analysts say about NVDA?',
      'Which sectors are Goldman and JP Morgan overweight on?',
      'What investment themes are the big firms pushing right now?',
      'Show me the bull and bear case for the healthcare sector',
    ],
  },  {
    emoji: '🧒',
    name: 'Kids & Family',
    queries: [
      'Teach my 8-year-old about saving money',
      'Create a savings challenge for my teenager',
      'My kid wants to understand what the stock market is',
      'Help me set up an allowance system',
    ],
  },
];

/* ── Capabilities ─────────────────────────────────────────────────── */
const HERO_CAPABILITIES = [
  {
    bgLetter: 'C',
    label: 'DEAL FINDER',
    title: 'Smart Coupons',
    desc: 'Ask for coupons to any store, restaurant, or service. Richy searches in real-time, validates codes, and shows you the best deals with confidence ratings.',
    stats: ['Verified Codes', 'Real-Time Search', 'Any Store'],
  },
  {
    bgLetter: 'S',
    label: 'SPEND HELPER',
    title: 'Spend Helper',
    desc: 'Tell Richy what you pay for each month. He\'ll find zombie subscriptions, negotiate your bills, and build a savings roadmap sorted by impact.',
    stats: ['Bill Negotiation', 'Subscription Audit', 'Savings Roadmap'],
  },
  {
    bgLetter: 'R',
    label: 'RESEARCH AGGREGATOR',
    title: 'Investment Intelligence',
    desc: 'See what Goldman, JP Morgan, Morningstar, and 10+ major firms think about any stock or sector. Consensus scores, price targets, bull & bear cases — like Rotten Tomatoes for stocks.',
    stats: ['Consensus Scores', 'Sector Views', 'Theme Tracking'],
  },
];

const SMALL_CAPABILITIES = [
  { icon: '▤', title: 'Budget & Cash Flow', desc: 'Personalized budgets, health scores, and cash flow projections with your real numbers.' },
  { icon: '△', title: 'Tax Strategy', desc: 'Deduction finder, bracket optimizer, and quarterly payment calculator. File smarter.' },
  { icon: '◎', title: 'Wealth Education', desc: 'Investment concepts in plain English. Compound interest, index funds, retirement math.' },
  { icon: '⚡', title: 'Smart Cost Cutting', desc: 'Gas optimization, meal planning, insurance shopping, energy audits. Every dollar counts.' },
  { icon: '◇', title: 'Decision Simulator', desc: 'Run the math on real choices: rent vs buy, pay off debt vs invest, job offer comparison.' },
  { icon: '🏷️', title: 'Price Intelligence', desc: 'Compare prices across every major retailer. Find out if you\'re overpaying and where to get the same thing cheaper. Store rankings by category included.' },
  { icon: '🎯', title: 'Goal Simulator', desc: 'Simulate any savings goal with 3 scenarios, milestone timelines, and Monte Carlo probability analysis.' },
  { icon: '📅', title: 'Bill Predictor', desc: 'Predict next month\'s bills, flag cash flow danger zones, and never be surprised by a renewal again.' },
  { icon: '📍', title: 'Local Deal Radar', desc: 'Find the best deals near you, cross-referenced with what you actually buy. Historic lows flagged.' },
  { icon: '🧾', title: 'Receipt Analyzer', desc: 'Break down any purchase by category. Find items you overpaid for and where to get them cheaper.' },
  { icon: '📊', title: 'Analyst Consensus', desc: 'See what Goldman, JP Morgan, Morningstar, and other major firms think about any stock or sector. Consensus scores, price targets, bull & bear cases.' },
  { icon: '🛒', title: 'Grocery Planner', desc: 'Turn any grocery list into an optimized shopping plan. Compare prices across stores, stack coupons, and get clean exportable lists.' },
  { icon: '📐', title: 'Allocation Mapper', desc: 'Organize your investment thinking into a structured plan with ETFs, expense ratios, and monthly schedules across accounts.' },
];

/* ── Footer links ─────────────────────────────────────────────────── */
const FOOTER_COLS = [
  { heading: 'PRODUCT', links: [
    { label: 'Chat', href: '/chat' },
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Calculators', href: '/calculators' },
    { label: 'Kids Zone', href: '/kids' },
  ]},
  { heading: 'COMPANY', links: [
    { label: 'About', href: '#' },
    { label: 'Blog', href: '#' },
    { label: 'Careers', href: '#' },
  ]},
  { heading: 'LEGAL', links: [
    { label: 'Privacy', href: '#' },
    { label: 'Terms', href: '#' },
    { label: 'Security', href: '#' },
  ]},
];

/* ══════════════════════════════════════════════════════════════════════
   LANDING PAGE
   ══════════════════════════════════════════════════════════════════════ */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg text-txt overflow-x-hidden">
      <LandingNav />

      {/* ── HERO ──────────────────────────────────────────────────────── */}
      <header className="relative overflow-hidden bg-bg grid-bg">
        {/* Glowing orbs */}
        <div className="absolute top-[-20%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-accent/[.08] blur-[100px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40vw] h-[40vw] rounded-full bg-accent/[.04] blur-[80px] pointer-events-none" />
        {/* Faded R */}
        <div className="absolute top-[10%] right-[5%] text-[clamp(200px,30vw,500px)] font-extrabold text-accent/[.04] leading-none select-none pointer-events-none">R</div>

        <div className="relative max-w-7xl mx-auto px-6 pt-28 pb-20 lg:pt-40 lg:pb-32">
          <div className="max-w-3xl">
            <FadeUp>
              <div className="badge-pill w-fit mb-8">AI-Powered Financial Coach</div>
            </FadeUp>
            <FadeUp delay={0.06}>
              <h1 className="font-extrabold tracking-tighter leading-[0.97]"
                  style={{ fontSize: 'clamp(44px, 6.5vw, 88px)' }}>
                Your money deserves<br />
                <span className="text-accent">a smarter plan.</span>
              </h1>
            </FadeUp>
            <FadeUp delay={0.12}>
              <p className="mt-6 text-[15px] sm:text-base text-txt-off max-w-xl leading-[1.7]">
                Agent Richy is your all-in-one AI financial coach — he analyzes
                your spending, finds deals, cuts your bills, optimizes your taxes, and builds your wealth. For free.
              </p>
            </FadeUp>
            <FadeUp delay={0.18}>
              <div className="mt-10 flex flex-wrap gap-4">
                <Link href="/chat">
                  <button className="btn-primary inline-flex items-center gap-2">
                    Start Chatting <ArrowRight className="w-4 h-4" />
                  </button>
                </Link>
                <a href="#how-it-works">
                  <button className="btn-secondary">See How It Works</button>
                </a>
              </div>
            </FadeUp>
          </div>
        </div>
      </header>

      {/* ── STATS MARQUEE ─────────────────────────────────────────────── */}
      <section className="border-y border-line bg-s1 py-5 overflow-hidden">
        <div className="animate-marquee marquee-track">
          {[...MARQUEE_ITEMS, ...MARQUEE_ITEMS].map((item, i) => (
            <span key={i} className="flex items-center gap-3 px-8 text-sm font-medium text-txt-off whitespace-nowrap">
              <span className="text-accent text-xs">◆</span> {item}
            </span>
          ))}
        </div>
      </section>

      {/* ── WHY AGENT RICHY ───────────────────────────────────────────── */}
      <section className="bg-bg border-b border-line">
        <div className="max-w-6xl mx-auto px-6 py-24 lg:py-32">
          <FadeUp>
            <p className="section-label">WHY AGENT RICHY</p>
            <h2 className="section-title">
              Smarter tools, real results.<br />
              <span className="muted">Not another generic budgeting app.</span>
            </h2>
          </FadeUp>
          <div className="mt-16 space-y-0">
            {WHY_ROWS.map((row, i) => (
              <FadeUp key={row.num} delay={i * 0.06}>
                <div className="flex items-start gap-6 sm:gap-10 py-8 border-t border-line group">
                  <span className="font-mono text-accent text-sm font-semibold tracking-label mt-1 flex-shrink-0">{row.num}</span>
                  <div>
                    <h3 className="text-lg sm:text-xl font-bold text-txt mb-2 tracking-tight">{row.title}</h3>
                    <p className="text-sm text-txt-off leading-[1.7] max-w-xl">{row.desc}</p>
                  </div>
                </div>
              </FadeUp>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ──────────────────────────────────────────────── */}
      <section id="how-it-works" className="bg-s1 border-b border-line">
        <div className="max-w-6xl mx-auto px-6 py-24 lg:py-32">
          <FadeUp>
            <p className="section-label">HOW IT WORKS</p>
            <h2 className="section-title">
              Three steps to financial clarity.<br />
              <span className="muted">No spreadsheets required.</span>
            </h2>
          </FadeUp>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-16">
            {STEPS.map((step, i) => (
              <FadeUp key={step.title} delay={i * 0.08}>
                <div className="ds-card h-full">
                  <span className="absolute top-4 right-5 text-[120px] font-extrabold text-accent/[.06] leading-none select-none pointer-events-none">{step.letter}</span>
                  <p className="section-label !mb-4">{step.label}</p>
                  <h3 className="text-xl font-bold text-txt mb-3 tracking-tight relative z-10">{step.title}</h3>
                  <p className="text-sm text-txt-off leading-[1.7] relative z-10">{step.desc}</p>
                </div>
              </FadeUp>
            ))}
          </div>
        </div>
      </section>

      {/* ── WHAT RICHY CAN DO ─────────────────────────────────────────── */}
      <section className="bg-bg border-b border-line">
        <div className="max-w-6xl mx-auto px-6 py-24 lg:py-32">
          <FadeUp>
            <p className="section-label">CAPABILITIES</p>
            <h1 className="section-title">
              One agent. <span className="text-accent">Every angle.</span>
            </h1>
            <p className="text-txt-off text-lg max-w-2xl mx-auto text-center mb-16">
              Richy doesn&apos;t hand you off to specialists. He handles budgets, finds deals,
              cuts bills, teaches your kids about money, and simulates your biggest financial
              decisions — all in one conversation.
            </p>
          </FadeUp>

          {/* Top row — 3 hero capability cards */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5">
            {HERO_CAPABILITIES.map((cap, i) => (
              <FadeUp key={cap.title} delay={i * 0.08}>
                <div className="bg-card border border-line rounded-card p-8 relative overflow-hidden h-full">
                  <span className="absolute top-2 right-4 text-[120px] font-black text-accent/[0.04] leading-none select-none pointer-events-none">
                    {cap.bgLetter}
                  </span>
                  <p className="font-mono text-accent text-xs uppercase tracking-label mb-3 relative z-10">
                    {cap.label}
                  </p>
                  <h3 className="text-xl font-bold text-txt mb-3 tracking-tight relative z-10">
                    {cap.title}
                  </h3>
                  <p className="text-sm text-txt-off leading-[1.7] mb-5 relative z-10">
                    {cap.desc}
                  </p>
                  <div className="flex flex-wrap gap-2 relative z-10">
                    {cap.stats.map((stat) => (
                      <span
                        key={stat}
                        className="text-xs font-mono text-accent/80 bg-ghost border border-line px-2.5 py-1 rounded-full"
                      >
                        {stat}
                      </span>
                    ))}
                  </div>
                </div>
              </FadeUp>
            ))}
          </div>

          {/* Bottom row — 6 smaller capability cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {SMALL_CAPABILITIES.map((cap, i) => (
              <FadeUp key={cap.title} delay={i * 0.06}>
                <div className="bg-card border border-line rounded-card p-6
                                hover:border-line-hover hover:-translate-y-[3px]
                                transition-all duration-300 h-full">
                  <span className="text-3xl mb-3 block">{cap.icon}</span>
                  <h3 className="text-txt text-lg font-semibold mb-1 tracking-tight">{cap.title}</h3>
                  <p className="text-txt-off text-sm leading-relaxed">{cap.desc}</p>
                </div>
              </FadeUp>
            ))}
          </div>
        </div>
      </section>

      {/* ── DEEP DIVE ─────────────────────────────────────────────────── */}
      <DeepDiveSection />

      {/* ── LIVE PREVIEW ──────────────────────────────────────────────── */}
      <section className="bg-s1 border-b border-line">
        <div className="max-w-6xl mx-auto px-6 py-24 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <FadeUp>
              <p className="section-label">LIVE PREVIEW</p>
              <h2 className="section-title !text-[clamp(28px,3.5vw,48px)]">
                See Richy in action.<br />
                <span className="muted">Real conversations, real savings.</span>
              </h2>
              <p className="mt-6 text-sm text-txt-off leading-[1.7] max-w-md">
                In this example, Richy identifies <strong className="text-accent font-semibold">$1,403/year</strong> in
                unused subscriptions a user didn&apos;t even know about.
              </p>
              <Link href="/chat" className="mt-8 inline-block">
                <button className="btn-primary inline-flex items-center gap-2">
                  Try It Yourself <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
            </FadeUp>
            <FadeUp delay={0.12}>
              <ChatPreview />
            </FadeUp>
          </div>
        </div>
      </section>

      {/* ── CTA BANNER ────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-bg border-b border-line">
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-accent/[.12] rounded-full blur-[100px] pointer-events-none" />
        <div className="relative max-w-4xl mx-auto px-6 py-24 lg:py-32 text-center">
          <FadeUp>
            <p className="section-label">GET STARTED</p>
            <h2 className="section-title !text-[clamp(32px,4.5vw,64px)]">
              Ready to take control?
            </h2>
            <p className="mt-4 text-txt-off max-w-lg mx-auto text-[15px] leading-[1.7]">
              Join thousands already building wealth with Agent Richy. It&apos;s free, it&apos;s smart, and it actually works.
            </p>
            <div className="mt-10">
              <Link href="/chat">
                <button className="btn-primary inline-flex items-center gap-2">
                  Chat with Richy Now <ChevronRight className="w-4 h-4" />
                </button>
              </Link>
            </div>
          </FadeUp>
        </div>
      </section>

      {/* ── FOOTER ────────────────────────────────────────────────────── */}
      <footer className="bg-bg border-t border-line">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-12">
            {/* Logo + description */}
            <div className="md:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-accent-dark
                                flex items-center justify-center text-black text-sm font-extrabold">R</div>
                <span className="text-lg font-bold text-txt tracking-tight">Agent Richy</span>
              </div>
              <p className="text-sm text-txt-muted leading-[1.7] max-w-xs">
                AI-powered personal finance platform that helps you save more, spend smarter, and build real wealth.
              </p>
            </div>
            {/* Link columns */}
            {FOOTER_COLS.map((col) => (
              <div key={col.heading}>
                <p className="font-mono text-xs font-semibold text-accent uppercase tracking-label mb-4">{col.heading}</p>
                <div className="space-y-3">
                  {col.links.map((link) => (
                    <Link key={link.label} href={link.href}
                          className="block text-sm text-txt-off hover:text-txt transition-colors">
                      {link.label}
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-12 pt-6 border-t border-line flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <p className="text-xs text-txt-muted">&copy; 2026 Agent Richy. All rights reserved.</p>
            <p className="text-xs text-txt-muted">Powered by Vert AI</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

/* ── Deep Dive accordion section ──────────────────────────────────── */
function DeepDiveSection() {
  const [open, setOpen] = useState<number | null>(null);

  const toggle = (i: number) => setOpen(open === i ? null : i);

  return (
    <section className="bg-s1 border-b border-line">
      <div className="max-w-4xl mx-auto px-6 py-24 lg:py-32">
        <FadeUp>
          <p className="section-label">DEEP DIVE</p>
          <h1 className="section-title">
            What people ask Richy. <span className="muted">Every day.</span>
          </h1>
        </FadeUp>

        <div className="mt-16 space-y-3">
          {DEEP_DIVE_CATEGORIES.map((cat, i) => {
            const isOpen = open === i;
            return (
              <FadeUp key={cat.name} delay={i * 0.04}>
                <div>
                  {/* Header */}
                  <button
                    onClick={() => toggle(i)}
                    className={`w-full flex items-center justify-between bg-card border rounded-card px-5 py-4
                               cursor-pointer transition-colors
                               ${isOpen
                                 ? 'border-line-hover rounded-b-none'
                                 : 'border-line hover:border-line-hover'}`}
                  >
                    <span className="flex items-center gap-3 text-txt font-medium text-sm">
                      <span className="text-lg">{cat.emoji}</span>
                      {cat.name}
                    </span>
                    <motion.span
                      animate={{ rotate: isOpen ? 180 : 0 }}
                      transition={{ duration: 0.2 }}
                      className="text-txt-muted"
                    >
                      <ChevronDown className="w-4 h-4" />
                    </motion.span>
                  </button>

                  {/* Expanded content */}
                  <AnimatePresence initial={false}>
                    {isOpen && (
                      <motion.div
                        key={`panel-${i}`}
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.25, ease: 'easeInOut' }}
                        className="overflow-hidden"
                      >
                        <div className="bg-s1 rounded-b-card border-x border-b border-line px-5 py-4">
                          {cat.queries.map((q, qi) => (
                            <p
                              key={qi}
                              className={`text-txt-off text-sm py-2.5 ${
                                qi < cat.queries.length - 1 ? 'border-b border-line' : ''
                              }`}
                            >
                              &ldquo;{q}&rdquo;
                            </p>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </FadeUp>
            );
          })}
        </div>
      </div>
    </section>
  );
}

/* ── Chat Preview (mock) ──────────────────────────────────────────── */
function ChatPreview() {
  return (
    <div className="rounded-[14px] border border-line bg-card overflow-hidden shadow-2xl shadow-black/40">
      {/* Title bar */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-line bg-s1">
        <span className="w-3 h-3 rounded-full bg-red-500/60" />
        <span className="w-3 h-3 rounded-full bg-yellow-500/60" />
        <span className="w-3 h-3 rounded-full bg-accent/60" />
        <span className="ml-2 text-xs text-txt-muted font-mono">agent-richy — chat</span>
      </div>
      {/* Messages */}
      <div className="p-5 space-y-4 bg-s1">
        {/* User */}
        <div className="flex justify-end">
          <div className="rounded-2xl rounded-br-md bg-accent text-black text-sm px-4 py-2.5 max-w-[80%] font-medium">
            I feel like I&apos;m wasting money on subscriptions. Can you check?
          </div>
        </div>
        {/* Richy */}
        <div className="flex gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent to-accent-dark flex items-center justify-center text-[10px] font-extrabold text-black flex-shrink-0 mt-0.5">R</div>
          <div className="rounded-2xl rounded-bl-md bg-card border border-line text-txt text-sm px-4 py-2.5 max-w-[80%] leading-relaxed">
            I found <strong className="text-accent">3 unused subscriptions</strong> totaling <strong className="text-accent">$1,403/year</strong>:
            <br />• Adobe Creative Cloud — $54.99/mo (unused 4 months)
            <br />• Peloton Digital — $12.99/mo (no logins in 6 months)
            <br />• WSJ Premium — $48.75/mo (1 article in 3 months)
          </div>
        </div>
        {/* Typing */}
        <div className="flex gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent to-accent-dark flex items-center justify-center text-[10px] font-extrabold text-black flex-shrink-0 mt-0.5">R</div>
          <div className="rounded-2xl rounded-bl-md bg-card border border-line px-4 py-3 flex gap-1.5">
            <span className="w-2 h-2 rounded-full bg-accent/60 animate-bounce [animation-delay:0ms]" />
            <span className="w-2 h-2 rounded-full bg-accent/60 animate-bounce [animation-delay:150ms]" />
            <span className="w-2 h-2 rounded-full bg-accent/60 animate-bounce [animation-delay:300ms]" />
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Landing Navbar ───────────────────────────────────────────────── */
function LandingNav() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 h-[72px] transition-all duration-300
      ${scrolled ? 'bg-[rgba(0,0,0,.82)] backdrop-blur-[24px] border-b border-line' : 'bg-transparent'}`}>
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-accent-dark
                          flex items-center justify-center text-black text-sm font-extrabold">R</div>
          <span className="text-base font-bold text-txt tracking-tight">Agent Richy</span>
        </Link>
        <div className="hidden md:flex items-center gap-8">
          {['Home', 'Chat', 'Dashboard', 'Calculators', 'Kids Zone'].map((label) => {
            const href = label === 'Home' ? '/' : label === 'Kids Zone' ? '/kids' : `/${label.toLowerCase()}`;
            return (
              <Link key={label} href={href} className="text-sm text-txt-off hover:text-txt transition-colors">{label}</Link>
            );
          })}
        </div>
        <div className="hidden md:block">
          <Link href="/chat">
            <button className="px-6 py-2.5 text-sm rounded-[10px] bg-accent text-black font-extrabold
                               shadow-[0_0_30px_rgba(0,232,123,.18)] hover:brightness-110 transition-all">
              Launch App
            </button>
          </Link>
        </div>
        <button className="md:hidden flex flex-col gap-1.5 p-3 min-w-[44px] min-h-[44px] items-center justify-center"
                onClick={() => setMobileOpen(!mobileOpen)} aria-label="Toggle menu">
          <span className={`block w-5 h-0.5 bg-txt-off transition-transform ${mobileOpen ? 'rotate-45 translate-y-2' : ''}`} />
          <span className={`block w-5 h-0.5 bg-txt-off transition-opacity ${mobileOpen ? 'opacity-0' : ''}`} />
          <span className={`block w-5 h-0.5 bg-txt-off transition-transform ${mobileOpen ? '-rotate-45 -translate-y-2' : ''}`} />
        </button>
      </div>
      {mobileOpen && (
        <motion.div
          initial={{ opacity: 0, x: '100%' }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: '100%' }}
          className="md:hidden fixed inset-y-0 right-0 w-64 bg-s1 border-l border-line pt-20 px-6 z-40"
        >
          <div className="flex flex-col gap-5">
            {[{ label: 'Home', href: '/' }, { label: 'Chat', href: '/chat' }, { label: 'Dashboard', href: '/dashboard' }, { label: 'Calculators', href: '/calculators' }, { label: 'Kids Zone', href: '/kids' }].map((link) => (
              <Link key={link.href} href={link.href} className="text-base text-txt-off hover:text-accent transition-colors" onClick={() => setMobileOpen(false)}>
                {link.label}
              </Link>
            ))}
            <Link href="/chat" onClick={() => setMobileOpen(false)}>
              <button className="mt-4 w-full py-3 rounded-[10px] bg-accent text-black font-extrabold text-sm
                                 shadow-[0_0_30px_rgba(0,232,123,.18)]">Launch App</button>
            </Link>
          </div>
        </motion.div>
      )}
    </nav>
  );
}
