<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="text-gray-600 mt-2">Loading invoice details...</p>
    </div>

    <div v-else-if="error" class="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
      {{ error }}
    </div>

    <div v-else-if="invoice">
      <div class="flex justify-between items-start mb-6">
        <div>
          <h2 class="text-2xl font-bold">Invoice Details</h2>
          <p class="text-gray-600 mt-1">Invoice #{{ invoice.invoiceNumber || 'N/A' }}</p>
        </div>
        <span class="px-3 py-1 text-sm font-semibold rounded-full" :class="getStatusClass(invoice.status)">
          {{ invoice.status }}
        </span>
      </div>

      <!-- Extracted Fields Section with Feedback -->
      <div class="mb-6">
        <h3 class="text-lg font-semibold mb-4">Extracted Information</h3>
        <div class="bg-gray-50 rounded-lg p-4 space-y-3">
          <FieldFeedback v-if="invoice.invoiceNumber !== undefined" field-name="invoiceNumber"
            :field-value="invoice.invoiceNumber" :current-feedback="getFieldFeedback('invoiceNumber')"
            :invoice-id="invoice.id" @feedback="handleFeedback" />

          <FieldFeedback v-if="invoice.invoiceDate !== undefined" field-name="invoiceDate"
            :field-value="formatDate(invoice.invoiceDate)" :current-feedback="getFieldFeedback('invoiceDate')"
            :invoice-id="invoice.id" @feedback="handleFeedback" />

          <FieldFeedback v-if="invoice.dueDate !== undefined" field-name="dueDate"
            :field-value="formatDate(invoice.dueDate)" :current-feedback="getFieldFeedback('dueDate')"
            :invoice-id="invoice.id" @feedback="handleFeedback" />

          <FieldFeedback v-if="invoice.vendorName !== undefined" field-name="vendorName"
            :field-value="invoice.vendorName" :current-feedback="getFieldFeedback('vendorName')"
            :invoice-id="invoice.id" @feedback="handleFeedback" />

          <FieldFeedback v-if="invoice.supplierName !== undefined" field-name="supplierName"
            :field-value="invoice.supplierName" :current-feedback="getFieldFeedback('supplierName')"
            :invoice-id="invoice.id" @feedback="handleFeedback" />

          <FieldFeedback v-if="invoice.supplierRuc !== undefined" field-name="supplierRuc"
            :field-value="invoice.supplierRuc" :current-feedback="getFieldFeedback('supplierRuc')"
            :invoice-id="invoice.id" @feedback="handleFeedback" />

          <FieldFeedback v-if="invoice.subtotal !== undefined" field-name="subtotal"
            :field-value="formatAmount(invoice.subtotal, invoice.currency)"
            :current-feedback="getFieldFeedback('subtotal')" :invoice-id="invoice.id" @feedback="handleFeedback" />

          <FieldFeedback v-if="invoice.taxAmount !== undefined" field-name="taxAmount"
            :field-value="formatAmount(invoice.taxAmount, invoice.currency)"
            :current-feedback="getFieldFeedback('taxAmount')" :invoice-id="invoice.id" @feedback="handleFeedback" />

          <FieldFeedback v-if="invoice.totalAmount !== undefined" field-name="totalAmount"
            :field-value="formatAmount(invoice.totalAmount, invoice.currency)"
            :current-feedback="getFieldFeedback('totalAmount')" :invoice-id="invoice.id" @feedback="handleFeedback" />

          <FieldFeedback v-if="invoice.currency !== undefined" field-name="currency" :field-value="invoice.currency"
            :current-feedback="getFieldFeedback('currency')" :invoice-id="invoice.id" @feedback="handleFeedback" />
        </div>
      </div>

      <!-- OCR Engine Info -->
      <div v-if="invoice.ocrEngine" class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
        <h3 class="text-sm font-medium text-blue-800 mb-1">OCR Engine</h3>
        <p class="text-sm text-blue-600">
          Processed with: {{ invoice.ocrEngine === 'document_ai' ? 'Google Document AI' : 'Tesseract OCR' }}
          <span v-if="invoice.ocrConfidence"> (Confidence: {{ (invoice.ocrConfidence * 100).toFixed(1) }}%)</span>
        </p>
      </div>

      <!-- Additional Metadata -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 class="text-sm font-medium text-gray-500 mb-2">Uploaded</h3>
          <p class="text-lg font-semibold">{{ formatDate(invoice.uploadedAt) }}</p>
        </div>

        <div>
          <h3 class="text-sm font-medium text-gray-500 mb-2">File Name</h3>
          <p class="text-lg font-semibold">{{ invoice.fileName }}</p>
        </div>

        <div v-if="invoice.processedAt">
          <h3 class="text-sm font-medium text-gray-500 mb-2">Processed</h3>
          <p class="text-lg font-semibold">{{ formatDate(invoice.processedAt) }}</p>
        </div>
      </div>

      <div v-if="invoice.errorMessage" class="mb-6 p-4 bg-red-50 border border-red-200 rounded">
        <h3 class="text-sm font-medium text-red-800 mb-1">Error Message</h3>
        <p class="text-sm text-red-600">{{ invoice.errorMessage }}</p>
      </div>

      <div v-if="invoice.lineItems && invoice.lineItems.length > 0" class="mb-6">
        <h3 class="text-lg font-semibold mb-4">Line Items</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Unit Price
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(item, index) in invoice.lineItems" :key="index">
                <td class="px-6 py-4 text-sm text-gray-900">{{ item.description }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">{{ item.quantity }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">{{ formatAmount(item.unitPrice, invoice.currency) }}</td>
                <td class="px-6 py-4 text-sm text-gray-900 font-medium">{{ formatAmount(item.totalPrice,
                  invoice.currency) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="flex gap-4">
        <button @click="handleDownload" :disabled="downloadLoading"
          class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed">
          {{ downloadLoading ? 'Loading...' : 'Download PDF' }}
        </button>
        <button @click="goBack" class="bg-gray-200 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-300">
          Back to List
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useInvoiceStore } from '../../stores/invoices';
import { useRouter } from 'vue-router';
import FieldFeedback from './FieldFeedback.vue';

interface Props {
  invoiceId: string;
}

const props = defineProps<Props>();

const invoiceStore = useInvoiceStore();
const router = useRouter();

const downloadLoading = ref(false);
const feedbackLoading = ref(false);

const invoice = computed(() => invoiceStore.currentInvoice);
const loading = computed(() => invoiceStore.loading);
const error = computed(() => invoiceStore.error);

onMounted(async () => {
  try {
    await invoiceStore.fetchInvoiceDetail(props.invoiceId);
  } catch (err) {
    console.error('Error fetching invoice details:', err);
  }
});

const formatDate = (dateString?: string): string => {
  if (!dateString) return 'N/A';
  
  // Parse date as local date to avoid timezone issues
  // If date is in format "YYYY-MM-DD", parse it directly
  const parts = dateString.split('-');
  if (parts.length === 3) {
    const year = parseInt(parts[0]);
    const month = parseInt(parts[1]) - 1; // Month is 0-indexed
    const day = parseInt(parts[2]);
    const date = new Date(year, month, day);
    
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }
  
  // Fallback for other date formats
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

const formatAmount = (amount?: number, currency?: string): string => {
  if (amount === undefined || amount === null) return 'N/A';
  return `${currency || '$'} ${amount.toFixed(2)}`;
};

const getStatusClass = (status: string): string => {
  switch (status) {
    case 'processed':
      return 'bg-green-100 text-green-800';
    case 'processing':
      return 'bg-yellow-100 text-yellow-800';
    case 'failed':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const handleDownload = async () => {
  downloadLoading.value = true;
  try {
    const url = await invoiceStore.getDownloadUrl(props.invoiceId);
    window.open(url, '_blank');
  } catch (err) {
    console.error('Error downloading invoice:', err);
  } finally {
    downloadLoading.value = false;
  }
};

const goBack = () => {
  router.push('/invoices');
};

const getFieldFeedback = (fieldName: string): 'upvote' | 'downvote' | null => {
  if (!invoice.value?.fieldFeedback) return null;
  const feedback = invoice.value.fieldFeedback[fieldName];
  return feedback ? feedback.vote : null;
};

const handleFeedback = async ({ fieldName, vote }: { fieldName: string; vote: 'upvote' | 'downvote' | 'remove' }) => {
  if (feedbackLoading.value || !invoice.value) {
    console.log('Feedback blocked:', { feedbackLoading: feedbackLoading.value, hasInvoice: !!invoice.value });
    return;
  }

  feedbackLoading.value = true;

  try {
    console.log('Submitting feedback:', { invoiceId: props.invoiceId, fieldName, vote });
    await invoiceStore.submitFieldFeedback(props.invoiceId, fieldName, vote);
    console.log('Feedback submitted successfully');
  } catch (err) {
    console.error('Error submitting feedback:', err);
    // Error is already handled in the store and FieldFeedback component
  } finally {
    feedbackLoading.value = false;
  }
};
</script>
