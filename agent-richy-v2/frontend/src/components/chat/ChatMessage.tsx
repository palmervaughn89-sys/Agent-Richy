'use client';

import React from 'react';
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
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed
          ${
            isUser
              ? 'bg-accent text-black rounded-br-md font-medium'
              : 'bg-card text-txt border border-line rounded-bl-md'
          }`}
      >
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
