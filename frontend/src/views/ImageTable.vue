<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-bold mb-4">Manage Images</h2>

    <div v-if="error" class="mb-4 text-red-500">
      {{ error }}
    </div>

    <div v-if="loading" class="flex justify-center my-4">
      <LoadingSpinner />
    </div>

    <div v-else>
      <div class="overflow-auto max-h-[400px] border border-gray-200 rounded-lg">
        <table class="w-full">
          <TableHeader :headers="tableHeaders" />
          <tbody>
            <tr
              v-for="image in images"
              :key="image.id"
              class="border-t hover:bg-gray-50 transition-colors"
            >
              <td class="px-4 py-2">{{ image.id }}</td>
              <td class="px-4 py-2">{{ image.path }}</td>
              <td class="px-4 py-2">{{ image.category }}</td>
              <td class="px-4 py-2 space-x-2">
                <Tooltip text="Delete image">
                  <button @click="deleteImage(image.id)" class="btn-danger">Delete</button>
                </Tooltip>
                <Tooltip text="Update image">
                  <button @click="showUpdateModal(image)" class="btn-warning">Update</button>
                </Tooltip>
                <Tooltip text="Create new image">
                  <button @click="openCreateModal(image)" class="btn-primary">Create</button>
                </Tooltip>
                <Tooltip text="View analysis">
                  <button @click="fetchHistogram(image.url)" class="btn-secondary">Analysis</button>
                </Tooltip>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showAnalysis" class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-if="realImage" class="col-span-full">
        <h4 class="text-lg font-semibold mb-2">Original Image</h4>
        <img :src="realImage" alt="Original Image" class="rounded-lg shadow-md max-w-full h-auto" />
      </div>

      <HistogramChart
        v-if="histogramPlot"
        :data="histogramPlot"
        title="Color Distribution"
      />

      <HistogramChart
        v-if="dominantColorsPlot"
        :data="dominantColorsPlot"
        title="Dominant Colors"
      />
      
      <HistogramChart
        v-if="gaborFeatures"
        :data="gaborFeatures"
        title="Gabor Features"
      />

      <HistogramChart
        v-if="huMoments"
        :data="huMoments"
        title="Hu Moments"
      />
    </div>

    <CreateModal 
      v-if="showCreateModal" 
      :show="showCreateModal" 
      :initialFormData="form"  
      @close="showCreateModal = false" 
      @create-success="handleCreateSuccess"
    />
    
    <UpdateModal
      v-if="showModal"
      :show="showModal"
      :image="imageToUpdate"
      @close="showModal = false"
      @update-success="handleUpdateSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useImageStore } from '../stores/imageStore';
import TableHeader from '../components/table/TableHeader.vue';
import HistogramChart from '../components/visualizations/HistogramChart.vue';
import UpdateModal from './UpdateModel.vue';
import CreateModal from './CreateModal.vue';
import Tooltip from '../components/Tooltip.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';

const imageStore = useImageStore();
const images = ref([]);
const showModal = ref(false);
const imageToUpdate = ref(null);
const error = ref(null);
const showAnalysis = ref(false);
const loading = ref(false);
const showCreateModal = ref(false);

// Analysis data
const histogramPlot = ref(null);
const dominantColorsPlot = ref(null);
const huMoments = ref(null);
const gaborFeatures = ref(null);
const realImage = ref(null);

const LARAVEL_API_URL = 'http://localhost:8000';

const tableHeaders = [
  { key: 'id', label: 'ID' },
  { key: 'path', label: 'Image Path' },
  { key: 'category', label: 'Category' },
  { key: 'actions', label: 'Actions' }
];


const fetchImages = async () => {
  loading.value = true;
  try {
    const data = await imageStore.getImages();
    images.value = data;
  } catch (err) {
    error.value = 'Failed to fetch images: ' + err.message;
  } finally {
    loading.value = false;
  }
};

const deleteImage = async (id) => {
  try {
    await imageStore.deleteImage(id);
    await fetchImages();
  } catch (err) {
    error.value = 'Failed to delete image: ' + err.message;
  }
};

const showUpdateModal = (image) => {
  imageToUpdate.value = image;
  showModal.value = true;
};

const handleUpdateSuccess = async () => {
  showModal.value = false;
  await fetchImages();
};

const fetchHistogram = async (imageUrl) => {
  loading.value = true;
  showAnalysis.value = true;

  try {
    const response = await fetch('http://localhost:5000/api/generate-plots', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_url: imageUrl }),
    });

    if (!response.ok) throw new Error('Failed to fetch analysis data');

    const data = await response.json();

    // Directly assign base64 strings for image display
    histogramPlot.value = `data:image/png;base64,${data.color_histogram_plot}`;
    dominantColorsPlot.value = `data:image/png;base64,${data.dominant_colors_plot}`;
    gaborFeatures.value = `data:image/png;base64,${data.gabor_features_plot}`;
    huMoments.value = `data:image/png;base64,${data.hu_moments_plot}`;
    realImage.value = `${LARAVEL_API_URL}${imageUrl}`;
  } catch (err) {
    error.value = 'Failed to fetch analysis: ' + err.message;
    showAnalysis.value = false;
  } finally {
    loading.value = false;
  }
};

const openCreateModal = (image) => {
  showCreateModal.value = true;
  form.value.base_image_id = image.id; // Pre-fill the base image ID
};
const handleCreateSuccess = async () => {
  showCreateModal.value = false;
  await fetchImages();
};

onMounted(fetchImages);
</script>

<style scoped>
.visualization-card {
  @apply bg-white p-4 rounded-lg shadow-md;
}
</style>
