<template>
  <div class="max-w-md mx-auto p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
    <div class="flex items-start">
      <div class="flex-shrink-0">
        <svg class="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <div class="ml-3 flex-1">
        <h3 class="text-lg font-medium text-yellow-800 mb-2">
          Email Verification Required
        </h3>
        <p class="text-sm text-yellow-700 mb-4">
          Please verify your email address to access all features. Check your inbox for the verification link.
        </p>
        
        <div v-if="message" class="mb-4 p-3 rounded" :class="messageClass">
          {{ message }}
        </div>
        
        <button
          @click="handleResend"
          :disabled="loading || cooldown > 0"
          class="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
        >
          {{ buttonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';
import { useAuthStore } from '../../stores/auth';
import type { User } from '../../types/user';

interface Props {
  user: User;
}

defineProps<Props>();

const authStore = useAuthStore();

const loading = ref(false);
const message = ref('');
const isError = ref(false);
const cooldown = ref(0);
let cooldownInterval: number | null = null;

const emit = defineEmits<{
  'verification-sent': [];
}>();

const messageClass = computed(() => {
  return isError.value
    ? 'bg-red-100 border border-red-400 text-red-700'
    : 'bg-green-100 border border-green-400 text-green-700';
});

const buttonText = computed(() => {
  if (loading.value) return 'Sending...';
  if (cooldown.value > 0) return `Wait ${cooldown.value}s`;
  return 'Resend Verification Email';
});

const startCooldown = () => {
  cooldown.value = 60; // 60 seconds cooldown
  cooldownInterval = window.setInterval(() => {
    cooldown.value--;
    if (cooldown.value <= 0 && cooldownInterval) {
      clearInterval(cooldownInterval);
      cooldownInterval = null;
    }
  }, 1000);
};

const handleResend = async () => {
  loading.value = true;
  message.value = '';
  isError.value = false;
  
  try {
    await authStore.resendVerification();
    message.value = 'Verification email sent! Please check your inbox.';
    isError.value = false;
    emit('verification-sent');
    startCooldown();
  } catch (err: any) {
    message.value = err.message || 'Failed to send verification email. Please try again.';
    isError.value = true;
  } finally {
    loading.value = false;
  }
};

onUnmounted(() => {
  if (cooldownInterval) {
    clearInterval(cooldownInterval);
  }
});
</script>
