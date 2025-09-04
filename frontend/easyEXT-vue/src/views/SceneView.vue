<template>
  <div class="scene-container">
    <!-- 左侧类别导航 -->
    <div class="category-panel">
      <div 
        v-for="category in sceneData" 
        :key="category.id"
        @click="selectCategory(category.id)"
        :class="{ 'active': activeCategoryId === category.id }"
        class="category-item"
      >
        {{ category.name }}
      </div>
    </div>

    <!-- 右侧场景内容 -->
    <div class="scene-content">
      <template v-if="currentScenes.length">
        <div v-for="scene in currentScenes" :key="scene.id" class="scene-card">
          <h3>{{ scene.name }}</h3>
          <p>{{ scene.description }}</p>
          <div class="scene-meta">
            <span>创建时间: {{ formatDate(scene.createdAt) }}</span>
          </div>
        </div>
      </template>
      <div v-else-if="loading" class="loading-tip">
        加载中...
      </div>
      <div v-else class="empty-tip">
        {{ errorMessage || '请选择场景类别查看详情' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getScenes } from '../api/http'
import type { Scene, SceneCategory } from '../api/http'

// 响应式数据
const sceneData = ref<SceneCategory[]>([])
const activeCategoryId = ref<string>('')
const currentScenes = ref<Scene[]>([])
const loading = ref<boolean>(false)
const errorMessage = ref<string>('')

// 从后端获取场景数据
const fetchSceneData = async () => {
  try {
    loading.value = true
    errorMessage.value = ''
    // 使用API获取实际数据
    const data = await getScenes<SceneCategory[]>()
    sceneData.value = data
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '获取场景数据失败'
    console.error('Failed to fetch scene data:', error)
    // 在API调用失败时使用模拟数据
    sceneData.value = [
      {
        id: 'c1',
        name: '自然风光',
        scenes: [
          { id: 's1', name: '山脉景观', description: '壮丽的山脉与日出美景', createdAt: '2025-01-15T00:00:00Z' },
          { id: 's2', name: '海岸风光', description: '阳光沙滩与海浪的完美结合', createdAt: '2025-02-20T00:00:00Z' }
        ]
      },
      {
        id: 'c2',
        name: '城市建筑',
        scenes: [
          { id: 's3', name: '现代摩天楼', description: '城市天际线与现代建筑美学', createdAt: '2025-03-10T00:00:00Z' },
          { id: 's4', name: '历史遗迹', description: '百年历史建筑的文化传承', createdAt: '2025-04-05T00:00:00Z' }
        ]
      },
      {
        id: 'c3',
        name: '室内设计',
        scenes: [
          { id: 's5', name: '家居空间', description: '现代简约风格的家居设计', createdAt: '2025-05-18T00:00:00Z' }
        ]
      }
    ]
  } finally {
    loading.value = false
  }
}

// 类别选择处理
const selectCategory = (categoryId: string) => {
  activeCategoryId.value = categoryId
  const category = sceneData.value.find(c => c.id === categoryId)
  currentScenes.value = category ? [...category.scenes] : []
}

// 日期格式化工具
const formatDate = (dateString?: string) => {
  if (!dateString) return '未知时间'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch {
    return dateString
  }
}

// 生命周期钩子
onMounted(async () => {
  await fetchSceneData()
  // 默认选中第一个类别
  if (sceneData.value.length) {
    selectCategory(sceneData.value[0].id)
  }
})
</script>

<style scoped>
.scene-container {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
}

.category-panel {
  width: 240px;
  padding: 20px 0;
  background-color: #fff;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.category-item {
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 15px;
  color: #606266;
}

.category-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.category-item.active {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: 600;
  border-right: 3px solid #409eff;
}

.scene-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.scene-card {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 16px;
  transition: transform 0.3s;
}

.scene-card:hover {
  transform: translateY(-3px);
}

.scene-card h3 {
  margin-top: 0;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 12px;
}

.scene-card p {
  color: #606266;
  line-height: 1.6;
}

.scene-meta {
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
}

.empty-tip,
.loading-tip {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  color: #909399;
  font-size: 16px;
}

.loading-tip {
  color: #409eff;
}
</style>