export interface LineItem {
  description: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

export interface Invoice {
  id: string;
  userId: string;
  fileName: string;
  storageUrl: string;
  status: 'processing' | 'processed' | 'failed';
  
  // Extracted data
  invoiceNumber?: string;
  invoiceDate?: string;
  vendorName?: string;
  totalAmount?: number;
  currency?: string;
  lineItems?: LineItem[];
  
  // Metadata
  uploadedAt: string;
  processedAt?: string;
  errorMessage?: string;
}

export interface InvoiceUpload {
  file: File;
}

export interface InvoiceResponse {
  invoiceId: string;
  fileName: string;
  status: string;
  message?: string;
}

export interface InvoiceListResponse {
  invoices: Invoice[];
  total: number;
}

export interface InvoiceQuery {
  sortBy?: 'date' | 'amount' | 'vendor';
  order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}
