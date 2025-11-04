import { computed } from 'vue';
import { useInvoiceStore } from '../stores/invoices';
import type { InvoiceQuery } from '../types/invoice';

export function useInvoices() {
  const invoiceStore = useInvoiceStore();

  // State
  const invoices = computed(() => invoiceStore.invoices);
  const currentInvoice = computed(() => invoiceStore.currentInvoice);
  const loading = computed(() => invoiceStore.loading);
  const error = computed(() => invoiceStore.error);
  const sortedInvoices = computed(() => invoiceStore.sortedInvoices);
  const totalInvoices = computed(() => invoiceStore.totalInvoices);
  const processingInvoices = computed(() => invoiceStore.processingInvoices);
  const processedInvoices = computed(() => invoiceStore.processedInvoices);
  const failedInvoices = computed(() => invoiceStore.failedInvoices);

  // Methods
  const fetchInvoices = async (query?: InvoiceQuery) => {
    try {
      await invoiceStore.fetchInvoices(query);
      return { success: true };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const uploadInvoice = async (file: File) => {
    try {
      const response = await invoiceStore.uploadInvoice(file);
      return { success: true, data: response };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const fetchInvoiceDetail = async (invoiceId: string) => {
    try {
      const invoice = await invoiceStore.fetchInvoiceDetail(invoiceId);
      return { success: true, data: invoice };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const getDownloadUrl = async (invoiceId: string) => {
    try {
      const url = await invoiceStore.getDownloadUrl(invoiceId);
      return { success: true, data: url };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  };

  const clearError = () => {
    invoiceStore.clearError();
  };

  const clearCurrentInvoice = () => {
    invoiceStore.clearCurrentInvoice();
  };

  return {
    // State
    invoices,
    currentInvoice,
    loading,
    error,
    sortedInvoices,
    totalInvoices,
    processingInvoices,
    processedInvoices,
    failedInvoices,
    // Methods
    fetchInvoices,
    uploadInvoice,
    fetchInvoiceDetail,
    getDownloadUrl,
    clearError,
    clearCurrentInvoice,
  };
}
