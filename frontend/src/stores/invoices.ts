import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Invoice, InvoiceQuery } from '../types/invoice';
import { invoiceService } from '../services/invoice.service';

export const useInvoiceStore = defineStore('invoices', () => {
  // State
  const invoices = ref<Invoice[]>([]);
  const currentInvoice = ref<Invoice | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const total = ref(0);

  // Getters
  const sortedInvoices = computed(() => {
    return [...invoices.value].sort((a, b) => {
      const dateA = new Date(a.uploadedAt).getTime();
      const dateB = new Date(b.uploadedAt).getTime();
      return dateB - dateA; // Descending order
    });
  });

  const totalInvoices = computed(() => total.value);

  const processingInvoices = computed(() => {
    return invoices.value.filter(inv => inv.status === 'processing').length;
  });

  const processedInvoices = computed(() => {
    return invoices.value.filter(inv => inv.status === 'processed').length;
  });

  const failedInvoices = computed(() => {
    return invoices.value.filter(inv => inv.status === 'failed').length;
  });

  // Actions
  const fetchInvoices = async (query?: InvoiceQuery) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await invoiceService.getInvoices(query);
      invoices.value = response.invoices;
      total.value = response.total;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch invoices';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const uploadInvoice = async (file: File) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await invoiceService.uploadInvoice(file);
      // Refresh invoice list after upload
      await fetchInvoices();
      return response;
    } catch (err: any) {
      error.value = err.message || 'Failed to upload invoice';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchInvoiceDetail = async (invoiceId: string) => {
    loading.value = true;
    error.value = null;
    try {
      const invoice = await invoiceService.getInvoiceById(invoiceId);
      currentInvoice.value = invoice;
      return invoice;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch invoice details';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getDownloadUrl = async (invoiceId: string) => {
    loading.value = true;
    error.value = null;
    try {
      const url = await invoiceService.getDownloadUrl(invoiceId);
      return url;
    } catch (err: any) {
      error.value = err.message || 'Failed to get download URL';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const clearError = () => {
    error.value = null;
  };

  const clearCurrentInvoice = () => {
    currentInvoice.value = null;
  };

  const submitFieldFeedback = async (invoiceId: string, fieldName: string, vote: 'upvote' | 'downvote' | 'remove') => {
    error.value = null;
    try {
      const updatedInvoice: Invoice = await invoiceService.submitFieldFeedback(invoiceId, { fieldName, vote });
      
      // Validate response
      if (!updatedInvoice || !updatedInvoice.id) {
        throw new Error('Invalid response from server');
      }
      
      // Update currentInvoice with new feedback data
      if (currentInvoice.value && currentInvoice.value.id === invoiceId) {
        // Preserve the current invoice and only update the fieldFeedback
        currentInvoice.value = {
          ...currentInvoice.value,
          ...updatedInvoice,
          fieldFeedback: updatedInvoice.fieldFeedback || {}
        };
      }
      
      // Also update in the invoices list if present
      const index = invoices.value.findIndex(inv => inv.id === invoiceId);
      if (index !== -1) {
        invoices.value[index] = {
          ...invoices.value[index],
          ...updatedInvoice,
          fieldFeedback: updatedInvoice.fieldFeedback || {}
        };
      }
      
      return { success: true, invoice: updatedInvoice };
    } catch (err: any) {
      error.value = err.message || 'Failed to submit feedback';
      throw err;
    }
  };

  return {
    // State
    invoices,
    currentInvoice,
    loading,
    error,
    total,
    // Getters
    sortedInvoices,
    totalInvoices,
    processingInvoices,
    processedInvoices,
    failedInvoices,
    // Actions
    fetchInvoices,
    uploadInvoice,
    fetchInvoiceDetail,
    getDownloadUrl,
    submitFieldFeedback,
    clearError,
    clearCurrentInvoice,
  };
});
