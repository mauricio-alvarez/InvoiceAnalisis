<template>
  <div id="app">
    <Navbar />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import Navbar from './components/common/Navbar.vue';
import { useAuthStore } from './stores/auth';

const authStore = useAuthStore();

onMounted(() => {
  // Initialize Firebase auth state listener
  authStore.initAuthListener();
});
</script>

<style>
#app {
  min-height: 100vh;
  background-color: #f3f4f6;
}
</style>
