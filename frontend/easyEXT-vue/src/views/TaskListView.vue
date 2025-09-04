<script setup lang="ts">
import {fetchTasks} from '@/api/api'
import { ref, onMounted } from 'vue'
import router from '@/router'
import type { Task } from '@/api/types'

const tableData = ref<Task[]>([])
const taskStatusMap: Record<number, string>  = {
    0: '待处理',
    1: '进行中',
    2: '已完成',
    3: '已取消',
    4: '失败',
    5: '超时',
    6: '已删除'
};


const handleDetail = (row: Task) => {
  // console.log('查看任务详情:', row);
  // 在这里可以添加更多逻辑，比如打开一个对话框显示详细信息 跳转干到详情页
  console.log('任务ID:', row.id)
  
  router.push({
    path: '/taskDetail',
    query: {
      taskId: row.id
    }
  })
  
};
onMounted(
    async () => {
    try {
      const response = await fetchTasks()
      console.log('获取任务列表成功',response)
      tableData.value = response
    } catch (error) {
      console.error(error)
      tableData.value = []
    
    
    } finally {
      // loading.value = false
    }
  })
</script>

<template>
  <el-table :data="tableData" border style="width: 100%">
    <el-table-column type="index" label="序号"/>
   
    <el-table-column prop="sceneName" label="场景" />
    <el-table-column prop="taskStatus" label="任务状态"  :formatter="(row: Task) => taskStatusMap[row.taskStatus] || '未知' " />
    <el-table-column prop="createdTime" label="创建时间" width="180"/>
    <el-table-column prop="updateTime" label="更新时间" width="180" />
   <el-table-column label="任务详情" width="180">
      <template #default="scope">
        <!-- 点击按钮触发方法 -->
        <el-button 
          type="text" 
          size="mini" 
          @click="handleDetail(scope.row)"
        >
          查看详情
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>



<style scoped>
  .el-table th, .el-table td {
    text-align: center;
  }
</style>