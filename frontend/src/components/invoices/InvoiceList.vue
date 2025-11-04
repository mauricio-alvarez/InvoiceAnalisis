<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">My Invoices</h2>
      <div class="flex gap-2">
        <select
          v-model="sortBy"
          @change="handleSort"
          class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="date">Sort by Date</option>
          <option value="amount">Sort by Amount</option>
          <option value="vendor">Sort by Vendor</option>
        </select>
        <select
          v-model="filterBy"
          @change="handleFilter"
          class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Status</option>
          <option value="processing">Processing</option>
          <option value="processed">Processed</option>
          <option value="failed">Failed</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="text-gray-600 mt-2">Loading invoices...</p>
    </div>

    <div v-else-if="error" class="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
      {{ error }}
    </div>

    <div v-else-if="invoices.length === 0" class="text-center py-8">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-600 mt-2">No invoices found</p>
    </div>

    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Invoice #
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Vendor
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Amount
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Uploaded
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="invoice in invoices" :key="invoice.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ invoice.invoiceNumber || 'N/A' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(invoice.invoiceDate) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ invoice.vendorName || 'N/A' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatAmount(invoice.totalAmount, invoice.currency) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="getStatusClass(invoice.status)"
              >
                {{ invoice.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(invoice.uploadedAt) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button
                @click="viewDetails(invoice.id)"
                class="text-blue-600 hover:text-blue-900 mr-3"
              >
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useInvoiceStore } from '../../stores/invoices';
import { useRouter } from 'vue-router';

const invoiceStore = useInvoiceStore();
const router = useRouter();

const sortBy = ref('date');
const filterBy = ref('');

const invoices = computed(() => invoiceStore.sortedInvoices);
const loading = computed(() => invoiceStore.loading);
const error = computed(() => invoiceStore.error);

onMounted(async () => {
  await fetchInvoices();
});

const fetchInvoices = async () => {
  try {
    await invoiceStore.fetchInvoices({
      sortBy: sortBy.value as any,
      order: 'desc',
    });
  } catch (err) {
    console.error('Error fetching invoices:', err);
  }
};

const handleSort = () => {
  fetchInvoices();
};

const handleFilter = () => {
  // Filter logic would be implemented here
  fetchInvoices();
};

const formatDate = (dateString?: string): string => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
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

const viewDetails = (invoiceId: string) => {
  router.push(`/invoices/${invoiceId}`);
};
</script>
