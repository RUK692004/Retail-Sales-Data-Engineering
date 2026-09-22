import { apiClient } from './client';
import { ApiResponse, InventoryItem, InventoryQueryParams } from '@/types';

export const inventoryApi = {
  getInventory: async (params?: InventoryQueryParams): Promise<ApiResponse<InventoryItem[]>> => {
    const response = await apiClient.get<ApiResponse<InventoryItem[]>>('/inventory', { params });
    return response.data;
  },
};
