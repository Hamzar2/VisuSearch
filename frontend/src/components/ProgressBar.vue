<template>
  <div class="progress-bar" role="progressbar" :aria-valuenow="progress" aria-valuemin="0" aria-valuemax="100">
    <div 
      class="progress-bar-fill"
      :style="{ width: `${progress}%` }"
    ></div>
  </div>
</template>

<script setup>
defineProps({
  progress: {
    type: Number,
    required: true,
    validator: (value) => value >= 0 && value <= 100
  }
})
</script>