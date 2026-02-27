export type ProductCategory = 
  | "groceries" | "electronics" | "clothing" | "home_garden"
  | "health_beauty" | "baby_kids" | "pets" | "automotive"
  | "office" | "sports_outdoors" | "toys_games" | "other";

export type Store = 
  | "amazon" | "walmart" | "target" | "costco" | "kroger"
  | "walgreens" | "cvs" | "home_depot" | "lowes" | "bestbuy"
  | "sams_club" | "aldi" | "publix" | "whole_foods" | "trader_joes"
  | "dollar_general" | "dollar_tree" | "ebay" | "other";

export interface PricePoint {
  store: string;
  storeName: string;
  price: number;
  unitPrice?: number;          // Price per unit (per oz, per count, etc.)
  unit?: string;               // "oz", "count", "lb", etc.
  url?: string;                // Direct product link
  inStock: boolean;
  lastVerified: string;        // ISO date
  isOnSale: boolean;
  saleEnds?: string;
  membershipRequired?: boolean; // Costco, Sam's Club
  shippingCost?: number;       // 0 = free shipping
  primeRequired?: boolean;     // Amazon Prime pricing
}

export interface PriceComparison {
  id: string;
  productName: string;
  category: ProductCategory;
  userPaidPrice: number;
  userPaidStore: string;
  bestPrice: PricePoint;
  allPrices: PricePoint[];     // Sorted cheapest first
  savingsAmount: number;       // userPaidPrice - bestPrice.price
  savingsPercent: number;      // Percentage saved
  recommendation: string;     // "Switch to Costco for this item" or "You're already getting the best price"
}

export interface ShoppingProfile {
  userId: string;
  regularPurchases: {
    productName: string;
    category: ProductCategory;
    usualStore: string;
    usualPrice: number;
    frequency: "weekly" | "biweekly" | "monthly" | "quarterly";
    lastPurchased?: string;
  }[];
  preferredStores: string[];
  hasMemberships: {
    costco?: boolean;
    samsClub?: boolean;
    amazonPrime?: boolean;
    walmartPlus?: boolean;
  };
  location?: {
    zipCode: string;
    nearbyStores: string[];
  };
}

export interface PriceAlert {
  id: string;
  productName: string;
  targetPrice: number;
  currentBestPrice: number;
  triggered: boolean;
  store?: string;
}

export interface StoreCategoryRanking {
  category: ProductCategory;
  categoryName: string;
  rankings: {
    rank: number;
    store: string;
    storeName: string;
    avgPriceIndex: number;     // 100 = average. Below 100 = cheaper than average
    bestFor: string;           // "Bulk items", "Organic options", "Store brand quality"
    watchOut: string;          // "Requires membership", "Limited selection", "Higher markup on name brands"
  }[];
  lastUpdated: string;
  source: string;              // "Consumer Reports price comparison data", etc.
}

export interface SubscriptionValue {
  id: string;
  serviceName: string;
  monthlyCost: number;
  hoursUsedPerMonth: number;
  costPerHour: number;
  category: string;
  valueRating: "excellent" | "good" | "fair" | "poor" | "unused";
  recommendation: string;
  alternativeOptions?: {
    name: string;
    cost: number;
    note: string;
  }[];
}
