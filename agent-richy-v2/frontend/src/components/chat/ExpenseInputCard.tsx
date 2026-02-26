"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Trash2 } from "lucide-react";
import type { RecurringExpense, ExpenseCategory } from "@/types/spending";

interface ExpenseInputCardProps {
  onAddExpense: (expense: RecurringExpense) => void;
  onAnalyze: (expenses: RecurringExpense[]) => void;
  existingExpenses?: RecurringExpense[];
}

const CATEGORY_TABS: { label: string; value: ExpenseCategory }[] = [
  { label: "Subscriptions", value: "subscriptions" },
  { label: "Utilities", value: "utilities" },
  { label: "Insurance", value: "insurance" },
  { label: "Telecom", value: "telecom" },
  { label: "Food & Delivery", value: "food_delivery" },
  { label: "Transport", value: "transportation" },
  { label: "Memberships", value: "memberships" },
  { label: "Software", value: "software" },
];

const FREQUENCY_OPTIONS: { label: string; value: RecurringExpense["frequency"] }[] = [
  { label: "Monthly", value: "monthly" },
  { label: "Annual", value: "annual" },
  { label: "Weekly", value: "weekly" },
  { label: "Quarterly", value: "quarterly" },
];

function toMonthly(amount: number, frequency: RecurringExpense["frequency"]): number {
  switch (frequency) {
    case "weekly":
      return amount * 52 / 12;
    case "monthly":
      return amount;
    case "quarterly":
      return amount / 3;
    case "annual":
      return amount / 12;
  }
}

export default function ExpenseInputCard({
  onAddExpense,
  onAnalyze,
  existingExpenses = [],
}: ExpenseInputCardProps) {
  const [expenses, setExpenses] = useState<RecurringExpense[]>(existingExpenses);
  const [activeCategory, setActiveCategory] = useState<ExpenseCategory>("subscriptions");
  const [name, setName] = useState("");
  const [amount, setAmount] = useState("");
  const [frequency, setFrequency] = useState<RecurringExpense["frequency"]>("monthly");

  const monthlyTotal = expenses.reduce(
    (sum, e) => sum + toMonthly(e.amount, e.frequency),
    0,
  );

  const canAnalyze = expenses.length >= 3;

  const handleAdd = () => {
    const parsed = parseFloat(amount);
    if (!name.trim() || isNaN(parsed) || parsed <= 0) return;

    const expense: RecurringExpense = {
      id: crypto.randomUUID(),
      name: name.trim(),
      category: activeCategory,
      amount: parsed,
      frequency,
    };

    setExpenses((prev) => [...prev, expense]);
    onAddExpense(expense);
    setName("");
    setAmount("");
  };

  const handleRemove = (id: string) => {
    setExpenses((prev) => prev.filter((e) => e.id !== id));
  };

  const handleAnalyze = () => {
    if (canAnalyze) onAnalyze(expenses);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border border-line rounded-card p-5"
    >
      {/* Header */}
      <h3 className="text-lg font-semibold text-txt mb-4">Add Your Expenses</h3>

      {/* Category tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-4 scrollbar-none">
        {CATEGORY_TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setActiveCategory(tab.value)}
            className={`whitespace-nowrap px-3 py-1.5 rounded-full text-sm transition ${
              activeCategory === tab.value
                ? "bg-accent text-black font-medium"
                : "bg-s2 text-txt-muted border border-line hover:border-line-hover"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Form */}
      <div className="space-y-3 mb-4">
        <input
          type="text"
          placeholder="Service name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full bg-s2 border border-line rounded-lg px-3 py-2 text-txt placeholder-txt-muted text-sm focus:outline-none focus:ring-1 focus:ring-accent focus:border-accent transition"
        />

        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-txt-muted text-sm">$</span>
          <input
            type="number"
            placeholder="0.00"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full bg-s2 border border-line rounded-lg pl-7 pr-3 py-2 text-txt placeholder-txt-muted text-sm focus:outline-none focus:ring-1 focus:ring-accent focus:border-accent transition"
          />
        </div>

        <select
          value={frequency}
          onChange={(e) => setFrequency(e.target.value as RecurringExpense["frequency"])}
          className="w-full bg-s2 border border-line rounded-lg px-3 py-2 text-txt text-sm focus:outline-none focus:ring-1 focus:ring-accent focus:border-accent transition appearance-none"
        >
          {FREQUENCY_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        <button
          onClick={handleAdd}
          className="w-full bg-accent text-black font-semibold rounded-lg py-2.5 text-sm hover:bg-accent-dim transition flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" /> Add Expense
        </button>
      </div>

      {/* Running expense list */}
      {expenses.length > 0 && (
        <div className="space-y-2">
          <AnimatePresence initial={false}>
            {expenses.map((expense) => (
              <motion.div
                key={expense.id}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="flex justify-between items-center bg-s1 rounded-lg px-3 py-2"
              >
                <div className="flex items-center gap-2">
                  <span className="text-txt-off text-sm">{expense.name}</span>
                  <span className="font-mono text-[10px] text-accent bg-ghost px-1.5 py-0.5 rounded">
                    {expense.category.replace("_", " ").toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-txt font-medium text-sm">
                    ${expense.amount.toFixed(2)}
                    <span className="text-txt-muted text-xs">/{expense.frequency.slice(0, 2)}</span>
                  </span>
                  <button
                    onClick={() => handleRemove(expense.id)}
                    className="text-txt-muted hover:text-red-400 transition p-1"
                    aria-label={`Remove ${expense.name}`}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Running total */}
          <div className="border-t border-line pt-2 flex justify-between items-center">
            <span className="text-txt-muted text-sm">Monthly Total</span>
            <span className="text-accent font-semibold">
              ${monthlyTotal.toFixed(2)}
            </span>
          </div>
        </div>
      )}

      {/* Analyze button */}
      <div className="relative mt-4">
        <button
          onClick={handleAnalyze}
          disabled={!canAnalyze}
          className={`w-full bg-accent text-black font-semibold rounded-lg py-2.5 text-sm transition ${
            canAnalyze
              ? "hover:bg-accent-dim"
              : "opacity-50 cursor-not-allowed"
          }`}
          title={canAnalyze ? undefined : "Add at least 3 expenses"}
        >
          Analyze My Spending →
        </button>
        {!canAnalyze && expenses.length > 0 && (
          <p className="text-txt-muted text-xs text-center mt-1">
            Add at least {3 - expenses.length} more expense{3 - expenses.length !== 1 ? "s" : ""}
          </p>
        )}
      </div>
    </motion.div>
  );
}
