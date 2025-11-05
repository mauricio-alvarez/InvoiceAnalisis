<template>
  <div class="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6">Completa los datos de tu perfil</h2>
    
    <form @submit.prevent="handleSubmit">
      <div class="mb-4">
        <label for="ruc" class="block text-sm font-medium text-gray-700 mb-2">
          RUC <span class="text-red-500">*</span>
        </label>
        <input
          id="ruc"
          v-model="formData.ruc"
          type="text"
          required
          maxlength="11"
          placeholder="11 digits"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.ruc }"
        />
        <p v-if="errors.ruc" class="text-red-500 text-sm mt-1">{{ errors.ruc }}</p>
      </div>

      <div class="mb-4">
        <label for="razonSocial" class="block text-sm font-medium text-gray-700 mb-2">
          Razón Social <span class="text-red-500">*</span>
        </label>
        <input
          id="razonSocial"
          v-model="formData.razonSocial"
          type="text"
          required
          placeholder="Business legal name"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.razonSocial }"
        />
        <p v-if="errors.razonSocial" class="text-red-500 text-sm mt-1">{{ errors.razonSocial }}</p>
      </div>

      <div class="mb-4">
        <label for="representanteLegal" class="block text-sm font-medium text-gray-700 mb-2">
          Representante Legal <span class="text-red-500">*</span>
        </label>
        <input
          id="representanteLegal"
          v-model="formData.representanteLegal"
          type="text"
          required
          placeholder="Legal representative name"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.representanteLegal }"
        />
        <p v-if="errors.representanteLegal" class="text-red-500 text-sm mt-1">{{ errors.representanteLegal }}</p>
      </div>

      <div class="mb-4">
        <label for="direccion" class="block text-sm font-medium text-gray-700 mb-2">
          Dirección <span class="text-red-500">*</span>
        </label>
        <textarea
          id="direccion"
          v-model="formData.direccion"
          required
          rows="3"
          placeholder="Business address"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.direccion }"
        ></textarea>
        <p v-if="errors.direccion" class="text-red-500 text-sm mt-1">{{ errors.direccion }}</p>
      </div>

      <div class="mb-6">
        <label for="telefono" class="block text-sm font-medium text-gray-700 mb-2">
          Teléfono (Optional)
        </label>
        <input
          id="telefono"
          v-model="formData.telefono"
          type="tel"
          placeholder="Phone number"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div v-if="error" class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
        {{ error }}
      </div>

      <div v-if="success" class="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
        {{ success }}
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {{ loading ? 'Saving...' : 'Save Profile' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../../stores/auth';
import type { UserProfile } from '../../types/user';

const authStore = useAuthStore();

const formData = ref<UserProfile>({
  ruc: '',
  razonSocial: '',
  representanteLegal: '',
  direccion: '',
  telefono: '',
});

const errors = ref<Partial<Record<keyof UserProfile, string>>>({});
const error = ref('');
const success = ref('');
const loading = ref(false);

const emit = defineEmits<{
  'profile-updated': [];
  'profile-error': [error: string];
}>();

onMounted(() => {
  // Pre-fill form if user already has profile data
  if (authStore.currentUser) {
    formData.value = {
      ruc: authStore.currentUser.ruc || '',
      razonSocial: authStore.currentUser.razonSocial || '',
      representanteLegal: authStore.currentUser.representanteLegal || '',
      direccion: authStore.currentUser.direccion || '',
      telefono: authStore.currentUser.telefono || '',
    };
  }
});

const validateForm = (): boolean => {
  errors.value = {};
  
  if (!formData.value.ruc) {
    errors.value.ruc = 'RUC is required';
  } else if (!/^\d{11}$/.test(formData.value.ruc)) {
    errors.value.ruc = 'RUC must be exactly 11 digits';
  }
  
  if (!formData.value.razonSocial) {
    errors.value.razonSocial = 'Razón Social is required';
  } else if (formData.value.razonSocial.length < 3) {
    errors.value.razonSocial = 'Razón Social must be at least 3 characters';
  }
  
  if (!formData.value.representanteLegal) {
    errors.value.representanteLegal = 'Representante Legal is required';
  } else if (formData.value.representanteLegal.length < 3) {
    errors.value.representanteLegal = 'Representante Legal must be at least 3 characters';
  }
  
  if (!formData.value.direccion) {
    errors.value.direccion = 'Dirección is required';
  } else if (formData.value.direccion.length < 10) {
    errors.value.direccion = 'Dirección must be at least 10 characters';
  }
  
  return Object.keys(errors.value).length === 0;
};

const handleSubmit = async () => {
  if (!validateForm()) return;
  
  loading.value = true;
  error.value = '';
  success.value = '';
  
  try {
    await authStore.updateProfile(formData.value);
    success.value = 'Profile updated successfully!';
    emit('profile-updated');
  } catch (err: any) {
    error.value = err.message || 'Failed to update profile. Please try again.';
    emit('profile-error', error.value);
  } finally {
    loading.value = false;
  }
};
</script>
