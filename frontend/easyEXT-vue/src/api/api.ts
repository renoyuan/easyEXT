// api.ts
import axios from 'axios'
import type { Category, CategoryItem, Task } from '@/api/types'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 替换为实际 API 地址
  timeout: 10000,
})

// 定义转换函数（类型安全）
const mapBackendToCategory = (backendData: any): Category[] => {
  if (!backendData?.data?.scenes) return [] // 容错处理

  return backendData.data.scenes.map((scene: any) => ({
    id: scene.id.toString(), // 确保 ID 为字符串
    name: scene.category, // 重命名 category → name
    items: scene.scenarios.map((scenario: any) => ({
      id: scenario.id.toString(),
      name: scenario.scene_label, // 重命名 scene_label → name
    })),
  }))
}

// 任务转换函数（类型安全）
const mapBackendToTasks = (backendData: any): Task[] => {
  if (!backendData?.data?.page_info) return [] // 容错处理

  return backendData.data.page_info.map((task: any) => ({
    id: task.id,
    sceneId: task.scene_id,
    taskStatus: task.task_status,
    createdTime: task.created_time,
    updateTime: task.updated_time,
    sceneName: task.scene_name, // 新增 sceneName 字段
  }))
}


// 获取分类数据接口
export const fetchCategories = async (): Promise<Category[]> => {
  try {
    const response = await api.get('/api/v1/query/scenes')
    return mapBackendToCategory(response.data) // 确保后端返回数据结构与 Category[] 一致
  } catch (error) {
    throw new Error('获取分类数据失败')
  }
}


// 获取任务列表
export const fetchTasks = async (): Promise<Task[]> => {
  try {
    const response = await api.get('/api/v1/query/tasks')
    console.debug(response.data)
    return mapBackendToTasks(response.data) 
  } catch (error) {
    console.error(error)
    throw new Error('获取任务数据失败')
    
  }
}

// 获取任务详情
export const fetchDetail = async (taskId: number | string): Promise<any> => {
  try {
    console.debug("获取任务详情 taskId",taskId)
    const response = await api.get('/api/v1/query/task_info', 
      {
          params: {
            task_id: taskId
          }},
        )

    console.debug(response.data)
    return response.data
  } catch (error) {
    console.error(error)
    throw new Error('获取任务详情失败')
    
  }
}
