'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/chat', label: 'Chat', icon: '💬' },
  { href: '/kids', label: 'Kids', icon: '🎓' },
  { href: '/plan', label: 'Plan', icon: '🎯' },
  { href: '/profile', label: 'Profile', icon: '👤' },
];

export default function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40
                    bg-white dark:bg-navy-900 border-t border-gray-200 dark:border-navy-700
                    safe-area-bottom">
      <div className="flex items-center justify-around px-2 py-1.5">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || pathname?.startsWith(item.href + '/');
          return (
            <Link key={item.href} href={item.href} className="flex-1">
              <div className="flex flex-col items-center gap-0.5 py-1">
                <span className="text-lg">{item.icon}</span>
                <span
                  className={`text-[10px] font-medium ${
                    active
                      ? 'text-gold-600 dark:text-gold-400'
                      : 'text-gray-500 dark:text-gray-400'
                  }`}
                >
                  {item.label}
                </span>
                {active && (
                  <motion.div
                    layoutId="mobile-indicator"
                    className="w-4 h-0.5 rounded-full bg-gold-500"
                  />
                )}
              </div>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
