'use client';

import React, { Suspense, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { ChatPanel } from '@/components/chat';
import { AGENTS, AGENT_KEYS } from '@/lib/constants';
import { useChatStore } from '@/hooks/useChat';
import { PanelLeftClose, PanelLeft } from 'lucide-react';
import type { AgentKey } from '@/lib/types';

/* ── Agent intro messages ────────────────────────────────────────────── */
const AGENT_INTROS: Record<AgentKey, string> = {
  coach_richy:
    "Hey! I'm Coach Richy — your all-in-one financial advisor. Tell me about your situation and I'll route you to the right specialist or handle it myself.",
  budget_bot:
    "Hey! I'm your Budget Coach. Tell me about your monthly income and expenses, and I'll help you build a plan that actually works.",
  invest_intel:
    "Ready to grow your money? I'm Invest Intel — share your risk tolerance and goals, and I'll craft a strategy for you.",
  debt_destroyer:
    "Let's crush that debt! I'm the Debt Destroyer. Tell me what you owe and I'll map out the fastest path to freedom.",
  savings_sage:
    "I'm the Savings Sage. Whether it's an emergency fund or a big goal, let's figure out how much to save and where to keep it.",
  kid_coach:
    "Hi there! I'm the Kid Coach. I make money topics fun and easy to understand. Ask me anything!",
};

const SUGGESTED_TOPICS: Record<AgentKey, string[]> = {
  coach_richy: ['Help me build a financial plan', 'What should I focus on first?', 'Review my budget', 'How do I start investing?'],
  budget_bot: ['Analyze my spending', 'Create a 50/30/20 budget', 'How can I cut expenses?', 'Track my subscriptions'],
  invest_intel: ['How should I invest $500/month?', 'Explain index funds', 'Best investment for beginners', 'Build a portfolio'],
  debt_destroyer: ['Help me pay off credit cards', 'Snowball vs avalanche method', 'Should I consolidate debt?', 'Create a payoff plan'],
  savings_sage: ['Build an emergency fund', 'How much should I save?', 'High-yield savings accounts', 'Automate my savings'],
  kid_coach: ['How can kids earn money?', 'Teach me about saving', 'What is compound interest?', 'Needs vs wants'],
};

function ChatPageInner() {
  const searchParams = useSearchParams();
  const { activeAgent, setActiveAgent, sendMessage } = useChatStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  React.useEffect(() => {
    const paramAgent = searchParams.get('agent') as AgentKey | null;
    if (paramAgent && AGENTS[paramAgent]) {
      setActiveAgent(paramAgent);
    }
  }, [searchParams, setActiveAgent]);

  const currentAgent = AGENTS[activeAgent];

  return (
    <div className="flex h-full relative">
      {/* ── Left sidebar: agent selector ─────────────────────────────── */}
      {/* Desktop */}
      <div className="hidden lg:flex flex-col w-60 border-r border-line bg-s1 pt-4 px-3 overflow-y-auto flex-shrink-0">
        <AgentList
          activeAgent={activeAgent}
          setActiveAgent={(key) => {
            setActiveAgent(key);
            sendMessage(AGENT_INTROS[key]);
          }}
          sendMessage={sendMessage}
          topics={SUGGESTED_TOPICS}
          currentAgent={currentAgent}
        />
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
        <AgentList
          activeAgent={activeAgent}
          setActiveAgent={(key) => {
            setActiveAgent(key);
            setSidebarOpen(false);
          }}
          sendMessage={sendMessage}
          topics={SUGGESTED_TOPICS}
          currentAgent={currentAgent}
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

/* ── Agent list sidebar component ─────────────────────────────────────── */
function AgentList({
  activeAgent,
  setActiveAgent,
  sendMessage,
  topics,
  currentAgent,
}: {
  activeAgent: AgentKey;
  setActiveAgent: (key: AgentKey) => void;
  sendMessage: (msg: string) => void;
  topics: Record<AgentKey, string[]>;
  currentAgent: (typeof AGENTS)[AgentKey];
}) {
  return (
    <>
      <p className="font-mono text-[10px] font-semibold text-accent uppercase tracking-label mb-2 px-1">
        Specialist Agents
      </p>
      <div className="space-y-1 mb-5">
        {AGENT_KEYS.map((key) => {
          const agent = AGENTS[key];
          const isActive = key === activeAgent;
          return (
            <button
              key={key}
              onClick={() => setActiveAgent(key)}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left text-xs transition-all
                ${isActive
                  ? 'bg-ghost border border-line-hover text-txt'
                  : 'hover:bg-ghost border border-transparent text-txt-off hover:text-txt'
                }`}
            >
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center text-sm flex-shrink-0"
                style={{ backgroundColor: `${agent.color}18`, border: `1px solid ${agent.color}40` }}
              >
                {agent.icon}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{agent.name}</p>
                <p className="text-[10px] text-txt-muted truncate">{agent.specialty}</p>
              </div>
              {isActive && (
                <span className="w-2 h-2 rounded-full bg-accent flex-shrink-0" />
              )}
            </button>
          );
        })}
      </div>

      {/* Active agent info */}
      <div className="rounded-[14px] bg-card border border-line p-3 mb-4">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm">{currentAgent.icon}</span>
          <span className="text-xs font-semibold text-txt">{currentAgent.name}</span>
        </div>
        <p className="text-[10px] text-txt-muted italic">&ldquo;{currentAgent.tagline}&rdquo;</p>
      </div>

      {/* Suggested topics */}
      <p className="font-mono text-[10px] font-semibold text-accent uppercase tracking-label mb-2 px-1">
        Try asking
      </p>
      <div className="space-y-1.5">
        {(topics[activeAgent] ?? []).map((topic) => (
          <button
            key={topic}
            onClick={() => sendMessage(topic)}
            className="w-full text-left text-[11px] px-3 py-2 rounded-lg
                       bg-card border border-line text-txt-off
                       hover:border-line-hover hover:text-txt transition-colors"
          >
            {topic}
          </button>
        ))}
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
