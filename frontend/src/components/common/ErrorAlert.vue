<template>
  <div
    v-if="show"
    class="rounded-md p-4"
    :class="[bgClass, borderClass]"
    role="alert"
  >
    <div class="flex">
      <div class="flex-shrink-0">
        <svg
          class="h-5 w-5"
          :class="iconClass"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
            clip-rule="evenodd"
          />
        </svg>
      </div>
      <div class="ml-3 flex-1">
        <h3 v-if="title" class="text-sm font-medium" :class="titleClass">
          {{ title }}
        </h3>
        <div class="text-sm" :class="[messageClass, title ? 'mt-2' : '']">
          <p>{{ message }}</p>
        </div>
      </div>
      <div v-if="dismissible" class="ml-auto pl-3">
        <button
          @click="handleDismiss"
          class="-mx-1.5 -my-1.5 rounded-md p-1.5 inline-flex focus:outline-none focus:ring-2 focus:ring-offset-2"
          :class="[buttonClass, focusClass]"
        >
          <span class="sr-only">Dismiss</span>
          <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  message: string;
  title?: string;
  type?: 'error' | 'warning' | 'info';
  dismissible?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  type: 'error',
  dismissible: true,
});

const emit = defineEmits<{
  dismiss: [];
}>();

const show = ref(true);

const bgClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'bg-yellow-50';
    case 'info':
      return 'bg-blue-50';
    default:
      return 'bg-red-50';
  }
});

const borderClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'border border-yellow-200';
    case 'info':
      return 'border border-blue-200';
    default:
      return 'border border-red-200';
  }
});

const iconClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'text-yellow-400';
    case 'info':
      return 'text-blue-400';
    default:
      return 'text-red-400';
  }
});

const titleClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'text-yellow-800';
    case 'info':
      return 'text-blue-800';
    default:
      return 'text-red-800';
  }
});

const messageClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'text-yellow-700';
    case 'info':
      return 'text-blue-700';
    default:
      return 'text-red-700';
  }
});

const buttonClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'text-yellow-500 hover:bg-yellow-100';
    case 'info':
      return 'text-blue-500 hover:bg-blue-100';
    default:
      return 'text-red-500 hover:bg-red-100';
  }
});

const focusClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'focus:ring-yellow-600 focus:ring-offset-yellow-50';
    case 'info':
      return 'focus:ring-blue-600 focus:ring-offset-blue-50';
    default:
      return 'focus:ring-red-600 focus:ring-offset-red-50';
  }
});

const handleDismiss = () => {
  show.value = false;
  emit('dismiss');
};
</script>
