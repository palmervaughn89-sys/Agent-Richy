export type CouponCategory = "food" | "retail" | "services" | "travel" | "entertainment" | "tech" | "health" | "other";

export interface Coupon {
  id: string;
  store: string;
  storeLogo?: string;
  code: string;
  description: string;
  discountType: "percentage" | "fixed" | "bogo" | "free_shipping";
  discountValue: number;
  minimumPurchase?: number;
  expiresAt?: string;
  restrictions?: string;
  sourceUrl: string;
  affiliateUrl?: string;
  confidence: "verified" | "likely_valid" | "unverified";
  category: CouponCategory;
}

export interface CouponSearchOptions {
  category?: CouponCategory;
  location?: { lat: number; lng: number; radius: number };
  minDiscount?: number;
  includeExpired?: boolean;
  includeUnverified?: boolean;
}

export interface CouponProvider {
  searchCoupons(query: string, options?: CouponSearchOptions): Promise<Coupon[]>;
  validateCoupon(code: string, store: string): Promise<{ valid: boolean; confidence: number }>;
  getPopularDeals(category?: CouponCategory, location?: string): Promise<Coupon[]>;
}
