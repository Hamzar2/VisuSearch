<template>
  <div 
    class="flex items-center justify-center space-x-2"
    role="status"
    aria-label="Loading"
  >
    <div class="w-3 h-3 bg-primary rounded-full animate-bounce" style="animation-delay: -0.3s"></div>
    <div class="w-3 h-3 bg-primary rounded-full animate-bounce" style="animation-delay: -0.15s"></div>
    <div class="w-3 h-3 bg-primary rounded-full animate-bounce"></div>
    <span class="sr-only">Loading...</span>
  </div>
</template>