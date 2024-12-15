<!-- CreateModal.vue -->
<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
      <h3 class="text-lg font-semibold mb-4">Create New Image</h3>
      <form @submit.prevent="createImage">
        <div v-if="errorMessage" class="text-red-500 mb-4">{{ errorMessage }}</div>
          <label for="baseImage" class="block mb-2">Select Base Image:</label>
          <select 
            id="baseImage" 
            v-model.number="form.base_image_id" 
            class="w-full mb-4 p-2 border rounded" 
            required
          >
            <option v-for="image in images" :key="image.id" :value="image.id">
              Image ID: {{ image.id }}
            </option>
          </select>

          <!-- Transformation Selection -->
          <label for="transformation" class="block mb-2">Transformation:</label>
          <select 
            id="transformation" 
            v-model="form.transformation" 
            class="w-full mb-4 p-2 border rounded" 
            required
          >
            <option value="crop">Crop</option>
            <option value="resize">Resize</option>
            <option value="rotate">Rotate</option>
          </select>

          <!-- Transformation Parameters (Conditional) -->
          <div v-if="form.transformation === 'crop'" class="mb-4">
            <label for="x" class="block mb-1">X:</label>
            <input type="number" id="x" v-model.number="form.x" class="w-full p-2 border rounded mb-2" required>

            <label for="y" class="block mb-1">Y:</label>
            <input type="number" id="y" v-model.number="form.y" class="w-full p-2 border rounded mb-2" required>

            <label for="width" class="block mb-1">Width:</label>
            <input type="number" id="width" v-model.number="form.width" class="w-full p-2 border rounded mb-2" required>

            <label for="height" class="block mb-1">Height:</label>
            <input type="number" id="height" v-model.number="form.height" class="w-full p-2 border rounded" required>
          </div>

          <div v-else-if="form.transformation === 'resize'" class="mb-4">
            <label for="width" class="block mb-1">Width:</label>
            <input type="number" id="width" v-model.number="form.width" class="w-full p-2 border rounded mb-2" required>

            <label for="height" class="block mb-1">Height:</label>
            <input type="number" id="height" v-model.number="form.height" class="w-full p-2 border rounded" required>
          </div>

          <div v-else-if="form.transformation === 'rotate'" class="mb-4">
            <label for="angle" class="block mb-1">Angle:</label>
            <input type="number" id="angle" v-model.number="form.angle" class="w-full p-2 border rounded" required>
          </div>

          <!-- Submit and Cancel Buttons -->
          <div class="flex justify-between mt-4">
            <button 
              type="submit" 
              class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Create
            </button>
            <button 
              type="button" 
              @click="$emit('close')" 
              class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Cancel
            </button>
          </div>
        </form>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, onMounted, watch } from 'vue';
import { useImageStore } from '../stores/imageStore';

const emit = defineEmits(['close', 'create-success']);
const imageStore = useImageStore();
const show = ref(true); // Ensure modal is initially visible
const errorMessage = ref('');
const images = ref([]);
const form = ref({
  base_image_id: null,
  transformation: 'crop',
  x: 0,
  y: 0,
  width: 100,
  height: 100,
  angle: 0,
});

const fetchImages = async () => {
  try {
    images.value = await imageStore.getImages();
    // Set base_image_id if there are images available
    if (images.value.length > 0) {
      form.value.base_image_id = images.value[0].id;
    }
  } catch (error) {
    console.error('Error fetching images:', error);
    errorMessage.value = 'Failed to load images.';
  }
};


const createImage = async () => {
  try {
    console.log("here : ",form.value)
    await imageStore.createTransformedImage(form.value);
    emit('create-success');
    emit('close'); 
    errorMessage.value = ''; // Clear any previous error messages
  } catch (error) {
    console.error('Error creating image:', error);
    errorMessage.value = error.message; // Display the specific error from the backend
  }
};

onMounted(fetchImages);


// Watch for changes in the 'show' prop and update the local 'show' ref.
// This ensures the modal opens and closes correctly.
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  initialFormData: {    // Receive form data as prop
    type: Object,
    default: () => ({}) // Default empty object
  }
});


// const form = ref({...props.initialFormData}); 
watch(() => props.show, (newValue) => {
    show.value = newValue;
    if (newValue && images.value.length === 0) {
      fetchImages(); // Fetch images if the modal is opened and images haven't been loaded yet.
    }
  });
  
</script>