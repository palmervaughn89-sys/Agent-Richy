'use client';

import React from 'react';
import { motion } from 'framer-motion';
import type { AdvisorMatch } from '@/lib/advisorMarketplace';

/* ── Helpers ───────────────────────────────────────────────────────── */

function feeLabel(structure: string): string {
  const map: Record<string, string> = {
    fee_only: 'Fee-Only',
    fee_based: 'Fee-Based',
    commission: 'Commission',
    flat_fee: 'Flat Fee',
    hourly: 'Hourly',
  };
  return map[structure] ?? structure;
}

function formatLabel(f: string): string {
  const map: Record<string, string> = {
    in_person: 'In Person',
    video: 'Video',
    phone: 'Phone',
  };
  return map[f] ?? f;
}

function scoreColor(score: number): string {
  if (score >= 85) return 'text-accent border-accent/40 bg-accent/10';
  if (score >= 70) return 'text-blue-400 border-blue-400/40 bg-blue-400/10';
  if (score >= 50) return 'text-amber-400 border-amber-400/40 bg-amber-400/10';
  return 'text-red-400 border-red-400/40 bg-red-400/10';
}

function Stars({ rating, max = 5 }: { rating: number; max?: number }) {
  return (
    <span className="flex items-center gap-0.5">
      {Array.from({ length: max }, (_, i) => (
        <span key={i} className={i < Math.round(rating) ? 'text-accent' : 'text-s2'}>
          ★
        </span>
      ))}
      <span className="ml-1 text-off text-xs">{rating.toFixed(1)}</span>
    </span>
  );
}

/* ── Component ─────────────────────────────────────────────────────── */

interface Props {
  match: AdvisorMatch;
}

export default function AdvisorMatchCard({ match }: Props) {
  const { advisor, matchScore, matchReasons, estimatedCost, nextStep } = match;
  const initial = advisor.name.charAt(0).toUpperCase();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="bg-card border border-line rounded-card p-5 w-full"
    >
      {/* ── Advisor Header ─────────────────────────────────────────── */}
      <div className="flex gap-4">
        {/* Photo */}
        <div className="bg-s2 rounded-full w-16 h-16 flex items-center justify-center text-accent text-2xl font-bold shrink-0">
          {advisor.photo ? (
            <img src={advisor.photo} alt={advisor.name} className="w-full h-full rounded-full object-cover" />
          ) : (
            initial
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="text-txt text-lg font-semibold leading-tight flex items-center gap-2">
                {advisor.name}
                {advisor.verified && (
                  <span className="bg-accent/10 text-accent text-[10px] font-mono tracking-wider px-1.5 py-0.5 rounded-full">
                    VERIFIED
                  </span>
                )}
              </h3>
              <p className="text-off text-sm mt-0.5">
                {advisor.title} · {advisor.firm}
              </p>
            </div>

            {/* Match Score */}
            <div className={`flex items-center justify-center w-12 h-12 rounded-full border-2 text-sm font-bold shrink-0 ${scoreColor(matchScore)}`}>
              {matchScore}%
            </div>
          </div>

          {/* Certifications */}
          <div className="flex flex-wrap gap-1.5 mt-2">
            {advisor.certifications.map((cert) => (
              <span key={cert} className="badge-pill text-[10px]">
                {cert.replace('_', ' ')}
              </span>
            ))}
          </div>

          {/* Stars + Reviews */}
          <div className="flex items-center gap-2 mt-2">
            <Stars rating={advisor.rating} />
            <span className="text-muted text-xs">({advisor.reviewCount} reviews)</span>
          </div>
        </div>
      </div>

      {/* ── Match Reasons ──────────────────────────────────────────── */}
      <div className="mt-4">
        <p className="font-mono text-accent text-xs tracking-widest mb-2">WHY THIS MATCH</p>
        <ul className="space-y-1">
          {matchReasons.map((reason, i) => (
            <li key={i} className="text-off text-sm flex items-start gap-2">
              <span className="text-accent mt-0.5 shrink-0">✓</span>
              {reason}
            </li>
          ))}
        </ul>
      </div>

      {/* ── Key Details Grid ───────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-3 mt-4">
        <div className="bg-s1 rounded-lg p-3">
          <p className="text-muted text-[10px] font-mono tracking-wider">FEE STRUCTURE</p>
          <p className="text-txt text-sm font-medium mt-0.5">{feeLabel(advisor.feeStructure)}</p>
          <p className="text-off text-xs mt-0.5">{advisor.feeDetails}</p>
        </div>
        <div className="bg-s1 rounded-lg p-3">
          <p className="text-muted text-[10px] font-mono tracking-wider">EXPERIENCE</p>
          <p className="text-txt text-sm font-medium mt-0.5">{advisor.yearsExperience} years</p>
          <p className="text-off text-xs mt-0.5">{advisor.registeredWith.join(', ')}</p>
        </div>
        <div className="bg-s1 rounded-lg p-3">
          <p className="text-muted text-[10px] font-mono tracking-wider">MEETING FORMAT</p>
          <p className="text-txt text-sm font-medium mt-0.5">
            {advisor.meetingFormat.map(formatLabel).join(', ')}
          </p>
        </div>
        <div className="bg-s1 rounded-lg p-3">
          <p className="text-muted text-[10px] font-mono tracking-wider">AVAILABILITY</p>
          <p className="text-txt text-sm font-medium mt-0.5">
            {advisor.acceptingNewClients ? 'Accepting Clients' : 'Waitlist'}
          </p>
          <p className="text-off text-xs mt-0.5">{advisor.responseTime}</p>
        </div>
      </div>

      {/* ── Advisor's Approach ─────────────────────────────────────── */}
      <div className="mt-4 bg-s1 rounded-lg p-3">
        <p className="text-muted text-[10px] font-mono tracking-wider mb-1">ADVISOR&apos;S PHILOSOPHY</p>
        <p className="text-off text-sm italic leading-relaxed">&quot;{advisor.philosophy}&quot;</p>
      </div>

      {/* ── Cost + Next Step ───────────────────────────────────────── */}
      <div className="mt-4 bg-s1 rounded-lg p-3 flex items-center justify-between">
        <div>
          <p className="text-muted text-[10px] font-mono tracking-wider">ESTIMATED COST</p>
          <p className="text-txt text-sm font-medium mt-0.5">{estimatedCost}</p>
        </div>
        <div className="text-right">
          <p className="text-muted text-[10px] font-mono tracking-wider">NEXT STEP</p>
          <p className="text-off text-xs mt-0.5">{nextStep}</p>
        </div>
      </div>

      {/* ── CTAs ───────────────────────────────────────────────────── */}
      <div className="mt-4 space-y-2">
        <button className="btn-primary w-full text-sm">Schedule Free Intro Call</button>
        <button className="btn-secondary w-full text-sm">View Full Profile</button>
      </div>
    </motion.div>
  );
}
