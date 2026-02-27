'use client';

import React, { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '@/hooks/useChat';
import { DEMO_MESSAGES } from '@/lib/mockData';
import { Bug } from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

/* ── Quick action shortcuts ────────────────────────────────────────────── */
const QUICK_ACTIONS = [
  'Find coupons',
  'Analyze my spending',
  'Budget help',
  'Market outlook',
  'Price check',
  'Plan a goal',
  'Bill forecast',
  'Tax tips',
  'Negotiate a bill',
  'Top rated stocks',
  'Grocery planner',
  'How am I doing?',
  'My financial future',
  'What if...',
  'My rank',
  'Find an advisor',
  'My money map',
  'My invisible raise',
  'Should I buy now?',
  'Economic impact',
];

export default function ChatPanel() {
  const { messages, isLoading, streamingContent, sendMessage } = useChatStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [showDebug, setShowDebug] = useState(false);

  const isDev = process.env.NODE_ENV === 'development';

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  /** Inject a mock assistant message directly into the chat store. */
  const injectMock = (content: string) => {
    useChatStore.setState((state) => ({
      messages: [
        ...state.messages,
        {
          id: `mock_${Date.now()}`,
          role: 'assistant' as const,
          content,
          agent: 'coach_richy',
          timestamp: Date.now(),
        },
      ],
    }));
  };

  /** Export chat history as markdown file */
  const exportChat = () => {
    if (messages.length === 0) return;
    const lines = messages.map((m) => {
      const time = new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const role = m.role === 'user' ? '**You**' : `**${m.agent?.replace('_', ' ') || 'Richy'}**`;
      return `### ${role} (${time})\n\n${m.content}\n`;
    });
    const md = `# Agent Richy — Chat Export\n\n${lines.join('\n---\n\n')}`;
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `richy-chat-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-line bg-bg/80 backdrop-blur-md">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent to-accent-dark
                          flex items-center justify-center text-black text-[10px] font-extrabold">
            R
          </div>
          <div>
            <span className="text-sm font-semibold text-txt">Agent Richy</span>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              <span className="text-[10px] text-txt-muted">Online</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-txt-muted">
            {messages.length} message{messages.length !== 1 ? 's' : ''}
          </span>
          {messages.length > 0 && (
            <button
              onClick={exportChat}
              className="p-1.5 rounded-lg text-txt-muted hover:text-txt hover:bg-white/5 transition"
              title="Export chat"
              aria-label="Export chat as markdown"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
            </button>
          )}
          {isDev && (
            <button
              onClick={() => setShowDebug((v) => !v)}
              className={`p-1.5 rounded-lg transition ${
                showDebug ? 'bg-accent/20 text-accent' : 'text-txt-muted hover:text-txt hover:bg-white/5'
              }`}
              title="Toggle demo panel"
            >
              <Bug className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Debug / demo panel — dev mode only */}
      {isDev && showDebug && (
        <div className="flex items-center gap-2 px-4 py-2 border-b border-line bg-s2 overflow-x-auto scrollbar-none">
          <span className="text-[10px] font-mono uppercase tracking-label text-txt-muted shrink-0">
            Demo:
          </span>
          {Object.entries(DEMO_MESSAGES).map(([key, { label }]) => (
            <button
              key={key}
              onClick={() => injectMock(DEMO_MESSAGES[key].content)}
              className="whitespace-nowrap text-xs px-2.5 py-1 rounded-full bg-card border border-line
                         text-txt-off hover:border-accent hover:text-accent transition"
            >
              {label}
            </button>
          ))}
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1 scrollbar-thin bg-s1">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center opacity-70">
            <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-accent to-accent-dark flex items-center justify-center mb-4">
              <span className="text-2xl font-extrabold text-black">R</span>
            </div>
            <p className="text-sm text-txt-off max-w-xs">
              Hey there! I&apos;m Richy, your financial coach. Ask me anything about
              budgeting, investing, saving, debt &mdash; you name it!
            </p>
            <p className="text-xs text-txt-muted mt-2">Ask Richy about your finances...</p>
          </div>
        )}

        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <ChatMessage
              key={msg.id ?? i}
              message={msg}
              isLatest={i === messages.length - 1}
            />
          ))}
        </AnimatePresence>

        {/* Streaming indicator */}
        {isLoading && streamingContent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start mb-3"
          >
            <div className="flex-shrink-0 mr-2 mt-1">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent to-accent-dark
                              flex items-center justify-center text-black text-[10px] font-extrabold">
                R
              </div>
            </div>
            <div className="max-w-[75%] rounded-2xl rounded-bl-md px-4 py-3 text-sm
                            bg-card border border-line
                            text-txt leading-relaxed">
              <span className="whitespace-pre-wrap">{streamingContent}</span>
              <span className="inline-block ml-1 w-2 h-4 bg-accent animate-pulse rounded-sm" />
            </div>
          </motion.div>
        )}

        {/* Typing dots */}
        {isLoading && !streamingContent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start mb-3"
          >
            <div className="flex-shrink-0 mr-2 mt-1">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent to-accent-dark
                              flex items-center justify-center text-black text-[10px] font-extrabold">
                R
              </div>
            </div>
            <div className="rounded-2xl rounded-bl-md px-4 py-3 bg-card border border-line">
              <div className="flex gap-1.5">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 rounded-full bg-accent"
                    animate={{ y: [0, -6, 0] }}
                    transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.15 }}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area + Quick Actions */}
      <div className="border-t border-line bg-bg">
        <div className="px-4 pt-3 pb-2">
          <ChatInput />
        </div>
        {/* Quick action pills */}
        <div className="px-4 pb-3 flex flex-nowrap lg:flex-wrap gap-2 overflow-x-auto scrollbar-none">
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action}
              onClick={() => sendMessage(action)}
              className="flex-shrink-0 bg-s2 border border-line rounded-full px-3 py-1.5
                         text-sm text-txt-off hover:text-accent hover:border-line-hover
                         transition whitespace-nowrap"
            >
              {action}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
