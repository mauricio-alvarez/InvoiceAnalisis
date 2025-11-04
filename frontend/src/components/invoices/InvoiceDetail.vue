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
        <span
          class="px-3 py-1 text-sm font-semibold rounded-full"
          :class="getStatusClass(invoice.status)"
        >
          {{ invoice.status }}
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 class="text-sm font-medium text-gray-500 mb-2">Vendor Information</h3>
          <p class="text-lg font-semibold">{{ invoice.vendorName || 'N/A' }}</p>
        </div>

        <div>
          <h3 class="text-sm font-medium text-gray-500 mb-2">Invoice Date</h3>
          <p class="text-lg font-semibold">{{ formatDate(invoice.invoiceDate) }}</p>
        </div>

        <div>
          <h3 class="text-sm font-medium text-gray-500 mb-2">Total Amount</h3>
          <p class="text-lg font-semibold">{{ formatAmount(invoice.totalAmount, invoice.currency) }}</p>
        </div>

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
                <td class="px-6 py-4 text-sm text-gray-900 font-medium">{{ formatAmount(item.totalPrice, invoice.currency) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="flex gap-4">
        <button
          @click="handleDownload"
          :disabled="downloadLoading"
          class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {{ downloadLoading ? 'Loading...' : 'Download PDF' }}
        </button>
        <button
          @click="goBack"
          class="bg-gray-200 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-300"
        >
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

interface Props {
  invoiceId: string;
}

const props = defineProps<Props>();

const invoiceStore = useInvoiceStore();
const router = useRouter();

const downloadLoading = ref(false);

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
</script>
