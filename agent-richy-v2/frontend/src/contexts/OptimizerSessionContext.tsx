"use client";

import React, { createContext, useContext, useCallback, useState } from "react";
import type { RecurringExpense } from "@/types/spending";

/* ── Types ─────────────────────────────────────────────────────────── */

export type OptimizerPhase =
  | "collecting"
  | "analyzing"
  | "presenting"
  | "acting";

export interface OptimizerSession {
  active: boolean;
  expenses: RecurringExpense[];
  phase: OptimizerPhase;
}

interface OptimizerContextValue {
  session: OptimizerSession;
  activate: () => void;
  deactivate: () => void;
  setPhase: (phase: OptimizerPhase) => void;
  addExpense: (expense: RecurringExpense) => void;
  setExpenses: (expenses: RecurringExpense[]) => void;
  clearExpenses: () => void;
  /** Summary string to inject into subsequent AI messages for context. */
  getExpenseSummary: () => string;
}

/* ── Default values ────────────────────────────────────────────────── */

const DEFAULT_SESSION: OptimizerSession = {
  active: false,
  expenses: [],
  phase: "collecting",
};

const OptimizerContext = createContext<OptimizerContextValue>({
  session: DEFAULT_SESSION,
  activate: () => {},
  deactivate: () => {},
  setPhase: () => {},
  addExpense: () => {},
  setExpenses: () => {},
  clearExpenses: () => {},
  getExpenseSummary: () => "",
});

/* ── Provider ──────────────────────────────────────────────────────── */

export function OptimizerSessionProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [session, setSession] = useState<OptimizerSession>(DEFAULT_SESSION);

  const activate = useCallback(
    () =>
      setSession((s) => ({
        ...s,
        active: true,
        phase: s.expenses.length > 0 ? s.phase : "collecting",
      })),
    [],
  );

  const deactivate = useCallback(
    () => setSession((s) => ({ ...s, active: false })),
    [],
  );

  const setPhase = useCallback(
    (phase: OptimizerPhase) => setSession((s) => ({ ...s, phase })),
    [],
  );

  const addExpense = useCallback(
    (expense: RecurringExpense) =>
      setSession((s) => ({ ...s, expenses: [...s.expenses, expense] })),
    [],
  );

  const setExpenses = useCallback(
    (expenses: RecurringExpense[]) => setSession((s) => ({ ...s, expenses })),
    [],
  );

  const clearExpenses = useCallback(
    () => setSession((s) => ({ ...s, expenses: [], phase: "collecting" })),
    [],
  );

  const getExpenseSummary = useCallback(() => {
    if (session.expenses.length === 0) return "";
    const lines = session.expenses.map(
      (e) => `- ${e.name} (${e.category}): $${e.amount}/${e.frequency}`,
    );
    return `User's known recurring expenses:\n${lines.join("\n")}`;
  }, [session.expenses]);

  return (
    <OptimizerContext.Provider
      value={{
        session,
        activate,
        deactivate,
        setPhase,
        addExpense,
        setExpenses,
        clearExpenses,
        getExpenseSummary,
      }}
    >
      {children}
    </OptimizerContext.Provider>
  );
}

/* ── Hook ───────────────────────────────────────────────────────────── */

export function useOptimizerSession() {
  return useContext(OptimizerContext);
}
