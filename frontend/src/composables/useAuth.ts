import { computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import type { UserProfile } from '../types/user';

export function useAuth() {
  const authStore = useAuthStore();

  // State
  const currentUser = computed(() => authStore.currentUser);
  const loading = computed(() => authStore.loading);
  const error = computed(() => authStore.error);
  const isAuthenticated = computed(() => authStore.isAuthenticated);
  const isAdmin = computed(() => authStore.isAdmin);
  const isVerified = computed(() => authStore.isVerified);
  const profileCompleted = computed(() => authStore.profileCompleted);

  // Methods
  const register = async (email: string, password: string) => {
    try {
      await authStore.register(email, password);
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const login = async (email: string, password: string) => {
    try {
      await authStore.login(email, password);
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const logout = async () => {
    try {
      await authStore.logout();
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const resendVerification = async () => {
    try {
      await authStore.resendVerification();
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const updateProfile = async (profileData: UserProfile) => {
    try {
      await authStore.updateProfile(profileData);
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const fetchProfile = async () => {
    try {
      await authStore.fetchProfile();
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  return {
    // State
    currentUser,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isVerified,
    profileCompleted,
    // Methods
    register,
    login,
    logout,
    resendVerification,
    updateProfile,
    fetchProfile,
  };
}
