<template>
  <router-link 
    v-if="link"
    :to="link"
    class="block bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
  >
    <div class="flex items-center mb-4">
      <span class="text-3xl mr-3">{{ icon }}</span>
      <h2 class="text-xl font-semibold">{{ title }}</h2>
    </div>
    <p class="text-gray-600">{{ description }}</p>
  </router-link>

  <div 
    v-else
    @click="$emit('click')"
    class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
  >
    <div class="flex items-center mb-4">
      <span class="text-3xl mr-3">{{ icon }}</span>
      <h2 class="text-xl font-semibold">{{ title }}</h2>
    </div>
    <p class="text-gray-600">{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  link: {
    type: String,
    default: ''
  }
})
</script>