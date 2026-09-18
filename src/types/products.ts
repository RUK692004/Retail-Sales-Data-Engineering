export type ProductStatus = 'ACTIVE' | 'DISCONTINUED' | 'DRAFT';

export interface Product {
  skuId: string;
  productName: string;
  category: string;
  brand: string;
  price: number;
  costPrice: number;
  unit: string;
  status: ProductStatus;
  createdAt: string;
  description?: string;
}

export interface ProductQueryParams {
  page?: number;
  pageSize?: number;
  search?: string;
  category?: string;
  brand?: string;
  status?: ProductStatus | 'ALL';
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
