'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import type { ChatMessage as ChatMessageType } from '@/lib/types';
import { AGENTS } from '@/lib/constants';
import type { AgentKey } from '@/lib/types';
import ResponseRenderer from './ResponseRenderer';
import StructuredBlockRenderer from './StructuredBlockRenderer';

interface Props {
  message: ChatMessageType;
  isLatest?: boolean;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
    }
  };
  return (
    <button
      onClick={handleCopy}
      className="opacity-0 group-hover:opacity-100 transition-opacity absolute top-2 right-2
                 p-1.5 rounded-md bg-s2/80 border border-line hover:bg-s2 text-txt-muted hover:text-txt"
      aria-label="Copy message"
      title={copied ? 'Copied!' : 'Copy to clipboard'}
    >
      {copied ? (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      ) : (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
        </svg>
      )}
    </button>
  );
}

export default function ChatMessage({ message, isLatest = false }: Props) {
  const isUser = message.role === 'user';
  const agentInfo = message.agent ? AGENTS[message.agent as AgentKey] : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}
    >
      {/* Agent avatar */}
      {!isUser && (
        <div className="flex-shrink-0 mr-2 mt-1">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent to-accent-dark
                          flex items-center justify-center text-black text-[10px] font-extrabold">
            {agentInfo?.icon || 'R'}
          </div>
        </div>
      )}

      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed relative group
          ${
            isUser
              ? 'bg-accent text-black rounded-br-md font-medium'
              : 'bg-card text-txt border border-line rounded-bl-md'
          }`}
      >
        {/* Copy button (assistant messages only) */}
        {!isUser && <CopyButton text={message.content} />}
        {/* Agent label */}
        {!isUser && message.agent && (
          <span
            className="block text-[10px] font-mono font-semibold uppercase tracking-label mb-1 text-accent"
          >
            {agentInfo?.name || message.agent.replace('_', ' ')}
          </span>
        )}

        {/* Message body */}
        {isUser ? (
          <div className="whitespace-pre-wrap">{message.content}</div>
        ) : (
          <StructuredBlockRenderer content={message.content} />
        )}

        {/* Structured data */}
        {!isUser && message.structured && (
          <ResponseRenderer data={message.structured} />
        )}

        {/* Timestamp */}
        <span
          className={`block text-[10px] mt-1 ${
            isUser ? 'text-black/50' : 'text-txt-muted'
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>
    </motion.div>
  );
}
