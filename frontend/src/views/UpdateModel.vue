<script setup lang="ts">
import { ref } from 'vue'
import { useImageStore } from '../stores/imageStore'

const props = defineProps({
  show: Boolean,
  image: Object
})

const emit = defineEmits(['close', 'update-success'])

const imageStore = useImageStore()
const selectedFiles = ref<File[]>([])
const selectedCategory = ref(props.image?.category || '')
const loading = ref(false)
const error = ref<string | null>(null)

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    selectedFiles.value = Array.from(target.files)
  }
}

const updateImage = async () => {
  if (!props.image) return
  loading.value = true
  error.value = null

  try {
    await imageStore.updateImage(props.image.id, selectedFiles.value[0], selectedCategory.value)
    emit('update-success')
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
      <h2 class="text-xl font-bold mb-4">Update Image</h2>
      
      <div class="mb-4">
        <label class="block text-gray-700 text-sm font-bold mb-2">
          Select Category
        </label>
        <select 
          v-model="selectedCategory"
          class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option v-for="category in imageStore.categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>

      <div class="mb-4">
        <label class="block text-gray-700 text-sm font-bold mb-2">
          Upload New Image
        </label>
        <input 
          type="file"
          @change="handleFileSelect"
          accept="image/*"
          class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
      </div>

      <div class="flex justify-end space-x-2">
        <button 
          @click="updateImage"
          :disabled="!selectedFiles.length || !selectedCategory"
          class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
        >
          Update
        </button>
        <button 
          @click="$emit('close')"
          class="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
        >
          Cancel
        </button>
      </div>

      <div v-if="error" class="mt-4 text-red-500">
        {{ error }}
      </div>
    </div>
  </div>
</template>