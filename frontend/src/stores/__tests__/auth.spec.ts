import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from '../auth';

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('initializes with correct default state', () => {
    const store = useAuthStore();
    
    expect(store.currentUser).toBeNull();
    expect(store.isAuthenticated).toBe(false);
    expect(store.loading).toBe(false);
    expect(store.error).toBeNull();
  });

  it('computes isAdmin correctly', () => {
    const store = useAuthStore();
    
    expect(store.isAdmin).toBe(false);
  });

  it('computes isVerified correctly', () => {
    const store = useAuthStore();
    
    expect(store.isVerified).toBe(false);
  });

  it('computes profileCompleted correctly', () => {
    const store = useAuthStore();
    
    expect(store.profileCompleted).toBe(false);
  });
});
