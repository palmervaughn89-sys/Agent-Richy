/* ── Grocery Planner — optimized shopping plan engine ───────────────── */

// ==========================================
// TYPES
// ==========================================

export type GroceryCategory =
  | "produce" | "meat_seafood" | "dairy_eggs" | "bakery"
  | "frozen" | "pantry_staples" | "snacks" | "beverages"
  | "cleaning" | "personal_care" | "baby" | "pet"
  | "deli" | "prepared" | "other";

export interface GroceryItem {
  name: string;
  quantity: number;
  unit: string;                          // "lb", "oz", "count", "gallon", etc.
  category: GroceryCategory;
  brand?: string;                        // "Tide" vs generic/any
  brandFlexible: boolean;                // Will they accept store brand?
  estimatedPrice?: number;               // What they usually pay
  usualStore?: string;
}

export interface OptimizedGroceryPlan {
  // Input summary
  totalItems: number;
  estimatedTotalAtUsualStore: number;

  // Optimized plan
  optimizedTotal: number;
  totalSavings: number;
  savingsPercentage: number;

  // Store-by-store breakdown
  storeTrips: {
    store: string;
    storeName: string;
    items: {
      item: GroceryItem;
      priceAtThisStore: number;
      priceAtUsualStore: number;
      savings: number;
      onSale: boolean;
      couponAvailable: boolean;
      couponCode?: string;
      couponSavings?: number;
      substituteAvailable: boolean;
      substituteName?: string;
      substitutePrice?: number;
      substituteSavings?: number;
    }[];
    subtotal: number;
    couponsApplied: number;
    couponSavings: number;
  }[];

  // Single-store option (for convenience comparison)
  singleStoreBest: {
    store: string;
    total: number;
    vsOptimized: number;                 // How much more expensive
    convenienceTax: number;              // The premium for one-stop shopping
  };

  // Coupons found
  couponsFound: {
    item: string;
    store: string;
    code: string;
    savings: number;
    expiresAt: string;
  }[];

  // Substitution suggestions
  substitutions: {
    original: string;
    originalPrice: number;
    substitute: string;
    substitutePrice: number;
    savings: number;
    note: string;                        // "Store brand is identical quality" or "Different brand, similar product"
  }[];

  // Smart tips
  tips: string[];                        // "Buy chicken in bulk at Costco and freeze — saves $2.40/lb"
}

// ==========================================
// SYSTEM PROMPT INSTRUCTIONS
// ==========================================

export const GROCERY_PLANNER_INSTRUCTIONS = `
When a user shares a grocery list:

1. PARSE the list — identify each item, quantity, and any brand preferences
2. CATEGORIZE each item (produce, meat, dairy, pantry, etc.)
3. For each item, SEARCH for prices at the user's local stores
4. CHECK for active coupons on each item
5. IDENTIFY store brand substitutions that are significantly cheaper
6. BUILD the optimal plan:
   - If savings from multiple stores > $15: recommend multi-store plan
   - If savings < $15: recommend single cheapest store (convenience wins)
   - Always show the comparison either way
7. FORMAT as an OptimizedGroceryPlan JSON block
8. Add TIPS specific to their list

Smart rules:
- Don't send someone to 5 stores to save $8 — factor in gas and time
- Bulk suggestions only if the user has storage (ask about household size)
- Seasonal produce is always cheaper — suggest swaps
- Store loyalty cards are free money — remind them to use them
- Coupons stack: manufacturer + store coupon on the same item
`;
