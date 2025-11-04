import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router';
import { useAuthStore } from '../stores/auth';

// Import views
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import ProfileView from '../views/ProfileView.vue';
import DashboardView from '../views/DashboardView.vue';
import InvoicesView from '../views/InvoicesView.vue';
import AdminView from '../views/AdminView.vue';

// Import components for nested routes
import InvoiceUpload from '../components/invoices/InvoiceUpload.vue';
import InvoiceDetail from '../components/invoices/InvoiceDetail.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresAuth: false },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/invoices',
    name: 'Invoices',
    component: InvoicesView,
    meta: { requiresAuth: true },
  },
  {
    path: '/invoices/upload',
    name: 'InvoiceUpload',
    component: InvoiceUpload,
    meta: { 
      requiresAuth: true,
      requiresVerification: true,
      requiresProfile: true,
    },
  },
  {
    path: '/invoices/:invoiceId',
    name: 'InvoiceDetail',
    component: InvoiceDetail,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView,
    meta: { 
      requiresAuth: true,
      requiresAdmin: true,
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guards
router.beforeEach(async (
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const authStore = useAuthStore();

  // Wait for auth state to be initialized
  if (!authStore.isAuthenticated && to.meta.requiresAuth) {
    // Give some time for Firebase to initialize
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
    return;
  }

  // Redirect authenticated users away from login/register pages
  if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    next({ name: 'Dashboard' });
    return;
  }

  // Check if route requires admin role
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Dashboard' });
    return;
  }

  // Check if route requires email verification
  if (to.meta.requiresVerification && !authStore.isVerified) {
    next({ name: 'Profile' });
    return;
  }

  // Check if route requires profile completion
  if (to.meta.requiresProfile && !authStore.profileCompleted) {
    next({ name: 'Profile' });
    return;
  }

  next();
});

export default router;
