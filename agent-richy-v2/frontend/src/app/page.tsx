'use client';

import React, { useRef, useEffect, useState } from 'react';
import Link from 'next/link';
import { motion, useInView } from 'framer-motion';
import {
  ArrowRight,
  ChevronRight,
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
  '6 Specialist Agents',
  '$847 Avg. Annual Savings',
  '24/7 Always Available',
  '100% Free to Start',
  '10+ Financial Calculators',
  '<2s Response Time',
];

/* ── Why Agent Richy rows ─────────────────────────────────────────── */
const WHY_ROWS = [
  { num: '01', title: 'Actively Saves You Money', desc: 'Richy doesn\'t just advise — it finds real dollars you\'re leaving on the table.' },
  { num: '02', title: '6 Specialist AI Agents', desc: 'Budget Coach, Spending Optimizer, Tax Strategist, Gas & Transit, Wealth Advisor, Financial Educator.' },
  { num: '03', title: 'Real Numbers Not Generic Tips', desc: 'Every insight is calculated against your actual income, expenses, and goals.' },
  { num: '04', title: 'Builds Wealth Over Time', desc: 'Compound your savings with investing guidance, debt strategies, and long-term planning.' },
];

/* ── How It Works ─────────────────────────────────────────────────── */
const STEPS = [
  { letter: 'T', title: 'Tell', desc: 'Share your income, expenses, and goals. No judgment — just data.', label: 'STEP 01' },
  { letter: 'A', title: 'Analyze', desc: 'Richy\'s specialist agents crunch the numbers and find real savings.', label: 'STEP 02' },
  { letter: 'A', title: 'Act', desc: 'Follow specific, actionable steps. Track your progress over time.', label: 'STEP 03' },
];

/* ── Meet The Agents ──────────────────────────────────────────────── */
const AGENTS_DATA = [
  { letter: 'B', name: 'Budget Coach', desc: 'Creates realistic spending plans based on your actual income.' },
  { letter: 'S', name: 'Spending Optimizer', desc: 'Finds subscriptions and recurring charges you\'re overpaying.' },
  { letter: 'T', name: 'Tax Strategist', desc: 'Estimates taxes, finds deductions, and optimizes your withholding.' },
  { letter: 'G', name: 'Gas & Transit', desc: 'Cuts transportation costs with route and reward optimization.' },
  { letter: 'W', name: 'Wealth Advisor', desc: 'Builds investment portfolios aligned with your risk tolerance.' },
  { letter: 'F', name: 'Financial Educator', desc: 'Makes money concepts fun and accessible for all ages.' },
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
                Agent Richy is your AI financial coach — 6 specialist agents that analyze
                your spending, cut your costs, optimize your taxes, and build your wealth. For free.
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

      {/* ── MEET THE AGENTS ───────────────────────────────────────────── */}
      <section className="bg-bg border-b border-line">
        <div className="max-w-6xl mx-auto px-6 py-24 lg:py-32">
          <FadeUp>
            <p className="section-label">MEET THE AGENTS</p>
            <h2 className="section-title">
              Six specialists. One mission.<br />
              <span className="muted">Your financial freedom.</span>
            </h2>
          </FadeUp>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mt-16">
            {AGENTS_DATA.map((agent, i) => (
              <FadeUp key={agent.name} delay={i * 0.06}>
                <div className="ds-card h-full">
                  <span className="absolute top-3 right-4 text-[80px] font-extrabold text-accent/[.07] leading-none select-none pointer-events-none">{agent.letter}</span>
                  <div className="w-10 h-10 rounded-xl bg-ghost border border-line-hover
                                  flex items-center justify-center text-accent font-bold text-sm mb-4 relative z-10">
                    {agent.letter}
                  </div>
                  <h3 className="text-base font-bold text-txt mb-1 tracking-tight relative z-10">{agent.name}</h3>
                  <p className="text-sm text-txt-off leading-[1.7] relative z-10">{agent.desc}</p>
                </div>
              </FadeUp>
            ))}
          </div>
        </div>
      </section>

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
