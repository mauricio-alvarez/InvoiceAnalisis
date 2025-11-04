import axios, { AxiosError } from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { auth } from './firebase';

// Create Axios instance with base configuration
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach Firebase Auth token
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    try {
      const user = auth.currentUser;
      if (user) {
        const token = await user.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data: any = error.response.data;

      switch (status) {
        case 401:
          console.error('Unauthorized - Invalid or expired token');
          // Could trigger logout here
          break;
        case 403:
          console.error('Forbidden - Insufficient permissions');
          break;
        case 404:
          console.error('Resource not found');
          break;
        case 500:
          console.error('Server error');
          break;
        default:
          console.error(`Error ${status}:`, data?.error?.message || error.message);
      }

      return Promise.reject({
        code: data?.error?.code || `http/${status}`,
        message: data?.error?.message || error.message,
        details: data?.error?.details,
      });
    } else if (error.request) {
      // Request made but no response received
      console.error('Network error - No response from server');
      return Promise.reject({
        code: 'network-error',
        message: 'Unable to connect to server. Please check your internet connection.',
      });
    } else {
      // Error in request setup
      console.error('Request error:', error.message);
      return Promise.reject({
        code: 'request-error',
        message: error.message,
      });
    }
  }
);

export default api;
