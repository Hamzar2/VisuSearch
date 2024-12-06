<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Upload Images</h1>
    
    <div class="bg-white p-6 rounded-lg shadow-md">
      <div class="mb-4">
        <label class="block text-gray-700 text-sm font-bold mb-2">
          Select Category
        </label>
        <select 
          v-model="selectedCategory"
          class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>

      <div class="mb-4">
        <label class="block text-gray-700 text-sm font-bold mb-2">
          Upload Image(s)
        </label>
        <input 
          type="file"
          @change="handleFileSelect"
          multiple
          accept="image/*"
          class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
      </div>

      <button 
        @click="uploadImages"
        :disabled="!selectedFiles.length || !selectedCategory"
        class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        Upload
      </button>
    </div>

    <div v-if="loading" class="mt-4 text-center">
      <p>Uploading images...</p>
    </div>

    <div v-if="error" class="mt-4 text-red-500">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useImageStore } from '../stores/imageStore'

const imageStore = useImageStore()
const selectedFiles = ref([])
const selectedCategory = ref('')
const categories = imageStore.categories
const loading = ref(false)
const error = ref(null)

const handleFileSelect = (event) => {
  selectedFiles.value = Array.from(event.target.files)
}

const uploadImages = async () => {
  loading.value = true
  error.value = null
  
  try {
    for (const file of selectedFiles.value) {
      await imageStore.uploadImage(file, selectedCategory.value)
    }
    selectedFiles.value = []
    selectedCategory.value = ''
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>