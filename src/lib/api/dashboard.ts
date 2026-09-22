import { apiClient } from './client';
import { ApiResponse, DashboardSummary } from '@/types';

export const dashboardApi = {
  getSummary: async (): Promise<DashboardSummary> => {
    const response = await apiClient.get<ApiResponse<DashboardSummary>>('/dashboard/summary');
    return response.data.data;
  },
};
