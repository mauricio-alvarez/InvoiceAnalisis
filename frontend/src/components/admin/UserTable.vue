<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-2xl font-bold mb-6">User Management</h2>

    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="text-gray-600 mt-2">Loading users...</p>
    </div>

    <div v-else-if="error" class="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
      {{ error }}
    </div>

    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Email
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              RUC
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Razón Social
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Role
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Registered
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="user in users" :key="user.uid" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ user.email }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ user.ruc || 'N/A' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ user.razonSocial || 'N/A' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'"
              >
                {{ user.role }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="user.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
              >
                {{ user.isActive ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(user.createdAt) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button
                @click="openEditModal(user)"
                class="text-blue-600 hover:text-blue-900"
              >
                Edit
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="totalPages > 1" class="mt-4 flex justify-center gap-2">
        <button
          @click="previousPage"
          :disabled="currentPage === 1"
          class="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        >
          Previous
        </button>
        <span class="px-4 py-2">Page {{ currentPage }} of {{ totalPages }}</span>
        <button
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-bold mb-4">Edit User</h3>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
          <select
            v-model="editForm.role"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div class="mb-4">
          <label class="flex items-center">
            <input
              v-model="editForm.isActive"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="ml-2 text-sm text-gray-700">Active</span>
          </label>
        </div>

        <div v-if="editError" class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
          {{ editError }}
        </div>

        <div class="flex gap-2">
          <button
            @click="handleUpdate"
            :disabled="updating"
            class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {{ updating ? 'Updating...' : 'Update' }}
          </button>
          <button
            @click="closeEditModal"
            class="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAdminStore } from '../../stores/admin';
import type { User } from '../../types/user';

const adminStore = useAdminStore();

const currentPage = ref(1);
const pageSize = ref(50);
const showEditModal = ref(false);
const selectedUser = ref<User | null>(null);
const editForm = ref({ role: 'user' as 'user' | 'admin', isActive: true });
const updating = ref(false);
const editError = ref('');

const users = computed(() => adminStore.users);
const loading = computed(() => adminStore.loading);
const error = computed(() => adminStore.error);
const totalUsers = computed(() => adminStore.totalUsers);
const totalPages = computed(() => Math.ceil(totalUsers.value / pageSize.value));

onMounted(async () => {
  await fetchUsers();
});

const fetchUsers = async () => {
  try {
    await adminStore.fetchUsers(currentPage.value, pageSize.value);
  } catch (err) {
    console.error('Error fetching users:', err);
  }
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const openEditModal = (user: User) => {
  selectedUser.value = user;
  editForm.value = {
    role: user.role,
    isActive: user.isActive,
  };
  showEditModal.value = true;
  editError.value = '';
};

const closeEditModal = () => {
  showEditModal.value = false;
  selectedUser.value = null;
  editError.value = '';
};

const handleUpdate = async () => {
  if (!selectedUser.value) return;
  
  updating.value = true;
  editError.value = '';
  
  try {
    await adminStore.updateUser(selectedUser.value.uid, editForm.value);
    closeEditModal();
  } catch (err: any) {
    editError.value = err.message || 'Failed to update user';
  } finally {
    updating.value = false;
  }
};

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchUsers();
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchUsers();
  }
};
</script>
