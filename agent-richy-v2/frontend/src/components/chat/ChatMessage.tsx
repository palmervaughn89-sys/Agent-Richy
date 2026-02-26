'use client';

import React from 'react';
import { motion } from 'framer-motion';
import type { ChatMessage as ChatMessageType } from '@/lib/types';
import { AGENTS } from '@/lib/constants';
import type { AgentKey } from '@/lib/types';
import ResponseRenderer from './ResponseRenderer';

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
      {/* Agent badge */}
      {!isUser && (
        <div className="flex-shrink-0 mr-2 mt-1">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold shadow"
            style={{ background: agentInfo ? `linear-gradient(135deg, ${agentInfo.color}, ${agentInfo.color}dd)` : 'linear-gradient(135deg, #f59e0b, #d97706)' }}
          >
            {agentInfo?.icon || 'R'}
          </div>
        </div>
      )}

      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed
          ${
            isUser
              ? 'bg-gold-500 text-white rounded-br-md'
              : 'bg-white dark:bg-navy-800 text-navy-800 dark:text-gray-100 border border-gray-100 dark:border-navy-700 rounded-bl-md shadow-sm'
          }`}
      >
        {/* Agent label */}
        {!isUser && message.agent && (
          <span
            className="block text-[10px] font-semibold uppercase tracking-wider mb-1"
            style={{ color: agentInfo?.color || '#f59e0b' }}
          >
            {agentInfo?.name || message.agent.replace('_', ' ')}
          </span>
        )}

        {/* Message body */}
        <div className="whitespace-pre-wrap">{message.content}</div>

        {/* Structured data (charts, evidence, examples) */}
        {!isUser && message.structured && (
          <ResponseRenderer data={message.structured} />
        )}

        {/* Timestamp */}
        <span
          className={`block text-[10px] mt-1 ${
            isUser ? 'text-white/60' : 'text-gray-400 dark:text-gray-500'
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
