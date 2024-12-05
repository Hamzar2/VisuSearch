<template>
  <div class="relative">
    <img 
      :src="image.url" 
      :alt="image.category"
      class="w-full h-48 object-cover rounded-lg"
    >
    <div class="mt-2">
      <p v-if="showSimilarity" class="text-sm">
        Similarity: {{ image.similarity.toFixed(2) }}
      </p>
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  image: {
    type: Object,
    required: true
  },
  showSimilarity: {
    type: Boolean,
    default: false
  }
})
</script>