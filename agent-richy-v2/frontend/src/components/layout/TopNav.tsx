'use client';

import React from 'react';

interface Props {
  title?: string;
  children?: React.ReactNode;
}

export default function TopNav({ title, children }: Props) {
  return (
    <header className="flex items-center justify-between px-4 md:px-6 py-3
                        border-b border-gray-100 dark:border-navy-700
                        bg-white/80 dark:bg-navy-900/80 backdrop-blur-sm
                        sticky top-0 z-30">
      <div className="flex items-center gap-3">
        {title && (
          <h2 className="text-base font-semibold text-navy-800 dark:text-white">
            {title}
          </h2>
        )}
      </div>
      <div className="flex items-center gap-2">
        {children}
      </div>
    </header>
  );
}
