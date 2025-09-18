import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { useDataStore } from '@/stores/data'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 等待数据加载完成
const store = useDataStore();
await store.fetchData();
console.log("main store.info", store.info)

app.mount('#app')