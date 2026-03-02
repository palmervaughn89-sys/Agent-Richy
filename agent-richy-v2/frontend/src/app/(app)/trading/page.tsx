'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { TopNav } from '@/components/layout';
import {
  TrendingUp,
  TrendingDown,
  Search,
  RefreshCw,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Activity,
} from 'lucide-react';
import {
  getWeeklyPicks,
  scoreStock,
  getPerformance,
} from '@/lib/api';

/* ── Types ───────────────────────────────────────────────────────────── */
interface StockPick {
  ticker: string;
  company?: string;
  score: number;
  signal: string;
  sector?: string;
  last_price?: number;
  target_price?: number;
  confidence?: number;
  reasoning?: string;
  decision?: string;
}

interface StockScoreResult {
  ticker: string;
  composite_score: number;
  momentum_score?: number;
  value_score?: number;
  quality_score?: number;
  signal: string;
  details?: Record<string, unknown>;
}



/* ── Helpers ─────────────────────────────────────────────────────────── */
function decisionBadge(decision: string) {
  const d = (decision || '').toUpperCase();
  if (d === 'LONG' || d === 'BUY') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-accent/15 text-accent">
        <ArrowUpRight className="w-3 h-3" /> LONG
      </span>
    );
  }
  if (d === 'SHORT' || d === 'SELL') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-red-500/15 text-red-400">
        <ArrowDownRight className="w-3 h-3" /> SHORT
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-400">
      <Minus className="w-3 h-3" /> HOLD
    </span>
  );
}

function scoreColor(score: number) {
  if (score >= 70) return 'text-accent';
  if (score >= 50) return 'text-amber-400';
  return 'text-red-400';
}

function scoreBg(score: number) {
  if (score >= 70) return 'bg-accent/10';
  if (score >= 50) return 'bg-amber-500/10';
  return 'bg-red-500/10';
}

function fmt(n: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(n);
}

function regimeColor(regime: string) {
  switch ((regime || '').toUpperCase()) {
    case 'BULLISH': return 'text-accent bg-accent/10 border-accent/30';
    case 'BEARISH': return 'text-red-400 bg-red-500/10 border-red-500/30';
    default:        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
  }
}

function regimeIcon(regime: string) {
  switch ((regime || '').toUpperCase()) {
    case 'BULLISH': return <TrendingUp className="w-5 h-5" />;
    case 'BEARISH': return <TrendingDown className="w-5 h-5" />;
    default:        return <Activity className="w-5 h-5" />;
  }
}

/* ── Picks Table Component ───────────────────────────────────────────── */
function PicksTable({
  title,
  icon,
  iconColor,
  picks,
  loading,
  emptyMsg,
}: {
  title: string;
  icon: React.ReactNode;
  iconColor: string;
  picks: StockPick[];
  loading: boolean;
  emptyMsg: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.1 }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      className="rounded-card bg-card border border-line p-5"
    >
      <div className="flex items-center gap-2 mb-4">
        <div className={iconColor}>{icon}</div>
        <h3 className="text-sm font-semibold text-txt">{title}</h3>
        <span className="ml-auto text-[11px] text-txt-off font-mono">{picks.length} picks</span>
      </div>

      {loading ? (
        <div className="text-center py-8 text-txt-muted text-sm">Loading…</div>
      ) : picks.length === 0 ? (
        <div className="text-center py-8">
          <AlertTriangle className="w-6 h-6 text-amber-400 mx-auto mb-2" />
          <p className="text-xs text-txt-muted">{emptyMsg}</p>
        </div>
      ) : (
        <div className="overflow-x-auto -mx-5 px-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-line text-left text-[11px] text-txt-muted uppercase tracking-wider">
                <th className="pb-2.5 pr-4 font-medium">Ticker</th>
                <th className="pb-2.5 pr-4 font-medium">Score</th>
                <th className="pb-2.5 pr-4 font-medium">Decision</th>
                <th className="pb-2.5 pr-4 font-medium hidden sm:table-cell">Price</th>
                <th className="pb-2.5 font-medium hidden md:table-cell">Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {picks.map((pick, i) => (
                <motion.tr
                  key={pick.ticker}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="border-b border-line/40 hover:bg-ghost/40 transition-colors"
                >
                  <td className="py-3.5 pr-4">
                    <div>
                      <span className="font-bold text-txt tracking-tight">{pick.ticker}</span>
                      {pick.company && (
                        <span className="block text-[11px] text-txt-off mt-0.5">{pick.company}</span>
                      )}
                    </div>
                  </td>
                  <td className="py-3.5 pr-4">
                    <span className={`inline-flex items-center justify-center w-12 h-7 rounded-md text-xs font-bold ${scoreBg(pick.score)} ${scoreColor(pick.score)}`}>
                      {pick.score.toFixed(1)}
                    </span>
                  </td>
                  <td className="py-3.5 pr-4">
                    {decisionBadge(pick.decision || pick.signal)}
                  </td>
                  <td className="py-3.5 pr-4 text-txt-muted font-mono text-xs hidden sm:table-cell">
                    {pick.last_price ? fmt(pick.last_price) : '—'}
                  </td>
                  <td className="py-3.5 text-txt-off text-xs max-w-xs truncate hidden md:table-cell">
                    {pick.reasoning || '—'}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
}

/* ── Page ─────────────────────────────────────────────────────────────── */
export default function TradingPage() {
  // Weekly picks split into LONG / SHORT
  const [longPicks, setLongPicks] = useState<StockPick[]>([]);
  const [shortPicks, setShortPicks] = useState<StockPick[]>([]);
  const [loadingPicks, setLoadingPicks] = useState(true);

  // Market regime
  const [marketRegime, setMarketRegime] = useState('NEUTRAL');

  // Scorer
  const [scoreTicker, setScoreTicker] = useState('');
  const [scoreResult, setScoreResult] = useState<StockScoreResult | null>(null);
  const [loadingScore, setLoadingScore] = useState(false);
  const [scoreError, setScoreError] = useState('');

  /* ── Fetch picks ───────────────────────────────────────────────────── */
  const fetchPicks = useCallback(async () => {
    setLoadingPicks(true);
    try {
      const data: StockPick[] = await getWeeklyPicks(10);
      const longs: StockPick[] = [];
      const shorts: StockPick[] = [];
      for (const p of data) {
        const d = (p.decision || p.signal || '').toUpperCase();
        if (d === 'SHORT' || d === 'SELL') {
          shorts.push(p);
        } else {
          longs.push(p);
        }
      }
      setLongPicks(longs.slice(0, 5));
      setShortPicks(shorts.slice(0, 5));
    } catch {
      setLongPicks([]);
      setShortPicks([]);
    } finally {
      setLoadingPicks(false);
    }
  }, []);

  /* ── Fetch market regime ────────────────────────────────────────────── */
  const fetchRegime = useCallback(async () => {
    try {
      const data = await getPerformance();
      setMarketRegime(data.market_regime ?? 'NEUTRAL');
    } catch {
      // keep default
    }
  }, []);

  useEffect(() => {
    fetchPicks();
    fetchRegime();
  }, [fetchPicks, fetchRegime]);

  /* ── Score a ticker ────────────────────────────────────────────────── */
  async function handleScore() {
    if (!scoreTicker.trim()) return;
    setLoadingScore(true);
    setScoreError('');
    setScoreResult(null);
    try {
      const data = await scoreStock(scoreTicker.trim());
      setScoreResult(data);
    } catch (err) {
      setScoreError(err instanceof Error ? err.message : 'Ticker not found');
    } finally {
      setLoadingScore(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <TopNav title="Trading" />

      <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6 space-y-6">
        {/* ── Header ─────────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2">
          <div>
            <p className="section-label">RICHY ENGINE</p>
            <h2 className="text-2xl font-extrabold text-txt tracking-tight">
              Stock Trading Intelligence
            </h2>
          </div>
          <button
            onClick={() => { fetchPicks(); fetchRegime(); }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                       text-txt-muted hover:text-txt hover:bg-ghost border border-line
                       hover:border-line-hover transition-all self-start sm:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingPicks ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* ── Market Regime + Stock Scorer ───────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Market Regime */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="rounded-card bg-card border border-line p-5 flex flex-col items-center justify-center text-center"
          >
            <span className="text-[11px] text-txt-muted uppercase tracking-wider font-medium mb-3">
              Market Regime
            </span>
            <div className={`flex items-center gap-2 px-5 py-3 rounded-xl border font-extrabold text-lg tracking-tight ${regimeColor(marketRegime)}`}>
              {regimeIcon(marketRegime)}
              {marketRegime.toUpperCase()}
            </div>
            <p className="text-[11px] text-txt-off mt-3">
              {marketRegime === 'BULLISH'
                ? 'Favoring long positions this week'
                : marketRegime === 'BEARISH'
                ? 'Favoring short/defensive positions'
                : 'Mixed signals — balanced approach'}
            </p>
          </motion.div>

          {/* Stock Scorer */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2 rounded-card bg-card border border-line p-5"
          >
            <div className="flex items-center gap-2 mb-4">
              <Search className="w-5 h-5 text-accent" />
              <h3 className="text-sm font-semibold text-txt">Stock Scorer</h3>
              <span className="text-[11px] text-txt-off ml-1">— score any ticker instantly</span>
            </div>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={scoreTicker}
                onChange={(e) => setScoreTicker(e.target.value.toUpperCase())}
                onKeyDown={(e) => e.key === 'Enter' && handleScore()}
                placeholder="Enter ticker (e.g. AAPL, TSLA, NVDA)"
                className="flex-1 px-3.5 py-2.5 rounded-lg bg-s1 border border-line text-txt text-sm
                           placeholder:text-txt-off focus:outline-none focus:border-accent
                           transition-colors font-mono"
              />
              <button
                onClick={handleScore}
                disabled={loadingScore || !scoreTicker.trim()}
                className="px-5 py-2.5 rounded-lg bg-accent text-black text-sm font-extrabold
                           hover:brightness-110 transition-all disabled:opacity-40
                           disabled:cursor-not-allowed shadow-[0_0_20px_rgba(0,232,123,.15)]"
              >
                {loadingScore ? 'Scoring…' : 'Score'}
              </button>
            </div>

            {scoreError && (
              <div className="flex items-center gap-2 text-red-400 text-sm mb-3">
                <AlertTriangle className="w-4 h-4" />
                {scoreError}
              </div>
            )}

            {scoreResult && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="rounded-lg bg-s1 border border-line p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-extrabold text-txt tracking-tight">
                      {scoreResult.ticker}
                    </span>
                    {decisionBadge(scoreResult.signal)}
                  </div>
                  <div className={`text-2xl font-extrabold ${scoreColor(scoreResult.composite_score)}`}>
                    {scoreResult.composite_score.toFixed(1)}
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  {scoreResult.momentum_score != null && (
                    <div className="rounded-lg bg-bg/50 p-3 text-center">
                      <span className="text-[11px] text-txt-muted block mb-1">Momentum</span>
                      <p className={`font-bold ${scoreColor(scoreResult.momentum_score)}`}>
                        {scoreResult.momentum_score.toFixed(1)}
                      </p>
                    </div>
                  )}
                  {scoreResult.value_score != null && (
                    <div className="rounded-lg bg-bg/50 p-3 text-center">
                      <span className="text-[11px] text-txt-muted block mb-1">Value</span>
                      <p className={`font-bold ${scoreColor(scoreResult.value_score)}`}>
                        {scoreResult.value_score.toFixed(1)}
                      </p>
                    </div>
                  )}
                  {scoreResult.quality_score != null && (
                    <div className="rounded-lg bg-bg/50 p-3 text-center">
                      <span className="text-[11px] text-txt-muted block mb-1">Quality</span>
                      <p className={`font-bold ${scoreColor(scoreResult.quality_score)}`}>
                        {scoreResult.quality_score.toFixed(1)}
                      </p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {!scoreResult && !scoreError && (
              <p className="text-xs text-txt-off text-center py-2">
                Type a stock ticker above and press <kbd className="px-1.5 py-0.5 rounded bg-s1 border border-line text-[11px] font-mono">Enter</kbd> or click Score
              </p>
            )}
          </motion.div>
        </div>

        {/* ── Top 5 LONG Picks ────────────────────────────────────── */}
        <PicksTable
          title="Top 5 LONG Picks"
          icon={<TrendingUp className="w-5 h-5" />}
          iconColor="text-accent"
          picks={longPicks}
          loading={loadingPicks}
          emptyMsg="No long picks this week. Connect the Richy Engine database."
        />

        {/* ── Top 5 SHORT Picks ───────────────────────────────────── */}
        <PicksTable
          title="Top 5 SHORT Picks"
          icon={<TrendingDown className="w-5 h-5" />}
          iconColor="text-red-400"
          picks={shortPicks}
          loading={loadingPicks}
          emptyMsg="No short picks this week."
        />

        {/* ── Disclaimer ───────────────────────────────────────────── */}
        <div className="text-center text-[11px] text-txt-off/60 px-8 pb-4">
          <em>
            Trading involves risk. This is an AI-powered scoring tool, not financial advice. Always do your own research.
          </em>
        </div>
      </div>
    </div>
  );
}
