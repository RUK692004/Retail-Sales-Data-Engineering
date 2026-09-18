import { apiClient } from './client';
import { ApiResponse, Sale, SalesMetrics, SalesQueryParams } from '@/types';

export const salesApi = {
  getSales: async (params?: SalesQueryParams): Promise<ApiResponse<Sale[]>> => {
    const response = await apiClient.get<ApiResponse<Sale[]>>('/sales', { params });
    return response.data;
  },

  getMetrics: async (): Promise<SalesMetrics> => {
    const response = await apiClient.get<ApiResponse<SalesMetrics>>('/sales/metrics');
    return response.data.data;
  },
};
