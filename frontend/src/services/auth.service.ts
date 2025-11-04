import api from './api';
import type { User, UserProfile, UserResponse } from '../types/user';

class AuthService {
  /**
   * Register a new user
   */
  async register(email: string, password: string): Promise<UserResponse> {
    const response = await api.post<UserResponse>('/api/auth/register', {
      email,
      password,
    });
    return response.data;
  }

  /**
   * Verify Firebase token with backend
   */
  async verifyToken(): Promise<User> {
    const response = await api.post<User>('/api/auth/verify-token');
    return response.data;
  }

  /**
   * Resend email verification
   */
  async resendVerification(): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/api/auth/resend-verification');
    return response.data;
  }

  /**
   * Get user profile
   */
  async getProfile(): Promise<User> {
    const response = await api.get<User>('/api/auth/profile');
    return response.data;
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData: UserProfile): Promise<User> {
    const response = await api.put<User>('/api/auth/profile', profileData);
    return response.data;
  }
}

export const authService = new AuthService();
