'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { RichyAvatar } from '@/components/avatar';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/chat', label: 'Chat', icon: '💬' },
  { href: '/kids', label: 'Kids Zone', icon: '🎓' },
  { href: '/plan', label: 'My Plan', icon: '🎯' },
  { href: '/profile', label: 'Profile', icon: '👤' },
  { href: '/calculators', label: 'Calculators', icon: '🧮' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col w-64 bg-white dark:bg-navy-900
                      border-r border-gray-100 dark:border-navy-700 h-screen sticky top-0">
      {/* Brand */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-100 dark:border-navy-700">
        <RichyAvatar size="sm" />
        <div>
          <h1 className="text-lg font-bold text-navy-800 dark:text-white tracking-tight">
            Agent Richy
          </h1>
          <p className="text-[10px] text-gray-400 uppercase tracking-widest">
            Financial Coach
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || pathname?.startsWith(item.href + '/');
          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                whileHover={{ x: 2 }}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                            transition-colors cursor-pointer
                  ${
                    active
                      ? 'bg-gold-50 dark:bg-gold-900/20 text-gold-700 dark:text-gold-400'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-navy-800'
                  }`}
              >
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>
                {active && (
                  <motion.div
                    layoutId="sidebar-indicator"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-gold-500"
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-100 dark:border-navy-700">
        <Link href="/upgrade">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r
                          from-gold-400 to-gold-500 text-white text-xs font-semibold
                          hover:from-gold-500 hover:to-gold-600 transition-all cursor-pointer
                          shadow-md">
            <span>⭐</span>
            <span>Upgrade to Pro</span>
          </div>
        </Link>
      </div>
    </aside>
  );
}
