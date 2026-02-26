'use client';

import React from 'react';
import { Sidebar, MobileNav } from '@/components/layout';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-bg">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        {children}
      </main>
      <MobileNav />
    </div>
  );
}
