<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-md">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between h-16">
          <router-link to="/" class="text-xl font-bold">Image Search System</router-link>
          <div class="flex space-x-4">
            <router-link 
              v-for="link in navLinks" 
              :key="link.path"
              :to="link.path"
              class="px-3 py-2 rounded-md hover:bg-gray-100"
            >
              {{ link.name }}
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <router-view></router-view>
  </div>
</template>

<script setup>
const navLinks = [
  { name: 'Home', path: '/' },
  { name: 'Upload', path: '/upload' },
  { name: 'Search', path: '/search' },
  { name: 'Categories', path: '/categories' }
]
</script>