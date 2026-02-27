/* ── In-memory rate limiter for API routes ───────────────────────────── */

interface RateLimitEntry {
  count: number;
  resetTime: number;
}

/** Map of "bucket:ip" → entry */
const store = new Map<string, RateLimitEntry>();

/** Periodically prune expired entries (every 5 min) */
let lastPrune = Date.now();
function prune() {
  const now = Date.now();
  if (now - lastPrune < 300_000) return;
  lastPrune = now;
  store.forEach((entry, key) => {
    if (now > entry.resetTime) store.delete(key);
  });
}

export interface RateLimitResult {
  ok: boolean;
  remaining: number;
  retryAfterMs: number;
}

/**
 * Check rate limit for a given bucket + identifier.
 * @param bucket  – e.g. "chat", "calculator", "keystroke"
 * @param id      – e.g. client IP
 * @param limit   – max requests per window
 * @param windowMs – window size in milliseconds
 */
export function rateLimit(
  bucket: string,
  id: string,
  limit: number,
  windowMs: number,
): RateLimitResult {
  prune();
  const key = `${bucket}:${id}`;
  const now = Date.now();
  const entry = store.get(key);

  if (!entry || now > entry.resetTime) {
    store.set(key, { count: 1, resetTime: now + windowMs });
    return { ok: true, remaining: limit - 1, retryAfterMs: 0 };
  }

  if (entry.count < limit) {
    entry.count++;
    return { ok: true, remaining: limit - entry.count, retryAfterMs: 0 };
  }

  return { ok: false, remaining: 0, retryAfterMs: entry.resetTime - now };
}
