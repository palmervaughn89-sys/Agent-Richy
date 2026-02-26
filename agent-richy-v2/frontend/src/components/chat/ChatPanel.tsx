'use client';

import React, { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '@/hooks/useChat';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

export default function ChatPanel() {
  const { messages, isLoading, streamingContent, activeAgent } = useChatStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  return (
    <div className="flex flex-col h-full">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-line bg-bg/80 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          <span className="text-sm font-medium text-txt">
            {activeAgent ? activeAgent.replace('_', ' ') : 'Coach Richy'}
          </span>
        </div>
        <span className="text-xs text-txt-muted">
          {messages.length} message{messages.length !== 1 ? 's' : ''}
        </span>
      </div>

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

      {/* Input area */}
      <div className="px-4 py-3 border-t border-line bg-bg">
        <ChatInput />
      </div>
    </div>
  );
}
