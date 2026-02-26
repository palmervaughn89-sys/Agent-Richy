import type { Metadata } from 'next';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'Agent Richy — Your AI Financial Coach | Free Personalized Money Advice',
  description:
    'Agent Richy is your AI financial coach. 6 specialist agents help you budget, invest, eliminate debt, optimize taxes, and build real wealth — completely free.',
  icons: { icon: '/favicon.svg' },
  openGraph: {
    title: 'Agent Richy — Your AI Financial Coach',
    description:
      '6 specialist AI agents analyze your spending, cut your costs, optimize your taxes, and build your wealth. For free.',
    url: 'https://agent-richy-pwgx.vercel.app',
    siteName: 'Agent Richy',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Agent Richy — Your AI Financial Coach',
    description:
      '6 specialist AI agents that help you build real wealth. Free forever.',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full dark scroll-smooth overflow-x-hidden">
      <body className="h-full bg-bg text-txt font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
