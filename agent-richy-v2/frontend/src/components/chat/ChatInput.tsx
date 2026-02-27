'use client';

import React, { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useKeystrokeWatcher } from '@/components/avatar';
import { useChatStore } from '@/hooks/useChat';

interface ChatInputProps {
  className?: string;
}

export default function ChatInput({ className = '' }: ChatInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { sendMessage, isLoading } = useChatStore();
  const { onInputChange, onMessageSent } = useKeystrokeWatcher();

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    }
  }, [text]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setText(val);
    onInputChange(val); // feed keystroke watcher
  };

  const handleSubmit = () => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;
    sendMessage(trimmed);
    onMessageSent();
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={`flex items-end gap-2 ${className}`} role="form" aria-label="Chat input">
      <textarea
        ref={textareaRef}
        value={text}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder="Ask Richy about your finances..."
        aria-label="Message input"
        rows={1}
        disabled={isLoading}
        className="flex-1 resize-none rounded-xl border border-line
                   bg-s2 px-4 py-3 text-sm text-txt
                   placeholder-txt-muted
                   focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent
                   transition-shadow disabled:opacity-60"
      />
      {isLoading ? (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => {
            // Abort streaming — clear loading state
            useChatStore.setState({ isLoading: false, streamingContent: '' });
          }}
          className="flex-shrink-0 w-10 h-10 rounded-xl bg-red-600 hover:bg-red-500
                     text-white flex items-center justify-center
                     transition-all"
          aria-label="Stop generating"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <rect x="4" y="4" width="16" height="16" rx="2" />
          </svg>
        </motion.button>
      ) : (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSubmit}
          disabled={!text.trim()}
          className="flex-shrink-0 w-10 h-10 rounded-xl bg-accent hover:brightness-110
                     text-black flex items-center justify-center shadow-[0_0_20px_rgba(0,232,123,.18)]
                     disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          aria-label="Send message"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 2L11 13" />
            <path d="M22 2L15 22L11 13L2 9L22 2Z" />
          </svg>
        </motion.button>
      )}
    </div>
  );
}
