export interface User {
  uid: string;
  email: string;
  emailVerified: boolean;
  role: 'user' | 'admin';
  createdAt: string;
  isActive: boolean;
  lastLoginAt?: string;
  profileCompleted: boolean;
  
  // Business profile fields
  ruc?: string;
  razonSocial?: string;
  representanteLegal?: string;
  direccion?: string;
  telefono?: string;
}

export interface UserProfile {
  ruc: string;
  razonSocial: string;
  representanteLegal: string;
  direccion: string;
  telefono?: string;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserResponse {
  uid: string;
  email: string;
  message?: string;
}

export interface UserUpdate {
  role?: 'user' | 'admin';
  isActive?: boolean;
}
