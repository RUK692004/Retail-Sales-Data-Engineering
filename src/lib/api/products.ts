import { apiClient } from './client';
import { ApiResponse, Product, ProductQueryParams } from '@/types';

export const productsApi = {
  getProducts: async (params?: ProductQueryParams): Promise<ApiResponse<Product[]>> => {
    const response = await apiClient.get<ApiResponse<Product[]>>('/products', { params });
    return response.data;
  },

  getProductBySku: async (skuId: string): Promise<Product> => {
    const response = await apiClient.get<ApiResponse<Product>>(`/products/${skuId}`);
    return response.data.data;
  },
};
