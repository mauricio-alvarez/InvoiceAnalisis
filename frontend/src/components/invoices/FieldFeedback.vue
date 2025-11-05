<template>
  <div class="flex items-center gap-12">
    <div class="flex items-center gap-2">
      <span class="text-sm font-medium text-gray-500">{{ fieldLabel }}:</span>
      <span class="text-sm text-gray-900">{{ displayValue }}</span>
    </div>

    <div class="flex items-center gap-1">
      <button
        @click="handleUpvote"
        :disabled="isLoading"
        class="p-1 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        :class="upvoteClass"
        :title="currentFeedback === 'upvote' ? 'Remove upvote' : 'Mark as correct'"
      >
        <svg
          class="w-5 h-5"
          fill="currentColor"
          viewBox="0 0 20 20"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z"
          />
        </svg>
      </button>
      
      <button
        @click="handleDownvote"
        :disabled="isLoading"
        class="p-1 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        :class="downvoteClass"
        :title="currentFeedback === 'downvote' ? 'Remove downvote' : 'Mark as incorrect'"
      >
        <svg
          class="w-5 h-5"
          fill="currentColor"
          viewBox="0 0 20 20"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.43a2 2 0 00-1.105-1.79l-.05-.025A4 4 0 0011.055 2H5.64a2 2 0 00-1.962 1.608l-1.2 6A2 2 0 004.44 12H8v4a2 2 0 002 2 1 1 0 001-1v-.667a4 4 0 01.8-2.4l1.4-1.866a4 4 0 00.8-2.4z"
          />
        </svg>
      </button>
    </div>
  </div>
  
  <!-- Error Toast -->
  <Transition
    enter-active-class="transform ease-out duration-300 transition"
    enter-from-class="translate-y-2 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition ease-in duration-100"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="showError"
      class="fixed top-4 right-4 max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden z-50"
    >
      <div class="p-4">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg
              class="h-6 w-6 text-red-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div class="ml-3 w-0 flex-1 pt-0.5">
            <p class="text-sm font-medium text-gray-900">Feedback Error</p>
            <p class="mt-1 text-sm text-gray-500">{{ errorMessage }}</p>
          </div>
          <div class="ml-4 flex-shrink-0 flex">
            <button
              @click="closeError"
              class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <span class="sr-only">Close</span>
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
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  fieldName: string;
  fieldValue: any;
  currentFeedback?: 'upvote' | 'downvote' | null;
  invoiceId: string;
}

const props = withDefaults(defineProps<Props>(), {
  currentFeedback: null,
});

const emit = defineEmits<{
  feedback: [{ fieldName: string; vote: 'upvote' | 'downvote' | 'remove' }];
}>();

const isLoading = ref(false);
const showError = ref(false);
const errorMessage = ref('');
let errorTimeoutId: number | null = null;

// Field label mapping
const fieldLabels: Record<string, string> = {
  invoiceNumber: 'Invoice Number',
  invoiceDate: 'Invoice Date',
  dueDate: 'Due Date',
  totalAmount: 'Total Amount',
  taxAmount: 'Tax Amount',
  subtotal: 'Subtotal',
  vendorName: 'Vendor Name',
  supplierName: 'Supplier Name',
  supplierRuc: 'RUC',
  currency: 'Currency',
};

const fieldLabel = computed(() => {
  return fieldLabels[props.fieldName] || props.fieldName;
});

const displayValue = computed(() => {
  if (props.fieldValue === null || props.fieldValue === undefined) {
    return 'N/A';
  }
  
  // Format amounts
  if (props.fieldName.includes('Amount') || props.fieldName === 'subtotal') {
    return typeof props.fieldValue === 'number' 
      ? props.fieldValue.toFixed(2) 
      : props.fieldValue;
  }
  
  return props.fieldValue;
});

const upvoteClass = computed(() => {
  if (props.currentFeedback === 'upvote') {
    return 'text-green-600 bg-green-50 hover:bg-green-100';
  }
  return 'text-gray-400 hover:text-green-600 hover:bg-green-50';
});

const downvoteClass = computed(() => {
  if (props.currentFeedback === 'downvote') {
    return 'text-red-600 bg-red-50 hover:bg-red-100';
  }
  return 'text-gray-400 hover:text-red-600 hover:bg-red-50';
});

const handleUpvote = () => {
  if (isLoading.value) return;
  
  try {
    // If already upvoted, remove the vote
    const vote = props.currentFeedback === 'upvote' ? 'remove' : 'upvote';
    emit('feedback', { fieldName: props.fieldName, vote });
  } catch (error: any) {
    console.error('Error in handleUpvote:', error);
    showErrorToast(error.message || 'Failed to submit feedback');
  }
};

const handleDownvote = () => {
  if (isLoading.value) return;
  
  try {
    // If already downvoted, remove the vote
    const vote = props.currentFeedback === 'downvote' ? 'remove' : 'downvote';
    emit('feedback', { fieldName: props.fieldName, vote });
  } catch (error: any) {
    console.error('Error in handleDownvote:', error);
    showErrorToast(error.message || 'Failed to submit feedback');
  }
};

const showErrorToast = (message: string) => {
  errorMessage.value = message;
  showError.value = true;
  
  if (errorTimeoutId) {
    clearTimeout(errorTimeoutId);
  }
  
  errorTimeoutId = window.setTimeout(() => {
    showError.value = false;
  }, 5000);
};

const closeError = () => {
  showError.value = false;
  if (errorTimeoutId) {
    clearTimeout(errorTimeoutId);
  }
};
</script>
