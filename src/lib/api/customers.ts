import { apiClient } from './client';
import { ApiResponse, Customer, CustomerQueryParams } from '@/types';

export const customersApi = {
  getCustomers: async (params?: CustomerQueryParams): Promise<ApiResponse<Customer[]>> => {
    const response = await apiClient.get<ApiResponse<Customer[]>>('/customers', { params });
    return response.data;
  },

  getCustomerById: async (customerId: string): Promise<Customer> => {
    const response = await apiClient.get<ApiResponse<Customer>>(`/customers/${customerId}`);
    return response.data.data;
  },
};
