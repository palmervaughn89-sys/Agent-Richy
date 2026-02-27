'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { PriceComparison, PricePoint } from '@/types/pricing';

function fmt(n: number): string {
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return iso;
  }
}

export default function PriceComparisonCard({
  comparison,
}: {
  comparison: PriceComparison;
}) {
  const [expanded, setExpanded] = useState(false);

  const isBestAlready = comparison.savingsAmount <= 0;
  const { bestPrice, allPrices } = comparison;
  const cheapest = allPrices[0]?.price ?? bestPrice.price;
  const mostExpensive = allPrices[allPrices.length - 1]?.price ?? comparison.userPaidPrice;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="bg-card border border-line rounded-card p-5"
    >
      {/* Header */}
      <h3 className="text-lg font-semibold text-txt">{comparison.productName}</h3>

      {/* You paid */}
      <div className="bg-s1 rounded-lg p-3 mt-3 flex items-center justify-between">
        <div>
          <span className="text-muted text-xs font-mono uppercase tracking-wider">
            You paid
          </span>
          <p className="text-off mt-0.5">
            {comparison.userPaidStore} &mdash;{' '}
            <span className="font-semibold">{fmt(comparison.userPaidPrice)}</span>
          </p>
        </div>
        {!isBestAlready && (
          <span className="text-red-400 text-lg font-bold select-none" title="Not the best price">
            ✕
          </span>
        )}
        {isBestAlready && (
          <span className="text-accent text-lg font-bold select-none" title="Best price!">
            ✓
          </span>
        )}
      </div>

      {/* Best price found */}
      <div className="bg-accent/10 border border-accent/20 rounded-lg p-3 mt-2">
        <span className="text-muted text-xs font-mono uppercase tracking-wider">
          Best price found
        </span>
        <p className="text-accent font-bold text-xl mt-0.5">
          {bestPrice.storeName} &mdash; {fmt(bestPrice.price)}
        </p>

        {/* Savings badge */}
        {!isBestAlready && (
          <span className="inline-block bg-accent text-black font-bold px-3 py-1 rounded-full text-sm mt-2">
            Save {fmt(comparison.savingsAmount)} ({comparison.savingsPercent}%)
          </span>
        )}
        {isBestAlready && (
          <span className="inline-block bg-accent/15 text-accent font-semibold px-3 py-1 rounded-full text-sm mt-2">
            You&apos;re already getting the best price!
          </span>
        )}

        {/* Metadata row */}
        <div className="flex flex-wrap items-center gap-3 mt-2">
          {bestPrice.url && (
            <a
              href={bestPrice.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent text-sm hover:underline"
            >
              View deal →
            </a>
          )}
          {bestPrice.membershipRequired && (
            <span className="text-muted text-xs">Requires membership</span>
          )}
          {bestPrice.primeRequired && (
            <span className="text-muted text-xs">Requires Prime</span>
          )}
          {bestPrice.isOnSale && bestPrice.saleEnds && (
            <span className="bg-amber-500/15 text-amber-400 text-xs px-2 py-0.5 rounded-full">
              Sale ends {formatDate(bestPrice.saleEnds)}
            </span>
          )}
          {bestPrice.shippingCost != null && bestPrice.shippingCost === 0 && (
            <span className="text-accent text-xs">Free shipping</span>
          )}
          {bestPrice.shippingCost != null && bestPrice.shippingCost > 0 && (
            <span className="text-muted text-xs">
              +{fmt(bestPrice.shippingCost)} shipping
            </span>
          )}
        </div>
      </div>

      {/* All prices toggle */}
      {allPrices.length > 1 && (
        <div className="mt-3">
          <button
            onClick={() => setExpanded((v) => !v)}
            className="text-accent text-sm cursor-pointer hover:underline focus:outline-none"
          >
            {expanded
              ? 'Hide comparison ↑'
              : `Compare all ${allPrices.length} stores →`}
          </button>

          <AnimatePresence>
            {expanded && (
              <motion.ul
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.25 }}
                className="mt-2 space-y-1 overflow-hidden"
              >
                {allPrices.map((pp: PricePoint, i: number) => {
                  const isCheapest = pp.price === cheapest;
                  const isMostExpensive =
                    pp.price === mostExpensive && allPrices.length > 1;
                  const isUserStore =
                    pp.storeName === comparison.userPaidStore ||
                    pp.store === comparison.userPaidStore;

                  return (
                    <li
                      key={pp.store + i}
                      className="flex items-center justify-between bg-s1 rounded-lg px-3 py-2"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-off">{pp.storeName}</span>
                        {isUserStore && (
                          <span className="text-muted text-[11px] bg-s2 px-1.5 py-0.5 rounded">
                            You paid here
                          </span>
                        )}
                        {pp.membershipRequired && (
                          <span className="text-muted text-[11px]">🔒</span>
                        )}
                        {!pp.inStock && (
                          <span className="text-red-400 text-[11px]">
                            Out of stock
                          </span>
                        )}
                      </div>
                      <span
                        className={`font-semibold ${
                          isCheapest
                            ? 'text-accent'
                            : isMostExpensive
                            ? 'text-red-400'
                            : 'text-txt'
                        }`}
                      >
                        {fmt(pp.price)}
                      </span>
                    </li>
                  );
                })}
              </motion.ul>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Recommendation */}
      <p className="text-off text-sm mt-3">{comparison.recommendation}</p>
    </motion.div>
  );
}
