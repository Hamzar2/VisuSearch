import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ImageUpload from '../views/ImageUpload.vue'
import ImageSearch from '../views/ImageSearch.vue'
import ImageCategories from '../views/ImageCategories.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/upload',
      name: 'upload',
      component: ImageUpload
    },
    {
      path: '/search',
      name: 'search',
      component: ImageSearch
    },
    {
      path: '/categories',
      name: 'categories',
      component: ImageCategories
    }
  ]
})

export default router