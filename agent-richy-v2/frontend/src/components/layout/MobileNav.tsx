'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  MessageSquare,
  GraduationCap,
  PieChart,
  Target,
  User,
} from 'lucide-react';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/chat', label: 'Chat', icon: MessageSquare },
  { href: '/kids', label: 'Kids', icon: GraduationCap },
  { href: '/lifestyle-portfolio', label: 'Portfolio', icon: PieChart },
  { href: '/plan', label: 'Plan', icon: Target },
  { href: '/profile', label: 'Profile', icon: User },
];

export default function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40
                    bg-bg/95 backdrop-blur-xl border-t border-line
                    safe-area-bottom">
      <div className="flex items-center justify-around px-2 py-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || pathname?.startsWith(item.href + '/');
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href} className="flex-1">
              <div className="flex flex-col items-center justify-center gap-0.5 min-h-[44px] py-1.5">
                <Icon className={`w-5 h-5 ${active ? 'text-accent' : 'text-txt-muted'}`} />
                <span
                  className={`text-[10px] font-medium ${
                    active ? 'text-accent' : 'text-txt-muted'
                  }`}
                >
                  {item.label}
                </span>
                {active && (
                  <motion.div
                    layoutId="mobile-indicator"
                    className="w-4 h-0.5 rounded-full bg-accent"
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
