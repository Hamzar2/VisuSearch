<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Image Search</h1>

    <div class="bg-white p-6 rounded-lg shadow-md mb-6">
      <div class="mb-4">
        <label class="block text-gray-700 text-sm font-bold mb-2">
          Upload Query Image
        </label>
        <input 
          type="file"
          @change="handleQueryImage"
          accept="image/*"
          class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
      </div>

      <div v-if="queryImageUrl" class="mb-4">
        <img :src="queryImageUrl" alt="Uploaded Image" class="max-w-full h-auto rounded-lg shadow-md"/>
      </div>

      <div class="mb-4">
        <label class="flex items-center">
          <input 
            type="checkbox"
            v-model="useRelevanceFeedback"
            class="mr-2"
          >
          Use Relevance Feedback
        </label>
      </div>

      <button 
        @click="searchImages"
        :disabled="!queryImage"
        class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        Search
      </button>
    </div>

    <div v-if="loading" class="text-center">
      <p>Searching...</p>
    </div>

    <div v-if="searchResults.length" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <image-card
        v-for="(result, index) in searchResults"
        :key="index"
        :image="result"
        :show-similarity="true"
      >
        <template #actions>
          <div v-if="useRelevanceFeedback" class="flex gap-2">
            <button 
              @click="markRelevance(index, true)"
              class="px-2 py-1 bg-green-500 text-white rounded"
            >
              Relevant
            </button>
            <button 
              @click="markRelevance(index, false)"
              class="px-2 py-1 bg-red-500 text-white rounded"
            >
              Not Relevant
            </button>
          </div>
        </template>
      </image-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useImageStore } from '../stores/imageStore'
import ImageCard from '../components/ImageCard.vue'

const imageStore = useImageStore()
const queryImage = ref(null)
const queryImageUrl = ref(null)
const useRelevanceFeedback = ref(false)
const loading = ref(false)
const searchResults = ref([])
const relevantIds = ref([])
const irrelevantIds = ref([])

const handleQueryImage = (event) => {
  const file = event.target.files[0]
  queryImage.value = file

  // Create a URL for the uploaded image
  queryImageUrl.value = URL.createObjectURL(file)

  // Reset relevance feedback data
  relevantIds.value = []
  irrelevantIds.value = []
  searchResults.value = [] // Clear previous search results
  console.log('Relevance feedback reset for new query image.')
}


const searchImages = async () => {
  if (!queryImage.value) return
  
  loading.value = true
  try {
    const results = await imageStore.searchSimilarImages(
      queryImage.value,
      useRelevanceFeedback.value
    )
    searchResults.value = results
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const markRelevance = async (index, isRelevant) => {
  const imageId = searchResults.value[index]?.id
  if (!imageId) return

  if (isRelevant) {
    relevantIds.value.push(imageId)
    console.log(relevantIds.value);
  } else {
    irrelevantIds.value.push(imageId)
    console.log(irrelevantIds.value);
  }

  try {
    // Send the feedback to the backend
    await imageStore.submitRelevanceFeedback(relevantIds.value, irrelevantIds.value)
    
    // Re-search with updated results
    await searchImages()
  } catch (error) {
    console.error('Error marking relevance:', error)
  }
}
</script>
