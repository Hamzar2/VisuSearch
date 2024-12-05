<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Image Search System</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <feature-card
        title="Upload Images"
        description="Upload and categorize your images"
        link="/upload"
        icon="📤"
      />
      <feature-card
        title="Search Images"
        description="Search images by content and similarity"
        link="/search"
        icon="🔍"
      />
      <feature-card
        title="Browse Categories"
        description="View and manage image categories"
        link="/categories"
        icon="📁"
      />
      <feature-card
        title="About"
        description="Learn about our image search technology"
        icon="ℹ️"
        @click="showAboutModal = true"
      />
    </div>

    <about-modal
      v-if="showAboutModal"
      @close="showAboutModal = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FeatureCard from '../components/FeatureCard.vue'
import AboutModal from '../components/AboutModal.vue'

const showAboutModal = ref(false)
</script>