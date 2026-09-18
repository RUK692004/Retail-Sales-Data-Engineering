export type PromotionStatus = 'ACTIVE' | 'UPCOMING' | 'EXPIRED';

export interface Promotion {
  promotionId: string;
  promotionName: string;
  targetType: 'SKU' | 'CATEGORY';
  targetValue: string;
  discountPercentage: number;
  startDate: string;
  endDate: string;
  status: PromotionStatus;
  redemptionCount: number;
  revenueGenerated: number;
}

export interface PromotionQueryParams {
  page?: number;
  pageSize?: number;
  search?: string;
  status?: PromotionStatus | 'ALL';
  targetType?: 'SKU' | 'CATEGORY' | 'ALL';
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
