<script lang="ts" setup>
  import { ref, onMounted } from 'vue'
  import { useDataStore } from '@/stores/data'
  import type { Category,CategoryItem } from '@/api/types'
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
  <div class="example-showcase">
    <el-card v-if="curCategory" class="box-card"
      v-for="(item, index) in items"
      :key="index" 
      style="margin-right: 10px;" shadow="always">
      <template #header>{{item.name}}</template>
      
      <img
        src="@\assets\blank.jpg"
        style="width: 100%"
      /> 
      <el-button type="primary" size="small">
        新增任务
      </el-button>
    </el-card>
  </div>
  
</template>



<style scoped>
  .box-card {
    width: 500px;
    max-width: 240px;
    margin: 20px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }
  .example-showcase  {
    cursor: pointer;
    color: var(--el-color-primary);
    display: flex;
    align-items: center;
     
  }
  
</style>
