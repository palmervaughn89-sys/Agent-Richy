'use client';

import React, { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '@/hooks/useChat';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

export default function ChatPanel() {
  const { messages, isLoading, streamingContent, activeAgent } = useChatStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages / streaming content
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  return (
    <div className="flex flex-col h-full">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-navy-700">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-sm font-medium text-navy-700 dark:text-gray-200">
            {activeAgent ? activeAgent.replace('_', ' ') : 'Coach Richy'}
          </span>
        </div>
        <span className="text-xs text-gray-400">
          {messages.length} message{messages.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1 scrollbar-thin">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center opacity-60">
            <span className="text-4xl mb-3">💰</span>
            <p className="text-sm text-gray-500 dark:text-gray-400 max-w-xs">
              Hey there! I&apos;m Richy, your financial coach. Ask me anything about
              budgeting, investing, saving, debt &mdash; you name it!
            </p>
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
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gold-400 to-gold-600
                              flex items-center justify-center text-white text-xs font-bold shadow">
                R
              </div>
            </div>
            <div className="max-w-[75%] rounded-2xl rounded-bl-md px-4 py-3 text-sm
                            bg-white dark:bg-navy-800 border border-gray-100 dark:border-navy-700
                            shadow-sm text-navy-800 dark:text-gray-100 leading-relaxed">
              <span className="whitespace-pre-wrap">{streamingContent}</span>
              <span className="inline-block ml-1 w-2 h-4 bg-gold-400 animate-pulse rounded-sm" />
            </div>
          </motion.div>
        )}

        {/* Typing dots when loading but no stream yet */}
        {isLoading && !streamingContent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start mb-3"
          >
            <div className="flex-shrink-0 mr-2 mt-1">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gold-400 to-gold-600
                              flex items-center justify-center text-white text-xs font-bold shadow">
                R
              </div>
            </div>
            <div className="rounded-2xl rounded-bl-md px-4 py-3 bg-white dark:bg-navy-800
                            border border-gray-100 dark:border-navy-700 shadow-sm">
              <div className="flex gap-1.5">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 rounded-full bg-gold-400"
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

      {/* Input area */}
      <div className="px-4 py-3 border-t border-gray-100 dark:border-navy-700 bg-gray-50 dark:bg-navy-900">
        <ChatInput />
      </div>
    </div>
  );
}
