<template>
  <div class="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Profile</h1>
        <p class="mt-2 text-sm text-gray-600">
          Manage your business profile information
        </p>
      </div>

      <EmailVerification
        v-if="currentUser && !currentUser.emailVerified"
        :user="currentUser"
        class="mb-6"
      />

      <ProfileForm @profile-updated="handleProfileUpdated" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import ProfileForm from '../components/auth/ProfileForm.vue';
import EmailVerification from '../components/auth/EmailVerification.vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const currentUser = computed(() => authStore.currentUser);

const handleProfileUpdated = () => {
  // Optionally redirect to dashboard after profile update
  setTimeout(() => {
    router.push('/dashboard');
  }, 2000);
};
</script>
