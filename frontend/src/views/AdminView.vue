<template>
  <div class="min-h-screen bg-gray-100">
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Admin Panel</h1>
          <p class="mt-2 text-sm text-gray-600">
            Manage users, invoices, and view platform statistics
          </p>
        </div>

        <div class="mb-6">
          <div class="border-b border-gray-200">
            <nav class="-mb-px flex space-x-8">
              <button
                @click="activeTab = 'dashboard'"
                :class="[
                  activeTab === 'dashboard'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
                ]"
              >
                Dashboard
              </button>
              <button
                @click="activeTab = 'users'"
                :class="[
                  activeTab === 'users'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
                ]"
              >
                Users
              </button>
              <button
                @click="activeTab = 'invoices'"
                :class="[
                  activeTab === 'invoices'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
                ]"
              >
                Invoices
              </button>
            </nav>
          </div>
        </div>

        <div v-if="activeTab === 'dashboard'">
          <Dashboard />
        </div>

        <div v-if="activeTab === 'users'">
          <UserTable />
        </div>

        <div v-if="activeTab === 'invoices'">
          <InvoiceTable />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Dashboard from '../components/admin/Dashboard.vue';
import UserTable from '../components/admin/UserTable.vue';
import InvoiceTable from '../components/admin/InvoiceTable.vue';

const activeTab = ref<'dashboard' | 'users' | 'invoices'>('dashboard');
</script>
