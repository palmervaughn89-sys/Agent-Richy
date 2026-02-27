'use client';

import { useEffect } from 'react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Optionally log to an error reporting service
  }, [error]);

  return (
    <div className="min-h-screen bg-bg text-txt flex flex-col items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-4" role="img" aria-label="Warning">⚠️</div>
        <h1 className="text-3xl font-bold mb-4">Something went wrong</h1>
        <p className="text-muted mb-8">
          An unexpected error occurred. Don&apos;t worry — your data is safe.
        </p>
        <button
          onClick={reset}
          className="px-6 py-3 rounded-xl bg-accent text-black font-semibold hover:bg-accent/90 transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}
