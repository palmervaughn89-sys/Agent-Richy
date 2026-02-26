import type { Metadata } from 'next';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'Agent Richy — Your AI Financial Coach',
  description: 'Interactive financial coaching powered by AI. Budgeting, investing, debt management, and more.',
  icons: { icon: '/favicon.ico' },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full dark">
      <body className="h-full bg-navy-900 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
