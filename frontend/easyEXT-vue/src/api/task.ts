// 任务类型
export interface Task {
  id: number
  title: string
  completed: boolean
  createdAt: string
}

// 分页参数
export interface PaginationParams {
  page: number
  size: number
}

// 任务筛选条件
export interface TaskFilter extends Partial<PaginationParams> {
  status?: 'pending' | 'completed'
}