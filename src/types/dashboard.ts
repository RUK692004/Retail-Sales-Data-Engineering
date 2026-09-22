export interface SalesTrendPoint {
  date: string;
  revenue: number;
  orders: number;
}

export interface SalesByStore {
  storeId: string;
  storeName: string;
  revenue: number;
  orders: number;
}

export interface TopProduct {
  skuId: string;
  productName: string;
  category: string;
  unitsSold: number;
  totalRevenue: number;
}

export interface SalesByCategory {
  category: string;
  revenue: number;
  percentage: number;
}

export interface PipelineStatus {
  status: 'HEALTHY' | 'WARNING' | 'DEGRADED' | 'FAILED';
  lastRunAt: string | null;
  recordsProcessedToday: number;
  errorRatePercentage: number;
}

export interface RecentSaleSnippet {
  saleId: string;
  date: string;
  customerName: string;
  productName: string;
  storeName: string;
  totalAmount: number;
}

export interface LowStockAlert {
  skuId: string;
  productName: string;
  storeName: string;
  stockOnHand: number;
  reorderPoint: number;
}

export interface DashboardSummary {
  totalRevenue: number;
  revenueGrowthPercentage: number;
  totalOrders: number;
  ordersGrowthPercentage: number;
  totalCustomers: number;
  totalSkus: number;
  totalInventoryUnits: number;
  lowStockItemsCount: number;
  salesTrend: SalesTrendPoint[];
  salesByStore: SalesByStore[];
  topProducts: TopProduct[];
  salesByCategory: SalesByCategory[];
  recentSales: RecentSaleSnippet[];
  lowStockAlerts: LowStockAlert[];
  pipelineStatus: PipelineStatus;
}
