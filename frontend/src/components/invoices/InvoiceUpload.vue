<template>
  <div class="max-w-xl mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6">Cargar Factura</h2>
    
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Seleccione PDF
      </label>
      <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,application/pdf"
          @change="handleFileSelect"
          class="hidden"
        />
        
        <div v-if="!selectedFile" @click="triggerFileInput" class="cursor-pointer">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="mt-2 text-sm text-gray-600">Haga click para seleccionar un archivo PDF</p>
          <p class="text-xs text-gray-500 mt-1">Tamaño máximo: 10MB</p>
        </div>
        
        <div v-else class="space-y-2">
          <svg class="mx-auto h-12 w-12 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
          <p class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
          <button
            @click="clearFile"
            type="button"
            class="text-sm text-red-600 hover:text-red-800"
          >
            Eliminar
          </button>
        </div>
      </div>
      <p v-if="error" class="text-red-500 text-sm mt-2">{{ error }}</p>
    </div>

    <div v-if="uploading" class="mb-4">
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div
          class="bg-blue-600 h-2 rounded-full transition-all duration-300"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
      <p class="text-sm text-gray-600 mt-2 text-center">Subiendo... {{ progress }}%</p>
    </div>

    <div v-if="success" class="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
      {{ success }}
    </div>

    <button
      @click="handleUpload"
      :disabled="!selectedFile || uploading"
      class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
    >
      {{ uploading ? 'Uploading...' : 'Upload Invoice' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useInvoiceStore } from '../../stores/invoices';

const invoiceStore = useInvoiceStore();

const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const uploading = ref(false);
const progress = ref(0);
const error = ref('');
const success = ref('');

const emit = defineEmits<{
  'upload-success': [invoiceId: string];
  'upload-error': [error: string];
}>();

const triggerFileInput = () => {
  fileInput.value?.click();
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

const validateFile = (file: File): boolean => {
  error.value = '';
  
  // Check file type
  if (file.type !== 'application/pdf') {
    error.value = 'Only PDF files are allowed';
    return false;
  }
  
  // Check file size (10MB limit)
  const maxSize = 10 * 1024 * 1024; // 10MB in bytes
  if (file.size > maxSize) {
    error.value = 'File size must not exceed 10MB';
    return false;
  }
  
  return true;
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  
  if (file && validateFile(file)) {
    selectedFile.value = file;
    error.value = '';
    success.value = '';
  } else {
    selectedFile.value = null;
  }
};

const clearFile = () => {
  selectedFile.value = null;
  error.value = '';
  success.value = '';
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

const handleUpload = async () => {
  if (!selectedFile.value) return;
  
  uploading.value = true;
  progress.value = 0;
  error.value = '';
  success.value = '';
  
  // Simulate progress
  const progressInterval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += 10;
    }
  }, 200);
  
  try {
    const response = await invoiceStore.uploadInvoice(selectedFile.value);
    progress.value = 100;
    success.value = 'Invoice uploaded successfully! Processing will begin shortly.';
    emit('upload-success', response.invoiceId);
    
    // Clear form after successful upload
    setTimeout(() => {
      clearFile();
      success.value = '';
    }, 3000);
  } catch (err: any) {
    error.value = err.message || 'Failed to upload invoice. Please try again.';
    emit('upload-error', error.value);
  } finally {
    clearInterval(progressInterval);
    uploading.value = false;
    progress.value = 0;
  }
};
</script>
