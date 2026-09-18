export interface Customer {
  customerId: string;
  fullName: string;
  email: string;
  city: string;
  state: string;
  country: string;
  totalPurchases: number;
  totalOrders: number;
  loyaltyTier: 'BRONZE' | 'SILVER' | 'GOLD' | 'PLATINUM';
  firstPurchasedAt: string;
  lastPurchasedAt: string;
}

export interface CustomerQueryParams {
  page?: number;
  pageSize?: number;
  search?: string;
  loyaltyTier?: string;
  city?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
