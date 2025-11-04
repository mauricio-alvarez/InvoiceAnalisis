<template>
  <div class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-center">Register</h2>
    
    <form @submit.prevent="handleSubmit">
      <div class="mb-4">
        <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
          Email
        </label>
        <input
          id="email"
          v-model="email"
          type="email"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.email }"
        />
        <p v-if="errors.email" class="text-red-500 text-sm mt-1">{{ errors.email }}</p>
      </div>

      <div class="mb-4">
        <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
          Password
        </label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.password }"
        />
        <p v-if="errors.password" class="text-red-500 text-sm mt-1">{{ errors.password }}</p>
      </div>

      <div class="mb-6">
        <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
          Confirm Password
        </label>
        <input
          id="confirmPassword"
          v-model="confirmPassword"
          type="password"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.confirmPassword }"
        />
        <p v-if="errors.confirmPassword" class="text-red-500 text-sm mt-1">{{ errors.confirmPassword }}</p>
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
        {{ loading ? 'Registering...' : 'Register' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const errors = ref<{ email?: string; password?: string; confirmPassword?: string }>({});
const error = ref('');
const success = ref('');
const loading = ref(false);

const emit = defineEmits<{
  'register-success': [];
  'register-error': [error: string];
}>();

const validateForm = (): boolean => {
  errors.value = {};
  
  if (!email.value) {
    errors.value.email = 'Email is required';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    errors.value.email = 'Invalid email format';
  }
  
  if (!password.value) {
    errors.value.password = 'Password is required';
  } else if (password.value.length < 6) {
    errors.value.password = 'Password must be at least 6 characters';
  }
  
  if (!confirmPassword.value) {
    errors.value.confirmPassword = 'Please confirm your password';
  } else if (password.value !== confirmPassword.value) {
    errors.value.confirmPassword = 'Passwords do not match';
  }
  
  return Object.keys(errors.value).length === 0;
};

const handleSubmit = async () => {
  if (!validateForm()) return;
  
  loading.value = true;
  error.value = '';
  success.value = '';
  
  try {
    await authStore.register(email.value, password.value);
    success.value = 'Registration successful! Please check your email to verify your account.';
    emit('register-success');
    
    // Clear form
    email.value = '';
    password.value = '';
    confirmPassword.value = '';
  } catch (err: any) {
    error.value = err.message || 'Registration failed. Please try again.';
    emit('register-error', error.value);
  } finally {
    loading.value = false;
  }
};
</script>
