<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold">Admin Dashboard</h2>

    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="text-gray-600 mt-2">Loading statistics...</p>
    </div>

    <div v-else-if="error" class="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
      {{ error }}
    </div>

    <div v-else-if="statistics" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Total Users Card -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Users</p>
            <p class="text-3xl font-bold text-gray-900 mt-2">{{ statistics.totalUsers }}</p>
          </div>
          <div class="bg-blue-100 rounded-full p-3">
            <svg class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
        </div>
        <p v-if="statistics.activeUsers !== undefined" class="text-sm text-gray-500 mt-2">
          {{ statistics.activeUsers }} active
        </p>
      </div>

      <!-- Total Invoices Card -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Invoices</p>
            <p class="text-3xl font-bold text-gray-900 mt-2">{{ statistics.totalInvoices }}</p>
          </div>
          <div class="bg-green-100 rounded-full p-3">
            <svg class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
        <p v-if="statistics.processingInvoices !== undefined" class="text-sm text-gray-500 mt-2">
          {{ statistics.processingInvoices }} processing
        </p>
      </div>

      <!-- Total Amount Card -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Amount</p>
            <p class="text-3xl font-bold text-gray-900 mt-2">{{ formatAmount(statistics.totalAmount) }}</p>
          </div>
          <div class="bg-yellow-100 rounded-full p-3">
            <svg class="h-8 w-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Success Rate Card -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Success Rate</p>
            <p class="text-3xl font-bold text-gray-900 mt-2">{{ formatPercentage(statistics.successRate) }}</p>
          </div>
          <div class="bg-purple-100 rounded-full p-3">
            <svg class="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
        <p v-if="statistics.failedInvoices !== undefined" class="text-sm text-gray-500 mt-2">
          {{ statistics.failedInvoices }} failed
        </p>
      </div>
    </div>

    <!-- Additional Info Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Recent Activity -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold mb-4">Quick Stats</h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Active Users</span>
            <span class="text-sm font-semibold">{{ statistics.activeUsers || 0 }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Processing Invoices</span>
            <span class="text-sm font-semibold">{{ statistics.processingInvoices || 0 }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Failed Invoices</span>
            <span class="text-sm font-semibold text-red-600">{{ statistics.failedInvoices || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- System Health -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold mb-4">System Health</h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Processing Success Rate</span>
            <span class="text-sm font-semibold text-green-600">{{ formatPercentage(statistics.successRate) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Total Revenue</span>
            <span class="text-sm font-semibold">{{ formatAmount(statistics.totalAmount) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Average per Invoice</span>
            <span class="text-sm font-semibold">
              {{ formatAmount(statistics.totalInvoices > 0 ? statistics.totalAmount / statistics.totalInvoices : 0) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useAdminStore } from '../../stores/admin';

const adminStore = useAdminStore();

const statistics = computed(() => adminStore.statistics);
const loading = computed(() => adminStore.loading);
const error = computed(() => adminStore.error);

onMounted(async () => {
  try {
    await adminStore.fetchStatistics();
  } catch (err) {
    console.error('Error fetching statistics:', err);
  }
});

const formatAmount = (amount: number): string => {
  return `$${amount.toFixed(2)}`;
};

const formatPercentage = (rate: number): string => {
  return `${(rate * 100).toFixed(1)}%`;
};
</script>
