export type ExpenseCategory = "subscriptions" | "utilities" | "insurance" | "telecom" | "food_delivery" | "transportation" | "memberships" | "software" | "finance" | "other";

export interface RecurringExpense {
  id: string;
  name: string;
  category: ExpenseCategory;
  amount: number;
  frequency: "weekly" | "monthly" | "quarterly" | "annual";
  provider?: string;
  startDate?: string;
  lastUsed?: string;
  notes?: string;
}

export interface ExpenseProfile {
  userId: string;
  expenses: RecurringExpense[];
  income?: number;
  metadata: {
    createdAt: string;
    updatedAt: string;
    dataSource: "manual" | "plaid" | "hybrid";
  };
}

export interface SavingsAction {
  id: string;
  type: "cancel" | "downgrade" | "negotiate" | "switch_annual" | "bundle" | "spend_to_save" | "free_alternative" | "timing" | "loyalty";
  title: string;
  description: string;
  targetExpense?: string;
  estimatedMonthlySavings: number;
  estimatedAnnualSavings: number;
  effortLevel: 1 | 2 | 3 | 4 | 5;
  timeToRealize: "immediate" | "next_cycle" | "1_month" | "3_months";
  script?: string;
  alternativeService?: string;
  upfrontCost?: number;
  roiMonths?: number;
}

export interface SavingsReport {
  userId: string;
  generatedAt: string;
  totalMonthlyExpenses: number;
  totalPotentialMonthlySavings: number;
  totalPotentialAnnualSavings: number;
  actions: SavingsAction[];
  subscriptionRedundancies: { services: string[]; combinedCost: number; suggestion: string }[];
  benchmarkComparisons: { expense: string; userPays: number; marketAverage: number; potential: number }[];
}

export interface DataProvider {
  getRecurringExpenses(userId: string): Promise<RecurringExpense[]>;
  detectSubscriptions(userId: string): Promise<RecurringExpense[]>;
  getSpendingTrends(userId: string, period: "1m" | "3m" | "6m" | "1y"): Promise<any[]>;
  flagUnusualCharges(userId: string): Promise<any[]>;
}
