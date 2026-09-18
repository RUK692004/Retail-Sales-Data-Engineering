export type InventoryStatus = 'IN_STOCK' | 'LOW_STOCK' | 'OUT_OF_STOCK';

export interface InventoryItem {
  id: string;
  storeId: string;
  storeName: string;
  skuId: string;
  productName: string;
  category: string;
  stockOnHand: number;
  reorderPoint: number;
  status: InventoryStatus;
  lastRestocked: string;
}

export interface InventoryMetrics {
  totalInventoryUnits: number;
  lowStockCount: number;
  outOfStockCount: number;
  storesWithIssuesCount: number;
}

export interface InventoryQueryParams {
  page?: number;
  pageSize?: number;
  search?: string;
  storeId?: string;
  status?: InventoryStatus | 'ALL';
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
