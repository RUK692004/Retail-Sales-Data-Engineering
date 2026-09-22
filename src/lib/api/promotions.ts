import { apiClient } from './client';
import { ApiResponse, Promotion, PromotionQueryParams } from '@/types';

export const promotionsApi = {
  getPromotions: async (params?: PromotionQueryParams): Promise<ApiResponse<Promotion[]>> => {
    const response = await apiClient.get<ApiResponse<Promotion[]>>('/promotions', { params });
    return response.data;
  },
};
