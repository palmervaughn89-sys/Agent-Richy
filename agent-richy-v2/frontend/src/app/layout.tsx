import type { Metadata } from 'next';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'Agent Richy — Your AI Financial Coach | Free Personalized Money Advice',
  description:
    'Agent Richy is your all-in-one AI financial coach. He helps you budget, find deals, negotiate bills, invest, eliminate debt, and build real wealth — completely free.',
  icons: { icon: '/favicon.svg' },
  openGraph: {
    title: 'Agent Richy — Your AI Financial Coach',
    description:
      'One AI coach that analyzes your spending, finds deals, cuts your bills, optimizes your taxes, and builds your wealth. For free.',
    url: 'https://agent-richy-pwgx.vercel.app',
    siteName: 'Agent Richy',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Agent Richy — Your AI Financial Coach',
    description:
      'Your all-in-one AI financial coach. Budgets, coupons, bill negotiation, investing, and more. Free forever.',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full dark scroll-smooth overflow-x-hidden">
      <body className="h-full bg-bg text-txt font-sans antialiased">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:z-[100] focus:top-4 focus:left-4 focus:px-4 focus:py-2 focus:bg-accent focus:text-black focus:rounded-lg focus:font-semibold"
        >
          Skip to main content
        </a>
        <main id="main-content">
          {children}
        </main>
      </body>
    </html>
  );
}
