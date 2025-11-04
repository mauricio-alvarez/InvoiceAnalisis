import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, UserUpdate } from '../types/user';
import type { Invoice } from '../types/invoice';
import type { Statistics } from '../types/api';
import { adminService } from '../services/admin.service';

export const useAdminStore = defineStore('admin', () => {
  // State
  const users = ref<User[]>([]);
  const allInvoices = ref<Invoice[]>([]);
  const statistics = ref<Statistics | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const totalUsers = ref(0);
  const totalInvoices = ref(0);

  // Getters
  const activeUsers = computed(() => {
    return users.value.filter(user => user.isActive).length;
  });

  const totalRevenue = computed(() => {
    return allInvoices.value.reduce((sum, invoice) => {
      return sum + (invoice.totalAmount || 0);
    }, 0);
  });

  const adminUsers = computed(() => {
    return users.value.filter(user => user.role === 'admin');
  });

  const regularUsers = computed(() => {
    return users.value.filter(user => user.role === 'user');
  });

  // Actions
  const fetchUsers = async (page: number = 1, limit: number = 50) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await adminService.getUsers(page, limit);
      users.value = response.users;
      totalUsers.value = response.total;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch users';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateUser = async (userId: string, updates: UserUpdate) => {
    loading.value = true;
    error.value = null;
    try {
      const updatedUser = await adminService.updateUser(userId, updates);
      
      // Update user in local state
      const index = users.value.findIndex(u => u.uid === userId);
      if (index !== -1) {
        users.value[index] = updatedUser;
      }
      
      return updatedUser;
    } catch (err: any) {
      error.value = err.message || 'Failed to update user';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchAllInvoices = async (filters?: {
    userId?: string;
    status?: string;
    startDate?: string;
    endDate?: string;
  }) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await adminService.getAllInvoices(filters);
      allInvoices.value = response.invoices;
      totalInvoices.value = response.total;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch invoices';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchStatistics = async () => {
    loading.value = true;
    error.value = null;
    try {
      const stats = await adminService.getStatistics();
      statistics.value = stats;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch statistics';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const clearError = () => {
    error.value = null;
  };

  return {
    // State
    users,
    allInvoices,
    statistics,
    loading,
    error,
    totalUsers,
    totalInvoices,
    // Getters
    activeUsers,
    totalRevenue,
    adminUsers,
    regularUsers,
    // Actions
    fetchUsers,
    updateUser,
    fetchAllInvoices,
    fetchStatistics,
    clearError,
  };
});
