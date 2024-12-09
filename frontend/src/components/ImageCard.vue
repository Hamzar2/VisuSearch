<template>
  <div class="image-card">
    <div class="image-container">
      <img 
        :src="'http://localhost:8000' + image?.url" 
        :alt="image?.category || 'Image'" 
        class="image"
      >
    </div>
    <div class="image-info">
      <p v-if="showSimilarity" class="similarity">
        Similarity: {{ typeof image?.similarity === 'number' ? image.similarity.toFixed(2) : 'N/A' }}
      </p>
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  image: {
    type: Object,
    required: true,
    default: () => ({
      url: '',
      category: '',
      similarity: null // Default value for similarity
    })
  },
  showSimilarity: {
    type: Boolean,
    default: false
  }
});
</script>

<style>
.image-card {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.image-container {
  width: 40%;
  margin-right: 20px;
  display: flex;
  justify-content: flex-start;
}

.image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 10px;
}

.image-info {
  width: 60%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.similarity {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}
</style>