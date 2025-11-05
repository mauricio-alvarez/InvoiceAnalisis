<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Bienvenido</h1>
        <p class="mt-2 text-sm text-gray-600">
          ¿No tiene una cuenta?
          <router-link to="/register" class="font-medium text-blue-600 hover:text-blue-500">
            Cree una cuenta aquí
          </router-link>
        </p>
      </div>
      
      <LoginForm @login-success="handleLoginSuccess" />
    </div>
  </div>
</template>

<script setup lang="ts">
import LoginForm from '../components/auth/LoginForm.vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const handleLoginSuccess = () => {
  // Redirect is handled in the LoginForm component
  console.log('Login successful');
};
</script>
