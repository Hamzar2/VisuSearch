<template>
  <div class="bg-white p-4 rounded-lg shadow-md">
    <h3 class="text-lg font-semibold mb-4">Image Features</h3>
    
    <div class="space-y-4">
      <!-- Color Histogram -->
      <div>
        <h4 class="font-medium mb-2">Color Histogram</h4>
        <canvas ref="histogramCanvas" width="300" height="150"></canvas>
      </div>

      <!-- Dominant Colors -->
      <div>
        <h4 class="font-medium mb-2">Dominant Colors</h4>
        <div class="flex space-x-2">
          <div
            v-for="(color, index) in dominantColors"
            :key="index"
            class="w-10 h-10 rounded"
            :style="{ backgroundColor: `rgb(${color.join(',')})` }"
          ></div>
        </div>
      </div>

      <!-- Gabor Features -->
      <div>
        <h4 class="font-medium mb-2">Gabor Features</h4>
        <div class="grid grid-cols-2 gap-2">
          <div v-for="(value, index) in gaborFeatures" :key="index" class="text-sm">
            Feature {{ index + 1 }}: {{ value.toFixed(3) }}
          </div>
        </div>
      </div>

      <!-- Hu Moments -->
      <div>
        <h4 class="font-medium mb-2">Hu Moments</h4>
        <div class="grid grid-cols-2 gap-2">
          <div v-for="(moment, index) in huMoments" :key="index" class="text-sm">
            Moment {{ index + 1 }}: {{ moment.toExponential(3) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  features: {
    type: Object,
    required: true
  }
})

const histogramCanvas = ref(null)
let histogramChart = null

const dominantColors = computed(() => props.features.dominant_colors)
const gaborFeatures = computed(() => props.features.gabor_features)
const huMoments = computed(() => props.features.hu_moments)

const drawHistogram = () => {
  if (histogramChart) {
    histogramChart.destroy()
  }

  const ctx = histogramCanvas.value.getContext('2d')
  histogramChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Array.from({ length: props.features.color_histogram.length }, (_, i) => i),
      datasets: [{
        label: 'Color Distribution',
        data: props.features.color_histogram,
        backgroundColor: 'rgba(75, 192, 192, 0.6)'
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  })
}

watch(() => props.features, drawHistogram, { deep: true })

onMounted(() => {
  drawHistogram()
})
</script>