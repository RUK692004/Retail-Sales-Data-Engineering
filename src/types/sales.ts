export interface Sale {
  saleId: string;
  saleDate: string;
  customerId: string;
  customerName: string;
  skuId: string;
  productName: string;
  category: string;
  storeId: string;
  storeName: string;
  quantity: number;
  unitPrice: number;
  totalAmount: number;
  paymentMethod: string;
}

export interface SalesMetrics {
  totalSalesCount: number;
  totalRevenue: number;
  averageOrderValue: number;
  totalQuantitySold: number;
}

export interface SalesQueryParams {
  page?: number;
  pageSize?: number;
  search?: string;
  startDate?: string;
  endDate?: string;
  storeId?: string;
  category?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
