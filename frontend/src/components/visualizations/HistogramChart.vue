<template>
  <div class="chart-container">
    <h4 class="text-lg font-semibold">{{ title }}</h4>
    <img :src="data" alt="Histogram Chart" class="rounded-lg shadow-md max-w-full h-auto" />
  </div>
</template>

<script>
export default {
  props: {
    data: {
      type: String,
      required: true, // Expect base64-encoded image string
    },
    title: {
      type: String,
      required: true,
    },
  },
};
</script>

<style scoped>
.chart-container {
  @apply bg-white p-4 rounded-lg shadow-md;
}
</style>
