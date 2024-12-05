<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Image Categories</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="category in categories" 
        :key="category"
        class="bg-white p-6 rounded-lg shadow-md"
      >
        <h2 class="text-xl font-semibold mb-4">{{ category }}</h2>
        <div class="grid grid-cols-2 gap-2">
          <image-card
            v-for="(image, index) in getImagesForCategory(category)"
            :key="index"
            :image="image"
          >
            <template #actions>
              <button 
                @click="deleteImage(image.id)"
                class="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full hover:bg-red-600"
              >
                ×
              </button>
            </template>
          </image-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useImageStore } from '../stores/imageStore'
import ImageCard from '../components/ImageCard.vue'

const imageStore = useImageStore()
const categories = computed(() => imageStore.categories)

const getImagesForCategory = (category) => {
  return imageStore.images.filter(img => img.category === category)
}

const deleteImage = async (imageId) => {
  // Implementation would depend on your backend API
}
</script>