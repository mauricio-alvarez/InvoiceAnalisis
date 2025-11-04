import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    host: true, // Listen on all addresses
    open: true, // Open browser automatically
  },
  envPrefix: 'VITE_',
  test: {
    globals: true,
    environment: 'happy-dom',
  },
  build: {
    // Production build optimizations
    target: 'esnext',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },
    // Code splitting configuration
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks for better caching
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'firebase-vendor': ['firebase/app', 'firebase/auth'],
          'ui-vendor': ['axios'],
        },
      },
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 1000,
    // Source maps for production debugging (optional, can be disabled)
    sourcemap: false,
  },
  // Performance optimizations
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios'],
  },
})
