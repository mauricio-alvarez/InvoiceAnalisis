import api from './api';
import type { Invoice, InvoiceResponse, InvoiceListResponse, InvoiceQuery, FeedbackRequest } from '../types/invoice';

class InvoiceService {
  /**
   * Upload a PDF invoice
   */
  async uploadInvoice(file: File): Promise<InvoiceResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<InvoiceResponse>('/api/invoices/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Get user's invoices with optional query parameters
   */
  async getInvoices(query?: InvoiceQuery): Promise<InvoiceListResponse> {
    const params = new URLSearchParams();
    
    if (query?.sortBy) params.append('sortBy', query.sortBy);
    if (query?.order) params.append('order', query.order);
    if (query?.page) params.append('page', query.page.toString());
    if (query?.limit) params.append('limit', query.limit.toString());

    const response = await api.get<InvoiceListResponse>('/api/invoices', { params });
    return response.data;
  }

  /**
   * Get invoice by ID
   */
  async getInvoiceById(invoiceId: string): Promise<Invoice> {
    const response = await api.get<Invoice>(`/api/invoices/${invoiceId}`);
    return response.data;
  }

  /**
   * Get download URL for invoice PDF
   */
  async getDownloadUrl(invoiceId: string): Promise<string> {
    const response = await api.get<{ url: string }>(`/api/invoices/${invoiceId}/download`);
    return response.data.url;
  }

  /**
   * Submit field feedback for an invoice
   */
  async submitFieldFeedback(invoiceId: string, feedback: FeedbackRequest): Promise<Invoice> {
    const response = await api.put<Invoice>(`/api/invoices/${invoiceId}/feedback`, feedback);
    return response.data;
  }
}

export const invoiceService = new InvoiceService();
