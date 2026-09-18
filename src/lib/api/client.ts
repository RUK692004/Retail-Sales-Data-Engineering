import axios from 'axios';

const baseURL = process.env.NEXT_PUBLIC_API_URL || '/api';

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const formattedError = {
      message: error.response?.data?.message || error.message || 'An unexpected error occurred',
      code: error.response?.status ? `ERR_${error.response.status}` : 'ERR_NETWORK',
      details: error.response?.data,
    };
    return Promise.reject(formattedError);
  }
);
