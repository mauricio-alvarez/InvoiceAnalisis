<template>
  <div class="min-h-screen bg-gray-100">
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="mb-8 flex justify-between items-center">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Facturas</h1>
            <p class="mt-2 text-sm text-gray-600">
              Controle y visualice las facturas subidas.
            </p>
          </div>
          <router-link
            to="/invoices/upload"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Subir Factura
          </router-link>
        </div>

        <InvoiceList />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import InvoiceList from '../components/invoices/InvoiceList.vue';
</script>
