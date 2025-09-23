<script lang="ts" setup>
  import { ref, onMounted } from 'vue'
  import { useDataStore } from '@/stores/data'
  import type { Category,CategoryItem } from '@/api/types'
  import { useRoute } from 'vue-router'
  import UploadView from '@/components/UploadView.vue'

  const route = useRoute()
  const categoryID = route.query.categoryID as string

  const isUploadVisible = ref(false)
  const handleUploadClick = () => {
  isUploadVisible.value = true
}
  const categories = ref<Category[] | null>([])   // 初始化空数组
  let cur_index:null |number   = null  // 当前选中索引
  let length   = null // 当前选中索引
  let items = ref<CategoryItem[] | null>([]) 
  let curCategory = ref<Category | null>(null)   // 当前选中分类


  onMounted(
    async () => {
    try {
      const store = useDataStore();
      await store.fetchData();  // 自动缓存，不会重复请求
      categories.value = store.info // 将 API 数据赋值给响应式变量
      console.log("categories.value",categories.value)
      cur_index = store.cur_index
      if (cur_index !== null) {
        curCategory.value = categories.value ? categories.value[cur_index] : null
      }
      console.log(categories.value)
      
      items.value = curCategory.value?.items || []

      console.log(cur_index)
    } catch (err: any) {
      err.value = '加载失败，请重试'
      console.log(err.value)
    
    } finally {
      // loading.value = false
    }
  })

</script>

<template>
  <!-- 默认渲染所有分类 有传入则 只渲染一个 -->
  <el-scrollbar height="1050px" >
   
  
  <div v-if="categoryID">
    <el-tag class="category-tag" type="primary" size="large">{{ curCategory ? curCategory.name : '无' }}</el-tag>

  <div class="example-showcase">
    
    <el-card v-if="curCategory" class="box-card"
      v-for="(item, index) in items"
      :key="item.id" 
      style="margin-right: 10px;" shadow="always">
      <template #header>{{item.name}}</template>
      
      <img
        src="@\assets\blank.jpg"
        style="width: 100%"
      /> 
      


    <!-- 上传弹窗 -->    
     <el-button type="primary" @click="handleUploadClick">
      <UploadView 
      v-if="isUploadVisible"
      :sceneID=item.id
      :sceneName="item.name"
      :visible="isUploadVisible"
      @close="isUploadVisible = true"
        />
     </el-button>
      
    </el-card>
     
  </div>
  </div>
  
  
  <div v-else>
    
    <div v-for="category in categories" :key="category.id" style="margin-bottom: 20px;">
    
      <el-tag class="category-tag" type="primary" size="large"  round>{{ category ? category.name : '无' }}</el-tag>

  <div class="example-showcase">
    
    <el-card v-if="category" class="box-card"
      v-for="(item, index) in category.items"
      :key="index" 
      style="margin-right: 10px;" shadow="always">
      <template #header>{{item.name}}</template>
      
      <img
        src="@\assets\blank.jpg"
        style="width: 100%"
      /> 
      


    <!-- 上传弹窗 -->    
     <el-button type="primary" @click="handleUploadClick">
      <UploadView 
      v-if="isUploadVisible"
      :sceneID=item.id
      :sceneName="item.name"
      :visible="isUploadVisible"
      @close="isUploadVisible = true"
        />
     </el-button>
      
    </el-card>
     
  </div>
    </div>
  </div>
  </el-scrollbar>
  
</template>



<style scoped>
  .category-tag {
    font-size: 18px;   /* 调整字体大小 */
    padding: 12px 20px; /* 调整内边距：上下 12px，左右 20px */
    height: auto;      /* 高度自适应，避免固定高度导致文字垂直不居中 */
    
  }
  .box-card {
    width: 500px;
    max-width: 240px;
    margin: 20px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }
  .example-showcase  {
    cursor: pointer;
    /* color: var(--el-color-primary);*/
    display: flex;
    align-items: center;
     
  }
  
</style>
