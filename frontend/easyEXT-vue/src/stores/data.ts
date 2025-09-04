// store/data.ts
import { defineStore } from 'pinia'
import axios, { AxiosError } from 'axios'
import  { fetchCategories } from '@/api/api'
import type { Category, CategoryItem} from '@/api/types'
// 定义后端返回数据的类型（你可以根据实际接口补充字段）
interface Info {
  id: number
  name: string
  [key: string]: any
}

export const useDataStore = defineStore('data', {
  state: () => ({
    info: null as Category[] | null,     // 后端返回的数据
    cur_index: null as number | null,                   // 当前选中的索引
    length:   0,                      // 数据长度
    loaded: false,                 // 是否已经加载
    loading: false,                // 是否正在加载
    error: null as AxiosError | null // 错误信息
  }),
  actions: {
    async fetchData(force = false): Promise<Category[] | null> {
      // 已经加载过并且不强制刷新，就直接返回
      if (this.loaded && !force) return this.info

      // 避免并发重复请求
      if (this.loading) return this.info

      this.loading = true
      this.error = null
      try {
        const res = await fetchCategories()
        // const res = await axios.get<Info>('/api/data')
        this.info = res
        this.loaded = true
        this.cur_index = 0
        this.length = this.info.length
      } catch (err) {
        this.error = err as AxiosError
        console.error('数据获取失败:', err)
      } finally {
        this.loading = false
      }
      return this.info
    }
  }
})
