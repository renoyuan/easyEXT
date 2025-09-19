
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import { fetchCategories } from '@/api/api'
import type { Category,CategoryItem } from '@/api/types'
import { ArrowRight } from '@element-plus/icons-vue'
import Breadcrumb from '@/components/Breadcrumb.vue'

import UploadView from '@/components/UploadView.vue'

const isUploadVisible = ref(false)
const handleUploadClick = () => {}
isUploadVisible.value = true

interface MenuItem {
  id: string
  name: string
}

const categories_ = ref<Category[]>([])

const handleAction = (category: Category, item: MenuItem) => {
  console.log(`操作：${category.name} - ${item.name}`)
}

const categories = ref<Category[] | null>([])   // 初始化空数组
let cur_index:null |number   = null  // 当前选中索引
let length   = null // 当前选中索引
let items = ref<CategoryItem[] | null>([])


onMounted(async () => {
  try {
    
    const store = useDataStore();
    await store.fetchData();  // 自动缓存，不会重复请求
    categories.value = store.info // 将 API 数据赋值给响应式变量
    console.log("fetchData categories.value",categories.value)
  } catch (err: any) {
    err.value = '加载失败，请重试'
    console.log(err.value)
    categories.value = categories_.value
  } finally {
    // loading.value = false
  }
})




</script>




<template>
  <div class="app">
    <el-container>
    <el-aside>
    <!-- 左侧垂直布局容器 -->
    <div class="vertical-menu">
      
      <router-link class="menu-title" :to="{ path: '/' }"> 场景列表 </router-link>
      <!-- 遍历生成多个下拉菜单 -->
      <el-dropdown
        v-for="category in categories"
        :key="category.id"
        placement="right-start"
        
      >
        <!-- 菜单标题 -->
        <span class="menu-title">
          <router-link  :to="{ path: '/', query: { categoryId:category.id } }"> {{ category.name }} </router-link >
          
          <el-icon> </el-icon>
        </span>

        <!-- 下拉菜单内容 -->
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-for="item in category.items"
              :key="item.id"
              @click="handleAction(category, item)"
            >
              <!-- 上传弹窗 -->    
            <el-button type="primary" @click="handleUploadClick">
              <UploadView 
              v-if="isUploadVisible"
              :sceneName="item.name"
              :sceneID="item.id"
              :visible="isUploadVisible"
              @close="isUploadVisible = true"
                />
            </el-button>
              <router-link  class="menu-title" :to="{ path: '/', query: { scene_id: 1, status: 1, page: 1, page_size: 10 } }"> {{ item.name }} </router-link >
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      <router-link  class="menu-title" :to="{ path: '/taskList', query: { scene_id: 1, status: 1, page: 1, page_size: 10 } }"> 任务列表 </router-link >
    </div>
    </el-aside>
    <el-main>
    <el-header>  
     <!-- 面包屑导航 -->
      <!-- <Breadcrumb /> -->
    <Breadcrumb />
    <!-- <el-breadcrumb class="arrow-right-class" :separator-icon="ArrowRight">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/about' }">promotion detail</el-breadcrumb-item>
    </el-breadcrumb> -->
    </el-header>
    <el-main>
    <!-- 内容区域 -->
    <div class="content">
      <router-view v-slot="{ Component }">
        <component :is="Component || 'HomeView'" />
      </router-view >
    </div>
  </el-main>
  </el-main>
  </el-container>
  </div>
</template>


<style scoped>

/* 左侧垂直菜单容器 */
.vertical-menu {
  position: fixed; /* 固定定位 */
  top: 0; /* 贴紧顶部 */
  left: 0; /* 贴紧左侧 */
  width: 150px;
  height: 100vh; /* 高度占满整个视口 */
  background: #f9fafc;
  border-right: 1px solid #e6e6e6;
  z-index: 1000; /* 确保菜单在其他内容上方 */
}
 /* 面包屑导航 */
.arrow-right-class {
  position: fixed; /* 固定定位 */
  top: 10px;  
  left: 180px; /* 留出左侧菜单的宽度 */

  vertical-align: middle;
}

/* 内容区域 */
.content {
  position: fixed;
  width: calc(100% - 180px- 35px); /* 留出左侧菜单的宽度 */
  right: 35px; /* 右侧留白宽度 */
  left: 180px;
  top: 50px; /* 留出面包屑导航的高度 */
  margin-left: 0px; /* 留出左侧菜单的宽度 */
  background: #e7e8ea;

}

/* 菜单标题样式 */
.menu-title {
  display: block;
  padding: 15px 20px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  &:hover {
    background: #ecf5ff;
  }
}

/* 下拉菜单宽度控制 */
.el-dropdown-menu {
  min-width: 80px !important;
}
</style>
