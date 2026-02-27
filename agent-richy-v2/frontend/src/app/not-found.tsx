'use client';

import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-bg text-txt flex flex-col items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="text-9xl font-extrabold text-accent/20 select-none mb-4">404</div>
        <h1 className="text-3xl font-bold mb-4">Page Not Found</h1>
        <p className="text-muted mb-8">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
          Let&apos;s get you back on track!
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/"
            className="px-6 py-3 rounded-xl bg-accent text-black font-semibold hover:bg-accent/90 transition-colors"
          >
            Go Home
          </Link>
          <Link
            href="/chat"
            className="px-6 py-3 rounded-xl border border-border text-txt font-semibold hover:bg-card transition-colors"
          >
            Chat with Richy
          </Link>
        </div>
      </div>
    </div>
  );
}
