// src/api/http.ts
import axios from 'axios';
import type { InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// 类型定义
export interface Scene {
  id: string;
  name: string;
  description?: string;
  createdAt?: string;
}

export interface SceneCategory {
  id: string;
  name: string;
  scenes: Scene[];
}

// 定义基础类型
interface ApiResponse<T = any> {
  code: number;
  data: T;
  message?: string;
}

// 创建实例
const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE,
  timeout: 10000,
});

// 请求拦截
http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (!config.headers) {
    config.headers = {};
  }
  config.headers.Authorization = `Bearer ${localStorage.getItem('token') || ''}`;
  return config;
});

// 响应拦截
http.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    if (response.data.code !== 200) {
      return Promise.reject(response.data.message);
    }
    return response.data.data; // 直接返回业务数据
  },
  (error: any) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 封装GET请求（带TS泛型）
export async function getScenes<T = any>(): Promise<T> {
  return http.get<T>('/query/scenes');
}