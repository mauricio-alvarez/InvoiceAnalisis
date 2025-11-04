<template>
  <div class="flex items-center justify-center" :class="containerClass">
    <div
      class="animate-spin rounded-full border-b-2"
      :class="[sizeClass, colorClass]"
    ></div>
    <p v-if="message" class="ml-3 text-gray-600" :class="textSizeClass">
      {{ message }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'gray' | 'green';
  message?: string;
  fullScreen?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'blue',
  message: '',
  fullScreen: false,
});

const containerClass = computed(() => {
  return props.fullScreen ? 'min-h-screen' : 'py-8';
});

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'h-4 w-4';
    case 'lg':
      return 'h-12 w-12';
    default:
      return 'h-8 w-8';
  }
});

const colorClass = computed(() => {
  switch (props.color) {
    case 'gray':
      return 'border-gray-600';
    case 'green':
      return 'border-green-600';
    default:
      return 'border-blue-600';
  }
});

const textSizeClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'text-sm';
    case 'lg':
      return 'text-lg';
    default:
      return 'text-base';
  }
});
</script>
