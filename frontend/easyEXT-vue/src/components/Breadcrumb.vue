<script setup ts>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
  const route = useRoute()

  // 计算属性，根据当前路由的 matched 生成面包屑列表
  const breadcrumbList = computed(() => {
    return route.matched.filter((item) => item.meta && item.meta.breadcrumb)
  })

  // 判断是否是最后一项
  const isLast = (index) => {
    return index === breadcrumbList.value.length - 1
  }


  

</script>

<template>
  <el-breadcrumb separator="/">
    <!-- 循环生成面包屑项 -->
    <el-breadcrumb-item
      v-for="(route, index) in breadcrumbList"
      :key="index"
    >
      <!-- 最后一项或不可点击项，使用 span -->
      <span v-if="isLast(index) || !route.meta?.breadcrumb">{{ route.meta?.breadcrumb }}</span>
      <!-- 其他项，使用 router-link 跳转 -->
      <router-link v-else :to="route.path || ''">{{ route.meta?.breadcrumb }}</router-link>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>



<style>
</style>