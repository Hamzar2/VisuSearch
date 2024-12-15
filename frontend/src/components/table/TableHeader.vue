<template>
  <thead class="bg-gray-50">
    <tr>
      <th v-for="header in headers" :key="header.key" class="px-4 py-2 text-left">
        {{ header.label }}
      </th>
    </tr>
  </thead>
</template>

<script setup>
defineProps({
  headers: {
    type: Array,
    required: true
  }
})
</script>