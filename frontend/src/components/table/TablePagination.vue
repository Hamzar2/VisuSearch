<template>
  <div class="flex items-center justify-between mt-4 px-4">
    <div class="text-sm text-gray-700">
      Showing {{ startIndex + 1 }} to {{ Math.min(endIndex, totalItems) }} of {{ totalItems }} entries
    </div>
    <div class="flex space-x-2">
      <button 
        @click="$emit('update:page', currentPage - 1)"
        :disabled="currentPage === 1"
        class="btn-secondary px-3 py-1 text-sm disabled:opacity-50"
      >
        Previous
      </button>
      <button
        @click="$emit('update:page', currentPage + 1)"
        :disabled="endIndex >= totalItems"
        class="btn-secondary px-3 py-1 text-sm disabled:opacity-50"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  currentPage: Number,
  itemsPerPage: Number,
  totalItems: Number
});

const startIndex = computed(() => (props.currentPage - 1) * props.itemsPerPage);
const endIndex = computed(() => startIndex.value + props.itemsPerPage);

defineEmits(['update:page']);
</script>