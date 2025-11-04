import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  signInWithEmailAndPassword,
  signOut,
  sendEmailVerification,
  onAuthStateChanged
} from 'firebase/auth';
import type { User as FirebaseUser } from 'firebase/auth';
import { auth } from '../services/firebase';
import type { User, UserProfile } from '../types/user';
import { authService } from '../services/auth.service.js';

export const useAuthStore = defineStore('auth', () => {
  // State
  const currentUser = ref<User | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const isAuthenticated = ref(false);

  // Getters
  const isAdmin = computed(() => currentUser.value?.role === 'admin');
  const isVerified = computed(() => currentUser.value?.emailVerified || false);
  const profileCompleted = computed(() => currentUser.value?.profileCompleted || false);

  // Actions
  const register = async (email: string, password: string) => {
    loading.value = true;
    error.value = null;
    try {
      // Register user via backend API (handles both Firebase Auth and Firestore)
      await authService.register(email, password);

      // Backend creates the user, so registration is successful
      return { email };
    } catch (err: any) {
      error.value = err.message || 'Registration failed';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const login = async (email: string, password: string) => {
    loading.value = true;
    error.value = null;
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      return userCredential.user;
    } catch (err: any) {
      error.value = err.message || 'Login failed';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const logout = async () => {
    loading.value = true;
    error.value = null;
    try {
      await signOut(auth);
      currentUser.value = null;
      isAuthenticated.value = false;
    } catch (err: any) {
      error.value = err.message || 'Logout failed';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const verifyEmail = async () => {
    loading.value = true;
    error.value = null;
    try {
      if (auth.currentUser) {
        await sendEmailVerification(auth.currentUser);
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to send verification email';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const resendVerification = async () => {
    loading.value = true;
    error.value = null;
    try {
      await authService.resendVerification();
    } catch (err: any) {
      error.value = err.message || 'Failed to resend verification email';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchProfile = async () => {
    loading.value = true;
    error.value = null;
    try {
      const profile = await authService.getProfile();
      currentUser.value = profile;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch profile';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateProfile = async (profileData: UserProfile) => {
    loading.value = true;
    error.value = null;
    try {
      const updatedUser = await authService.updateProfile(profileData);
      currentUser.value = updatedUser;
    } catch (err: any) {
      error.value = err.message || 'Failed to update profile';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Initialize auth state listener
  const initAuthListener = () => {
    onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
      if (firebaseUser) {
        isAuthenticated.value = true;
        try {
          // Fetch full user profile from backend
          await fetchProfile();
        } catch (err) {
          console.error('Error fetching user profile:', err);
        }
      } else {
        isAuthenticated.value = false;
        currentUser.value = null;
      }
    });
  };

  return {
    // State
    currentUser,
    loading,
    error,
    isAuthenticated,
    // Getters
    isAdmin,
    isVerified,
    profileCompleted,
    // Actions
    register,
    login,
    logout,
    verifyEmail,
    resendVerification,
    fetchProfile,
    updateProfile,
    initAuthListener,
  };
});
