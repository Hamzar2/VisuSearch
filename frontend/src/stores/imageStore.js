import { defineStore } from 'pinia'
import axios from 'axios'

const LARAVEL_API_URL = 'http://localhost:8000/api'

export const useImageStore = defineStore('images', {
  state: () => ({
    images: [],
    categories: ['Resident', 'Forest', 'Industry', 'Field', 'Parking', 'River&Lake', 'Grass'],
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
        for (const [key, value] of formData.entries()) {
          console.log(key, value); 
        }
        const response = await axios.post(`${LARAVEL_API_URL}/images/search`, formData)
        if (response.data) {
          console.log(response.data);
          return response.data
          
        } else {
          console.log("errooooor");
          throw new Error(response.statusText)
        }
      } catch (error) {
        this.error = error.message
        console.log("test" , error.response); 
        
      } finally {
        this.loading = false
      }
    },

    async submitRelevanceFeedback(relevantIds, irrelevantIds) {
      try {
        console.log("resultssssss : ",relevantIds, irrelevantIds);
        const response = await axios.post(`${LARAVEL_API_URL}/images/feedback`, {
          relevant_ids: relevantIds,
          irrelevant_ids: irrelevantIds
        })
        console.log("resultssssss : ",response.data);
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    async getImages() {
      this.loading = true
      try {
        const response = await axios.get(`${LARAVEL_API_URL}/images/getimages`)
        this.images = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteImage(id) {
      this.loading = true
      try {
        const formData = new FormData()
        formData.append('id',id)
        const response = await axios.post(`${LARAVEL_API_URL}/images/delete`,formData)
        this.images = this.images.filter(image => image.id !== id)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async createTransformedImage( formData) {
      try {
        // Ensure base_image_id is correctly sent as a number
        // formData.base_image_id = parseInt(formData.base_image_id);
        console.log("form data : ",formData);
        const response = await axios.post(`${LARAVEL_API_URL}/images/transform`, formData, {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        });
        this.images.push(response.data); // Add new image to state
        return response.data;  // Return the new image data
      } catch (error) {
        if (error.response && error.response.status === 422) {
            const errors = Object.values(error.response.data.errors).flat().join('\n');
            throw new Error(errors); // Re-throw with formatted validation errors
        } else {
            // Handle other errors
            throw error; // Re-throw if it's not a validation error
        }
      }
    },

    async updateImage(id, file, category) {
      this.loading = true
      try {
        const formData = new FormData()
        formData.append('id', id)
        formData.append('image', file)
        formData.append('category', category)

        const response = await axios.post(`${LARAVEL_API_URL}/images/update`, formData)
        const updatedImage = response.data
        const index = this.images.findIndex(image => image.id === id)
        if (index !== -1) {
          this.images[index] = updatedImage
        }
        return updatedImage
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    }
  },

  mutations: {
    ADD_IMAGE(state, image) {
      state.images.push(image); // or your preferred way to update the images array
    },
  },
})
