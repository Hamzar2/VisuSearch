<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg max-w-2xl w-full p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-2xl font-bold">About Image Search System</h2>
        <button 
          @click="$emit('close')"
          class="text-gray-500 hover:text-gray-700"
        >
          ×
        </button>
      </div>
      
      <div class="prose">
        <h3>Features</h3>
        <ul>
          <li>Content-based image search using advanced descriptors</li>
          <li>Bayesian relevance feedback for improved search results</li>
          <li>Support for multiple image categories</li>
          <li>Image feature extraction using:
            <ul>
              <li>Color histograms</li>
              <li>Dominant colors</li>
              <li>Gabor filter textures</li>
              <li>Hu moments for shape analysis</li>
            </ul>
          </li>
        </ul>
      </div>

      <div class="mt-6 flex justify-end">
        <button 
          @click="$emit('close')"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>