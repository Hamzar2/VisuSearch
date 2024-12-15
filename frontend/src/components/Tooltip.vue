<template>
  <div class="relative has-tooltip inline-block">
    <slot></slot>
    <div 
      class="tooltip"
      role="tooltip"
      :class="position"
    >
      {{ text }}
      <div class="tooltip-arrow"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  text: {
    type: String,
    required: true
  },
  position: {
    type: String,
    default: 'top',
    validator: (value) => ['top', 'bottom', 'left', 'right'].includes(value)
  }
})
</script>

<style scoped>
.tooltip {
  @apply absolute z-50 px-2 py-1 text-sm text-white bg-gray-900 rounded-lg;
}
.tooltip[class*="top"] { @apply bottom-full left-1/2 transform -translate-x-1/2 mb-2; }
.tooltip[class*="bottom"] { @apply top-full left-1/2 transform -translate-x-1/2 mt-2; }
.tooltip[class*="left"] { @apply right-full top-1/2 transform -translate-y-1/2 mr-2; }
.tooltip[class*="right"] { @apply left-full top-1/2 transform -translate-y-1/2 ml-2; }
</style>