'use client';

import { motion } from 'framer-motion';
import ExportableCard from './ExportableCard';
import ProactiveAlertCard from './ProactiveAlertCard';
import type { WeeklyDigest } from '@/lib/predictiveEngine';

/* ── Helpers ───────────────────────────────────────────────────────── */

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function fmtDetail(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

function dateRange(weekOf: string): string {
  const start = new Date(weekOf);
  const end = new Date(start);
  end.setDate(end.getDate() + 6);
  const opts: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' };
  return `${start.toLocaleDateString('en-US', opts)} – ${end.toLocaleDateString('en-US', opts)}, ${end.getFullYear()}`;
}

/* ── Animation ─────────────────────────────────────────────────────── */

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
};

/* ── Arrow indicators ──────────────────────────────────────────────── */

function TrendArrow({ value }: { value: number }) {
  if (value > 0)
    return <span className="text-accent text-lg">↑ +{value}</span>;
  if (value < 0)
    return <span className="text-red-400 text-lg">↓ {value}</span>;
  return <span className="text-muted text-lg">→ 0</span>;
}

/* ── Stat card ─────────────────────────────────────────────────────── */

function StatCell({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <motion.div
      variants={fadeUp}
      className="bg-card border border-line rounded-card p-3 text-center"
    >
      <p className="text-muted text-[10px] font-mono uppercase tracking-wider">
        {label}
      </p>
      <p className={`text-lg font-semibold mt-1 ${accent ? 'text-accent' : 'text-txt'}`}>
        {value}
      </p>
    </motion.div>
  );
}

/* ── Build export data ─────────────────────────────────────────────── */

function buildExportData(d: WeeklyDigest) {
  const lines = [
    `Weekly Money Report — ${dateRange(d.weekOf)}`,
    '',
    `Health Score Change: ${d.healthScoreChange >= 0 ? '+' : ''}${d.healthScoreChange}`,
    `Spent: ${fmtDetail(d.spendingThisWeek)}`,
    `Saved: ${fmtDetail(d.savingsThisWeek)}`,
    `Streak: ${d.streakDays} days`,
    '',
  ];

  if (d.winsThisWeek.length > 0) {
    lines.push('Wins:');
    d.winsThisWeek.forEach((w) => lines.push(`  ✓ ${w}`));
    lines.push('');
  }

  if (d.goalsProgress.length > 0) {
    lines.push('Goals:');
    d.goalsProgress.forEach((g) =>
      lines.push(`  ${g.name}: ${Math.round(g.progress)}% (${g.change >= 0 ? '+' : ''}${Math.round(g.change)}%)`),
    );
    lines.push('');
  }

  if (d.upcomingBills.length > 0) {
    lines.push('Upcoming Bills:');
    d.upcomingBills.forEach((b) =>
      lines.push(`  ${b.name}: ${fmtDetail(b.amount)} on ${b.date}`),
    );
    lines.push('');
  }

  lines.push(`Total Saved Since Joining: ${fmtDetail(d.totalSavedSinceJoining)}`);

  const text = lines.join('\n');
  return { clipboard: text, formatted: text };
}

/* ── Component ─────────────────────────────────────────────────────── */

interface Props {
  digest: WeeklyDigest;
}

export default function WeeklyDigestCard({ digest }: Props) {
  const d = digest;
  const dailySaved =
    d.streakDays > 0 ? d.totalSavedSinceJoining / d.streakDays : 0;

  return (
    <ExportableCard
      title="Weekly Money Report"
      exportData={buildExportData(d)}
    >
      <div className="overflow-hidden rounded-t-card">
        {/* ── HEADER ──────────────────────────────────────────── */}
        <div className="bg-gradient-to-r from-s1 to-card p-6">
          <p className="font-mono text-accent text-xs tracking-widest uppercase">
            Your Weekly Money Report
          </p>
          <p className="text-txt text-lg font-semibold mt-1">
            {dateRange(d.weekOf)}
          </p>

          <div className="flex items-end gap-3 mt-3">
            <span className="text-4xl font-bold text-txt leading-none">
              {d.healthScoreChange >= 0
                ? d.healthScoreChange
                : Math.abs(d.healthScoreChange)}
            </span>
            <TrendArrow value={d.healthScoreChange} />
            <span className="text-muted text-xs mb-1">health score change</span>
          </div>
        </div>

        {/* ── WINS ────────────────────────────────────────────── */}
        {d.winsThisWeek.length > 0 && (
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="show"
            className="bg-accent/5 rounded-lg p-4 mx-4 mt-4"
          >
            <p className="font-mono text-accent text-xs tracking-widest uppercase mb-2">
              🎉 Wins This Week
            </p>
            <ul className="space-y-1.5">
              {d.winsThisWeek.map((win, i) => (
                <li key={i} className="text-off text-sm flex items-start gap-2">
                  <span className="text-accent mt-0.5 shrink-0">✓</span>
                  {win}
                </li>
              ))}
            </ul>
          </motion.div>
        )}

        {/* ── STATS GRID ──────────────────────────────────────── */}
        <motion.div
          variants={stagger}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 sm:grid-cols-4 gap-3 mx-4 mt-4"
        >
          <StatCell label="Spent" value={fmt(d.spendingThisWeek)} />
          <StatCell label="Saved" value={fmt(d.savingsThisWeek)} accent />
          <StatCell
            label="Goals"
            value={
              d.goalsProgress.length > 0
                ? `${Math.round(d.goalsProgress.reduce((s, g) => s + g.progress, 0) / d.goalsProgress.length)}%`
                : '—'
            }
          />
          <StatCell label="Streak" value={`${d.streakDays}d`} />
        </motion.div>

        {/* ── ACTIVE ALERTS ───────────────────────────────────── */}
        {d.activeAlerts.length > 0 && (
          <div className="mx-4 mt-4 space-y-2">
            <p className="font-mono text-muted text-[10px] tracking-widest uppercase">
              Alerts
            </p>
            {d.activeAlerts.map((a) => (
              <ProactiveAlertCard key={a.id} alert={a} compact />
            ))}
          </div>
        )}

        {/* ── UPCOMING BILLS ──────────────────────────────────── */}
        {d.upcomingBills.length > 0 && (
          <div className="mx-4 mt-4">
            <p className="font-mono text-muted text-[10px] tracking-widest uppercase mb-2">
              Bills Coming Up
            </p>
            <div className="space-y-1.5">
              {d.upcomingBills.map((b, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-off">{b.name}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-muted text-xs">{b.date}</span>
                    <span className="text-txt font-medium">{fmtDetail(b.amount)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── UPCOMING OPPORTUNITIES ──────────────────────────── */}
        {d.upcomingOpportunities.length > 0 && (
          <div className="mx-4 mt-4">
            <p className="font-mono text-muted text-[10px] tracking-widest uppercase mb-2">
              Opportunities
            </p>
            <ul className="space-y-1">
              {d.upcomingOpportunities.map((opp, i) => (
                <li key={i} className="text-off text-sm flex items-start gap-2">
                  <span className="text-accent mt-0.5 shrink-0">→</span>
                  {opp}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* ── TOTAL IMPACT ────────────────────────────────────── */}
        <div className="bg-s1 rounded-card p-4 mx-4 mt-4 mb-4 text-center">
          <p className="text-accent text-xl font-bold">
            Since joining Richy, you&apos;ve saved {fmt(d.totalSavedSinceJoining)}
          </p>
          {dailySaved > 0 && (
            <p className="text-off text-sm mt-1">
              That&apos;s {fmtDetail(dailySaved)} per day of membership
            </p>
          )}
          {d.totalSavedThisMonth > 0 && (
            <p className="text-muted text-xs mt-1">
              {fmt(d.totalSavedThisMonth)} saved this month alone
            </p>
          )}
        </div>
      </div>
    </ExportableCard>
  );
}
