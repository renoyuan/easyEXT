import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// 正确写法
import TaskDetailView from '@/views/TaskDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
      meta: { breadcrumb: '首页' }
    },
    {
      path: '/taskList',
      name: 'taskList',
      component: () => import('../views/TaskListView.vue'),
      meta: { breadcrumb: '首页' }
    },
    {
      path: '/upload',
      name: 'upload',
      component: () => import('../components/UploadView.vue'),
      meta: { breadcrumb: '上传任务' }
    },
    {
      path: '/taskDetail',
      name: 'taskDetail', 
      component: TaskDetailView,
      meta: { breadcrumb: '任务详情'}
    },
    {
      path: '/scenes',
      name: 'scenes',
      // route level code-splitting
      // this generates a separate chunk (SceneView.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/SceneView.vue'),
    },
  ],
})

export default router
