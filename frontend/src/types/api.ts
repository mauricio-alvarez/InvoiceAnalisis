export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  success?: boolean;
}

export interface ApiError {
  code: string;
  message: string;
  details?: any;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface Statistics {
  totalUsers: number;
  totalInvoices: number;
  totalAmount: number;
  successRate: number;
  activeUsers?: number;
  processingInvoices?: number;
  failedInvoices?: number;
}
