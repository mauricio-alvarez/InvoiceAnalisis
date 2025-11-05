export interface LineItem {
  description: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

export interface FieldFeedback {
  vote: 'upvote' | 'downvote';
  userId: string;
  timestamp: string;
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
  dueDate?: string;
  vendorName?: string;
  supplierName?: string;
  supplierRuc?: string;
  totalAmount?: number;
  taxAmount?: number;
  subtotal?: number;
  currency?: string;
  lineItems?: LineItem[];
  
  // OCR metadata
  ocrEngine?: 'document_ai' | 'tesseract';
  ocrConfidence?: number;
  
  // Field feedback
  fieldFeedback?: {
    [fieldName: string]: FieldFeedback;
  };
  
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

export interface FeedbackRequest {
  fieldName: string;
  vote: 'upvote' | 'downvote' | 'remove';
}

export interface FeedbackResponse {
  success: boolean;
  invoice: Invoice;
}
