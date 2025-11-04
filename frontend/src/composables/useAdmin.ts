import { computed } from 'vue';
import { useAdminStore } from '../stores/admin';
import type { UserUpdate } from '../types/user';

export function useAdmin() {
  const adminStore = useAdminStore();

  // State
  const users = computed(() => adminStore.users);
  const allInvoices = computed(() => adminStore.allInvoices);
  const statistics = computed(() => adminStore.statistics);
  const loading = computed(() => adminStore.loading);
  const error = computed(() => adminStore.error);
  const totalUsers = computed(() => adminStore.totalUsers);
  const totalInvoices = computed(() => adminStore.totalInvoices);
  const activeUsers = computed(() => adminStore.activeUsers);
  const totalRevenue = computed(() => adminStore.totalRevenue);
  const adminUsers = computed(() => adminStore.adminUsers);
  const regularUsers = computed(() => adminStore.regularUsers);

  // Methods
  const fetchUsers = async (page: number = 1, limit: number = 50) => {
    try {
      await adminStore.fetchUsers(page, limit);
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const updateUser = async (userId: string, updates: UserUpdate) => {
    try {
      const updatedUser = await adminStore.updateUser(userId, updates);
      return { success: true, data: updatedUser };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const fetchAllInvoices = async (filters?: {
    userId?: string;
    status?: string;
    startDate?: string;
    endDate?: string;
  }) => {
    try {
      await adminStore.fetchAllInvoices(filters);
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const fetchStatistics = async () => {
    try {
      await adminStore.fetchStatistics();
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const clearError = () => {
    adminStore.clearError();
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
    activeUsers,
    totalRevenue,
    adminUsers,
    regularUsers,
    // Methods
    fetchUsers,
    updateUser,
    fetchAllInvoices,
    fetchStatistics,
    clearError,
  };
}
