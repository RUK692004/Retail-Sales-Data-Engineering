import { apiClient } from './client';
import {
  ApiResponse,
  DataQualitySummary,
  DataQualityIssue,
  DataQualityQueryParams,
} from '@/types';

export const dataQualityApi = {
  getSummary: async (): Promise<DataQualitySummary> => {
    const response = await apiClient.get<ApiResponse<DataQualitySummary>>('/data-quality/summary');
    return response.data.data;
  },

  getIssues: async (params?: DataQualityQueryParams): Promise<ApiResponse<DataQualityIssue[]>> => {
    const response = await apiClient.get<ApiResponse<DataQualityIssue[]>>('/data-quality/issues', {
      params,
    });
    return response.data;
  },
};
