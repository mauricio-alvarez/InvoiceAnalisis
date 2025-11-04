import api from './api';
import type { User, UserUpdate } from '../types/user';
import type { Invoice } from '../types/invoice';
import type { Statistics } from '../types/api';

interface UsersResponse {
  users: User[];
  total: number;
  page: number;
}

interface InvoicesResponse {
  invoices: Invoice[];
  total: number;
}

interface InvoiceFilters {
  userId?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
}

class AdminService {
  /**
   * Get all users with pagination
   */
  async getUsers(page: number = 1, limit: number = 50): Promise<UsersResponse> {
    const response = await api.get<UsersResponse>('/api/admin/users', {
      params: { page, limit },
    });
    return response.data;
  }

  /**
   * Update user properties
   */
  async updateUser(userId: string, updates: UserUpdate): Promise<User> {
    const response = await api.patch<User>(`/api/admin/users/${userId}`, updates);
    return response.data;
  }

  /**
   * Get all invoices with optional filters
   */
  async getAllInvoices(filters?: InvoiceFilters): Promise<InvoicesResponse> {
    const params = new URLSearchParams();
    
    if (filters?.userId) params.append('userId', filters.userId);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.startDate) params.append('startDate', filters.startDate);
    if (filters?.endDate) params.append('endDate', filters.endDate);

    const response = await api.get<InvoicesResponse>('/api/admin/invoices', { params });
    return response.data;
  }

  /**
   * Get platform statistics
   */
  async getStatistics(): Promise<Statistics> {
    const response = await api.get<Statistics>('/api/admin/statistics');
    return response.data;
  }
}

export const adminService = new AdminService();
