import { defineStore } from 'pinia'
import axios from 'axios'

const LARAVEL_API_URL = 'http://localhost:8000/api'

export const useImageStore = defineStore('images', {
  state: () => ({
    images: [],
    categories: ['Resident', 'Forest', 'Industry', 'Farmland', 'Parking', 'River&Lake', 'Grass'],
    loading: false,
    error: null
  }),
  
  actions: {
    async uploadImage(file, category) {
      this.loading = true
      try {
        const formData = new FormData()
        formData.append('image', file)
        formData.append('category', category)
        
        const response = await axios.post(`${LARAVEL_API_URL}/images/upload`, formData)
        this.images.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async searchSimilarImages(queryImage, useRelevanceFeedback = false) {
      this.loading = true
      try {
        const formData = new FormData()
        formData.append('image', queryImage)
        formData.append('use_relevance_feedback', useRelevanceFeedback)

        const response = await axios.post(`${LARAVEL_API_URL}/images/search`, formData)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async submitRelevanceFeedback(relevantIds, irrelevantIds) {
      try {
        const response = await axios.post(`${LARAVEL_API_URL}/images/feedback`, {
          relevant_ids: relevantIds,
          irrelevant_ids: irrelevantIds
        })
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      }
    }
  }
})