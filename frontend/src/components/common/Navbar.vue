<template>
  <nav class="bg-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <router-link to="/" class="flex-shrink-0 flex items-center">
            <h1 class="text-xl font-bold text-blue-600">Invoice Platform</h1>
          </router-link>
          
          <div v-if="isAuthenticated" class="hidden md:ml-6 md:flex md:space-x-8">
            <router-link
              to="/dashboard"
              class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-blue-600"
            >
              Dashboard
            </router-link>
            <router-link
              to="/invoices"
              class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-blue-600"
            >
              Facturas
            </router-link>
            <router-link
              v-if="isAdmin"
              to="/admin"
              class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-blue-600"
            >
              Admin
            </router-link>
          </div>
        </div>

        <div class="flex items-center">
          <div v-if="isAuthenticated" class="ml-3 relative">
            <div class="flex items-center gap-4">
              <span class="text-sm text-gray-700">{{ currentUser?.email }}</span>
              <div class="relative">
                <button
                  @click="toggleMenu"
                  class="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <div class="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                    {{ userInitials }}
                  </div>
                </button>

                <div
                  v-if="showMenu"
                  class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 z-50"
                >
                  <router-link
                    to="/profile"
                    @click="closeMenu"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Perfil
                  </router-link>
                  <button
                    @click="handleLogout"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Cerrar sesión
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="flex items-center gap-4">
            <router-link
              to="/login"
              class="text-sm font-medium text-gray-900 hover:text-blue-600"
            >
              Login
            </router-link>
            <router-link
              to="/register"
              class="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
            >
              Registrar
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '../../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const showMenu = ref(false);

const isAuthenticated = computed(() => authStore.isAuthenticated);
const currentUser = computed(() => authStore.currentUser);
const isAdmin = computed(() => authStore.isAdmin);

const userInitials = computed(() => {
  if (!currentUser.value?.email) return 'U';
  return currentUser.value.email.charAt(0).toUpperCase();
});

const toggleMenu = () => {
  showMenu.value = !showMenu.value;
};

const closeMenu = () => {
  showMenu.value = false;
};

const handleLogout = async () => {
  try {
    await authStore.logout();
    closeMenu();
    router.push('/login');
  } catch (err) {
    console.error('Logout error:', err);
  }
};

// Close menu when clicking outside
if (typeof window !== 'undefined') {
  window.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    if (!target.closest('.relative')) {
      showMenu.value = false;
    }
  });
}
</script>
