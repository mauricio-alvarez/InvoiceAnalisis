<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Crear una cuenta</h1>
        <p class="mt-2 text-sm text-gray-600">
          ¿Ya tiene una cuenta?
          <router-link to="/login" class="font-medium text-blue-600 hover:text-blue-500">
            Ingrese aquí
          </router-link>
        </p>
      </div>
      
      <RegisterForm @register-success="handleRegisterSuccess" />
    </div>
  </div>
</template>

<script setup lang="ts">
import RegisterForm from '../components/auth/RegisterForm.vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const handleRegisterSuccess = () => {
  // Show success message and redirect to login after a delay
  setTimeout(() => {
    router.push('/login');
  }, 3000);
};
</script>
