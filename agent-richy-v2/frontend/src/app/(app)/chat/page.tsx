'use client';

import React, { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { ChatPanel } from '@/components/chat';
import { RichyAvatar } from '@/components/avatar';
import { AGENTS, AGENT_KEYS } from '@/lib/constants';
import { useChatStore } from '@/hooks/useChat';
import type { AgentKey } from '@/lib/types';

function ChatPageInner() {
  const searchParams = useSearchParams();
  const { activeAgent, setActiveAgent, sendMessage } = useChatStore();

  // If ?agent=xxx in URL, switch to that agent on mount
  React.useEffect(() => {
    const paramAgent = searchParams.get('agent') as AgentKey | null;
    if (paramAgent && AGENTS[paramAgent]) {
      setActiveAgent(paramAgent);
    }
  }, [searchParams, setActiveAgent]);

  const currentAgent = AGENTS[activeAgent];

  const SUGGESTED_TOPICS: Record<AgentKey, string[]> = {
    coach_richy: ['Help me build a financial plan', 'What should I focus on first?', 'Review my budget', 'How do I start investing?'],
    budget_bot: ['Analyze my spending', 'Create a 50/30/20 budget', 'How can I cut expenses?', 'Track my subscriptions'],
    invest_intel: ['How should I invest $500/month?', 'Explain index funds', 'Best investment for beginners', 'Build a portfolio'],
    debt_destroyer: ['Help me pay off credit cards', 'Snowball vs avalanche method', 'Should I consolidate debt?', 'Create a payoff plan'],
    savings_sage: ['Build an emergency fund', 'How much should I save?', 'High-yield savings accounts', 'Automate my savings'],
    kid_coach: ['How can kids earn money?', 'Teach me about saving', 'What is compound interest?', 'Needs vs wants'],
  };

  return (
    <div className="flex h-full">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col h-full">
        <ChatPanel />
      </div>

      {/* Sidebar (desktop only) */}
      <div className="hidden lg:flex flex-col w-56 border-l border-navy-700 bg-navy-900 pt-4 px-3 overflow-y-auto">
        {/* Avatar */}
        <div className="flex flex-col items-center mb-4">
          <RichyAvatar size="lg" />
          <p className="text-[10px] text-gray-500 mt-2 text-center leading-relaxed">
            I react to your typing in real time!
          </p>
        </div>

        {/* Agent Switcher */}
        <div className="mb-4">
          <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Active Agent
          </p>
          <div className="space-y-1">
            {AGENT_KEYS.map((key) => {
              const agent = AGENTS[key];
              const isActive = key === activeAgent;
              return (
                <button
                  key={key}
                  onClick={() => setActiveAgent(key)}
                  className={`w-full flex items-center gap-2 px-2.5 py-2 rounded-lg text-left text-xs transition-colors
                    ${isActive
                      ? 'bg-navy-700 border border-gold-500/40'
                      : 'hover:bg-navy-800 border border-transparent'
                    }`}
                >
                  <span className="text-sm">{agent.icon}</span>
                  <div className="flex-1 min-w-0">
                    <p className={`font-medium truncate ${isActive ? 'text-white' : 'text-gray-400'}`}>
                      {agent.name}
                    </p>
                  </div>
                  {isActive && (
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500 flex-shrink-0" />
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Current agent info */}
        <div className="rounded-lg bg-navy-800 border border-navy-700 p-3 mb-4">
          <div className="flex items-center gap-2 mb-1">
            <span>{currentAgent.icon}</span>
            <span className="text-xs font-semibold text-white">{currentAgent.name}</span>
          </div>
          <p className="text-[10px] text-gray-400">{currentAgent.tagline}</p>
        </div>

        {/* Suggested topics */}
        <div className="space-y-1.5">
          <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">
            Try asking
          </p>
          {(SUGGESTED_TOPICS[activeAgent] ?? []).map((topic) => (
            <button
              key={topic}
              onClick={() => sendMessage(topic)}
              className="w-full text-left text-[11px] px-2.5 py-2 rounded-lg
                         bg-navy-800 border border-navy-700 text-gray-300
                         hover:border-gold-500/40 hover:text-white transition-colors"
            >
              {topic}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="flex h-full items-center justify-center text-gray-400">Loading chat...</div>}>
      <ChatPageInner />
    </Suspense>
  );
}
