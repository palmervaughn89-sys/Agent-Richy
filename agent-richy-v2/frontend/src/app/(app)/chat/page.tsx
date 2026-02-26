'use client';

import React, { Suspense, useState } from 'react';
import { ChatPanel } from '@/components/chat';
import { useChatStore } from '@/hooks/useChat';
import { PanelLeft } from 'lucide-react';

/* ── Topics sidebar data ─────────────────────────────────────────────── */
const TOPICS = [
  { icon: '📊', label: 'Budgeting',              starter: 'Help me build a budget' },
  { icon: '💰', label: 'Saving',                  starter: 'How can I save more money?' },
  { icon: '🏷️', label: 'Coupons & Deals',         starter: 'Find me some deals' },
  { icon: '🧾', label: 'Tax Strategy',            starter: 'Help me with tax planning' },
  { icon: '📈', label: 'Investing',               starter: 'How should I start investing?' },
  { icon: '🔄', label: 'Bills & Subscriptions',   starter: 'Audit my subscriptions and bills' },
  { icon: '⭐', label: 'Kids Zone',               starter: 'Teach my kid about money' },
];

function ChatPageInner() {
  const { sendMessage } = useChatStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-full relative">
      {/* ── Left sidebar: Topics ──────────────────────────────────────── */}
      {/* Desktop */}
      <div className="hidden lg:flex flex-col w-56 border-r border-line bg-s1 pt-4 px-3 overflow-y-auto flex-shrink-0">
        <TopicsSidebar sendMessage={sendMessage} />
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <div
        className={`lg:hidden fixed inset-y-0 left-0 z-50 w-64 bg-s1 border-r border-line pt-4 px-3 overflow-y-auto transform transition-transform duration-200 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <TopicsSidebar
          sendMessage={(msg) => {
            sendMessage(msg);
            setSidebarOpen(false);
          }}
        />
      </div>

      {/* ── Main chat area ───────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        {/* Mobile toggle */}
        <button
          className="lg:hidden absolute top-3 left-3 z-30 p-2.5 rounded-lg bg-card border border-line text-txt-muted hover:text-txt min-w-[44px] min-h-[44px] flex items-center justify-center"
          onClick={() => setSidebarOpen(true)}
        >
          <PanelLeft className="w-5 h-5" />
        </button>
        <ChatPanel />
      </div>
    </div>
  );
}

/* ── Topics sidebar component ─────────────────────────────────────────── */
function TopicsSidebar({ sendMessage }: { sendMessage: (msg: string) => void }) {
  return (
    <>
      {/* Richy identity card */}
      <div className="rounded-[14px] bg-card border border-line p-3 mb-5">
        <div className="flex items-center gap-2.5 mb-1.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-accent-dark
                          flex items-center justify-center text-black text-xs font-extrabold flex-shrink-0">
            R
          </div>
          <div>
            <p className="text-xs font-semibold text-txt">Agent Richy</p>
            <p className="text-[10px] text-txt-muted">Your AI financial coach</p>
          </div>
        </div>
        <p className="text-[10px] text-txt-muted italic mt-1">
          &ldquo;Your smart friend who happens to be a financial planner.&rdquo;
        </p>
      </div>

      {/* Topic buttons */}
      <p className="font-mono text-[10px] font-semibold text-accent uppercase tracking-label mb-2 px-1">
        Topics
      </p>
      <div className="space-y-1">
        {TOPICS.map((topic) => (
          <button
            key={topic.label}
            onClick={() => sendMessage(topic.starter)}
            className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left text-xs
                       hover:bg-ghost border border-transparent text-txt-off hover:text-txt
                       hover:border-line-hover transition-all"
          >
            <span className="text-sm flex-shrink-0">{topic.icon}</span>
            <span className="font-medium">{topic.label}</span>
          </button>
        ))}
      </div>

      {/* New chat */}
      <div className="mt-6 px-1">
        <button
          onClick={() => useChatStore.getState().clearMessages()}
          className="w-full text-[11px] px-3 py-2 rounded-lg
                     bg-ghost border border-line text-txt-muted
                     hover:border-line-hover hover:text-txt transition-colors text-center"
        >
          + New conversation
        </button>
      </div>
    </>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="flex h-full items-center justify-center text-txt-muted">Loading chat...</div>}>
      <ChatPageInner />
    </Suspense>
  );
}
