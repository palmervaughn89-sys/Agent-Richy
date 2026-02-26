'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  MessageSquare,
  GraduationCap,
  Target,
  User,
  Calculator,
  PieChart,
  Sparkles,
} from 'lucide-react';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/chat', label: 'Chat', icon: MessageSquare },
  { href: '/kids', label: 'Kids Zone', icon: GraduationCap },
  { href: '/lifestyle-portfolio', label: 'Lifestyle Portfolio', icon: PieChart },
  { href: '/plan', label: 'My Plan', icon: Target },
  { href: '/profile', label: 'Profile', icon: User },
  { href: '/calculators', label: 'Calculators', icon: Calculator },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col w-64 bg-s1
                      border-r border-line h-screen sticky top-0">
      {/* Brand */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-line">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-accent-dark
                        flex items-center justify-center text-black text-sm font-extrabold">R</div>
        <div>
          <h1 className="text-base font-bold text-txt tracking-tight">
            Agent Richy
          </h1>
          <p className="text-[10px] text-txt-muted font-mono uppercase tracking-label">
            Financial Coach
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || pathname?.startsWith(item.href + '/');
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                whileHover={{ x: 2 }}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                            transition-colors cursor-pointer
                  ${
                    active
                      ? 'bg-ghost text-accent border border-line-hover'
                      : 'text-txt-off hover:bg-card hover:text-txt border border-transparent'
                  }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
                {active && (
                  <motion.div
                    layoutId="sidebar-indicator"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-accent"
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-line">
        <Link href="/upgrade">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg
                          bg-accent text-black text-xs font-extrabold
                          hover:brightness-110 transition-all cursor-pointer
                          shadow-[0_0_30px_rgba(0,232,123,.18)]">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Upgrade to Pro</span>
          </div>
        </Link>
      </div>
    </aside>
  );
}
